import json,pathlib,sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from models import rule_select, splits, linear_fit
from core import predict
CFG=json.loads((pathlib.Path(__file__).resolve().parents[1]/'config/benchmark.json').read_text())

def test_signal_and_null_features():
    n=240; x=np.linspace(-3,3,n); rng=np.random.default_rng(15)
    f=pd.DataFrame({'group':[str(i) for i in range(n)],'lineage':['A','B']*(n//2),'expr:X':x,'expr:noise':rng.normal(size=n)})
    y=np.where(x>0,-1.,0.)
    m,details,_=rule_select(f,y,CFG)
    assert m['rule_all']['features']==['expr:X']
    assert np.mean((predict(m['rule_all'],f)-y)**2)<.08
    assert len(details)==8

def test_groups_never_cross():
    f=pd.DataFrame({'group':np.repeat(np.arange(60),2)})
    for a,b in splits(f,5,2): assert not set(f.iloc[a].group)&set(f.iloc[b].group)

def test_training_imputation_independent_of_test():
    f=pd.DataFrame({'expr:X':[1.,2.,np.nan,4.]}); y=np.array([1.,2.,2.,4.])
    model=linear_fit(f,y,['expr:X'],'ridge',1)
    assert model['medians']==[2.]
    held=pd.DataFrame({'expr:X':[np.nan,100000.]})
    assert predict(model,held)[0]==predict(model,held.iloc[:1])[0]
