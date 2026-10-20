import json,pathlib,sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from models import rule_select,lineage
from core import metrics,predict
from trial import pair_features,fit_pair
ROOT=pathlib.Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/benchmark.json').read_text())
PROTOCOL=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())

def test_lineage_only_signal_survives_lineage_permutation_null():
    n=240; labels=np.repeat(['A','B'],n//2); x=np.repeat([0.,1.],n//2)
    f=pd.DataFrame({'group':[str(i) for i in range(n)],'lineage':labels,'expr:X':x})
    y=-x
    rules,_,observed=rule_select(f,y,CFG)
    assert metrics(y,predict(rules['rule_all'],f))['r2']>.99
    # A globally predictive lineage proxy must not become a significant within-lineage hit.
    rng=np.random.default_rng(17)
    null=[]
    for _ in range(9):
        yp=y.copy()
        for l in ['A','B']:
            ix=np.flatnonzero(labels==l); yp[ix]=rng.permutation(y[ix])
        null.append(rule_select(f,yp,CFG)[2])
    assert (1+sum(v>=observed for v in null))/(1+len(null))==1.

def test_trial_blind_selection_uses_only_passed_training_data():
    rng=np.random.default_rng(11); n=180; a=rng.normal(size=n); b=rng.normal(size=n)
    f=pd.DataFrame({'group':[str(i) for i in range(n)],'lineage':['A']*n,
                    'expr:A':a,'expr:B':b,'expr:C':rng.normal(size=n)})
    first=pair_features(f,a,'unused','blind_pair',PROTOCOL)
    assert first[0]=='expr:A'
    other=pair_features(f,b,'unused','blind_pair',PROTOCOL)
    assert other[0]=='expr:B'
    model=fit_pair(f,a,'unused','blind_pair',CFG,PROTOCOL)
    assert model['complexity']['molecular_features']<=2
    assert metrics(a,predict(model,f))['r2']>.95

def test_cached_permutations_repeat_complete_selection_exactly():
    from models import permutation_statistics
    rng=np.random.default_rng(19); n=240
    f=pd.DataFrame({'group':[str(i) for i in range(n)],'lineage':np.repeat(['A','B','C'],80),
                    'expr:A':rng.normal(size=n),'cn:B':rng.normal(size=n),'damaging:C':rng.binomial(1,.3,n)})
    f.loc[::7,'expr:A']=np.nan
    y=rng.normal(size=n)+np.repeat([0,.2,.5],80)
    fast=permutation_statistics(f,y,CFG,23,9)
    rng=np.random.default_rng(23); slow=[]
    for _ in range(9):
        yp=y.copy()
        for l in sorted(f.lineage.unique()):
            ix=np.flatnonzero(f.lineage.to_numpy()==l);yp[ix]=rng.permutation(y[ix])
        slow.append(rule_select(f,yp,CFG)[2])
    np.testing.assert_allclose(fast,slow,rtol=1e-12,atol=1e-12)
