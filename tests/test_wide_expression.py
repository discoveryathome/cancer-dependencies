"""Scientific controls for broader-feature selection and evidence isolation."""
import builtins
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

import wide_expression as wide
import research_program as program


def test_training_screen_finds_signal_outside_original_panel():
    rng=np.random.default_rng(80);x=rng.normal(size=(200,340));genes=[str(i+1) for i in range(340)]
    y=4*x[:,339]+rng.normal(scale=.1,size=200)
    a=wide.fit_once(x[:140],y[:140],genes,'wide300',list(range(30)),1)
    b=wide.fit_once(x[:140],y[:140],genes,'panel30',list(range(30)),1)
    assert '340' in a['features'] and '340' not in b['features']
    assert np.mean((wide.predict(a,x[140:],genes)-y[140:])**2)<np.mean((wide.predict(b,x[140:],genes)-y[140:])**2)
    assert len(a['features'])==300 and len(b['features'])==30


def test_preprocessing_uses_training_missingness_and_variance_only():
    x=np.tile(np.arange(100.)[:,None],(1,35));y=np.arange(100.);genes=[str(i) for i in range(35)]
    x[:11,30]=np.nan; x[:,31]=4; x[:5,32]=np.nan
    indices,median,center,scale=wide.select_features(x,y,genes,'wide300',list(range(30)),top=33)
    assert 30 not in indices and 31 not in indices and 32 in indices
    k=list(indices).index(32); assert median[k]==pytest.approx(52)
    # Extreme held-out data and missing values cannot update fitted medians/scales.
    selection=(indices,median.copy(),center.copy(),scale.copy())
    held=np.full((2,35),1e9);held[0]=np.nan
    out=wide.transform(held,selection)
    assert np.isfinite(out).all() and np.array_equal(selection[1],median)
    with pytest.raises(ValueError,match='Too few'):wide.select_features(x,y,genes,'wide300',[],top=34)


def test_matrix_duplicate_ids_and_missing_models_fail_closed(tmp_path):
    p=tmp_path/'expr.csv';p.write_text(',A (1),B (2)\nM1,1,2\nM1,3,4\n')
    with pytest.raises(ValueError,match='duplicate matrix'):wide.read_rows(p,['M1'],['1'])
    p.write_text(',A (1),B (2)\nM1,1,2\n')
    with pytest.raises(ValueError,match='Missing requested'):wide.read_rows(p,['M2'],['1'])
    p.write_text(',A (1),B (1)\nM1,1,2\n')
    with pytest.raises(ValueError,match='Duplicate Entrez'):wide.headers(p)


def test_nested_feature_selection_never_receives_inner_validation_rows(monkeypatch):
    rng=np.random.default_rng(81);x=rng.normal(size=(90,320));y=rng.normal(size=90)
    frame=pd.DataFrame({'model_id':[f'M{i}' for i in range(90)],'group':[f'P{i}' for i in range(90)]})
    expected=[(x[a],y[a]) for a,b in wide.splits(frame,3,817)]+[(x,y)]
    actual=wide.select_features;calls=[]
    def check(xx,yy,*args,**kwargs):
        ex,ey=expected[len(calls)];assert np.array_equal(xx,ex) and np.array_equal(yy,ey);calls.append(len(xx));return actual(xx,yy,*args,**kwargs)
    monkeypatch.setattr(wide,'select_features',check)
    wide.fit_nested(frame,x,y,[str(i+1) for i in range(320)],'wide300',list(range(30)),{'inner_folds':3,'inner_seed':817,'alphas':[1,10]})
    assert calls==[60,60,60,90]


def test_training_input_loader_never_opens_external_outcomes(monkeypatch):
    if not wide.OLD.exists() or not wide.NEW.exists():pytest.skip('Optional pinned raw matrices absent')
    original,path_open=builtins.open,Path.open
    def guard(path):
        if isinstance(path,(str,Path)):
            text=str(path).lower()
            assert 'screen_gene_effect.csv' not in text and 'sanger' not in text
            assert 'data/panel/' not in text and not text.endswith('/results.json')
    def a(path,*args,**kwargs):guard(path);return original(path,*args,**kwargs)
    def b(path,*args,**kwargs):guard(path);return path_open(path,*args,**kwargs)
    monkeypatch.setattr(builtins,'open',a);monkeypatch.setattr(Path,'open',b)
    frame,x,genes,panel,*_=wide.inputs()
    assert len(frame)==773 and x.shape==(773,len(genes)) and len(genes)>300 and len(panel)==30


def test_program_rejects_undeclared_task_and_routes_both_tracks():
    with pytest.raises(ValueError,match='Missing declaration'):program.proposal({'track':'exploration'})
    catalog={'tracks':[{'id':'comparable-improvements','weight':50,'tasks':[{'id':'a'}]}, {'id':'exploration','weight':50,'tasks':[{'id':'b'}]}]}
    assert program.choose(catalog,'0'*32)['task']['id']=='a'
    assert program.choose(catalog,format(50,'032x'))['task']['id']=='b'
