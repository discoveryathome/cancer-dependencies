"""Controls for offset recovery, leakage, missingness and invariant rankings."""
import builtins
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

import expression_bridge as bridge
import bridge_sensitivity as sensitivity


def synthetic():
    rng=np.random.default_rng(4); genes=['G'+str(i) for i in range(30)]
    old=pd.DataFrame({'model_id':['M'+str(i) for i in range(150)],
                      'group':['P'+str(i) for i in range(150)],'lineage':['A']*150})
    for g in genes: old['expr:'+g]=rng.uniform(2,8,len(old))
    new=old.copy()
    for j,g in enumerate(genes): new['expr:'+g]+= .25 + j/20
    rules={'T':{'kind':'rule','features':['expr:G0'],'threshold':5}}
    return old,new,genes,rules


def test_recovers_offsets_out_of_fold_and_ignores_outcomes():
    old,new,genes,rules=synthetic()
    r=bridge.paired_audit(old,new,genes,rules)
    assert r['offset_validation']['numerical_gate_passed']
    assert r['offset_validation']['relative_reduction']==pytest.approx(1)
    assert r['offset_validation']['features_improved']==30
    old['y:T']=np.arange(150); new['y:T']=-np.arange(150)
    assert bridge.paired_audit(old,new,genes,rules)==r
    # Alter only a held-out fold: its estimated offsets cannot change.
    fold_ids={i for i,f in r['offset_validation']['folds'].items() if f==0}
    new.loc[new.model_id.isin(fold_ids),'expr:G0']+=10
    changed=bridge.paired_audit(old,new,genes,rules)
    assert changed['offset_validation']['fold_offsets']['0']==r['offset_validation']['fold_offsets']['0']


def test_missing_pairs_explicit_and_invalid_identity_rejected():
    old,new,genes,rules=synthetic(); new.loc[0,'expr:G0']=np.nan
    r=bridge.paired_audit(old,new,genes,rules)
    assert r['complete_n']==149 and r['incomplete_ids']==['M0']
    assert r['features']['G0']['paired_n']==149
    assert r['features']['G1']['paired_n']==150
    old.loc[1,'group']=old.loc[0,'group']
    with pytest.raises(ValueError,match='Duplicate development'): bridge.paired_audit(old,new,genes,rules)
    old,new,genes,rules=synthetic(); new=new.iloc[::-1]
    with pytest.raises(ValueError,match='Unaligned'): bridge.paired_audit(old,new,genes,rules)


def test_zero_shift_not_spurious_improvement_and_full_reference_iqr_used():
    old,new,genes,rules=synthetic()
    r=bridge.paired_audit(old,old.copy(),genes,rules)
    assert r['offset_validation']['numerical_gate_passed'] is False
    assert r['offset_validation']['relative_reduction'] is None
    r=bridge.paired_audit(old,new,genes,rules,{g:10. for g in genes})
    assert r['features']['G0']['oof']['before_scaled_mae']==pytest.approx(.025)


def test_real_prediction_stage_never_opens_outcomes(monkeypatch):
    inputs=bridge.ROOT/'data/raw/robustness-20261021'
    if not (inputs/'traditional_expression.csv').exists(): pytest.skip('Local publisher matrix unavailable')
    ordinary,path_open=builtins.open,Path.open
    def guard(path):
        if isinstance(path,(str,Path)):
            p=str(path).lower()
            assert 'screen_gene_effect.csv' not in p
            assert 'sanger' not in p and 'data/panel/' not in p
            assert not p.endswith('/results.json')
    def a(path,*args,**kwargs): guard(path); return ordinary(path,*args,**kwargs)
    def b(path,*args,**kwargs): guard(path); return path_open(path,*args,**kwargs)
    monkeypatch.setattr(builtins,'open',a); monkeypatch.setattr(Path,'open',b)
    frozen,base,corrected,source=sensitivity.prediction_data(bridge.ROOT/'data/raw/transfer-trial-20261021')
    assert len(corrected['rows'])==77 and len(corrected['predictions'])==12
    for target,row in corrected['rank_invariance'].items():
        assert len(row)==3 and all(x['ranks_identical'] for x in row.values())
    # A nonuniform offset would not preserve linear pair rankings in general;
    # for this frozen complete-input case the analytical intercept shift matches.
    for target, row in frozen['targets'].items():
        for family in ['compact_expression_pair','strong_expression','self_expression']:
            m=row['models'][family]
            offset=np.array([corrected['offsets'][f.split(':')[1]] for f in m['features']])
            expected=-np.dot(offset/np.array(m['scale']),np.array(m['coef']))
            assert corrected['rank_invariance'][target][family]['prediction_shift']==pytest.approx(expected,abs=1e-12)
