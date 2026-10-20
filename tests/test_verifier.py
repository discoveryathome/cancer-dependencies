import copy, json, pathlib, sys
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from core import bh, metrics, predict, sha256
from verify import verify

def fixture(tmp_path):
    f=pd.DataFrame({'model_id':['a','b','c','d'],'group':['a','b','c','d'],
       'partition':['development','development','final','final'], 'lineage':['l']*4,
       'expr:X':[0,2,0,2], 'y:T':[0,-1,0,-1]})
    f.to_csv(tmp_path/'f.csv',index=False)
    model={'kind':'rule','features':['expr:X'],'medians':[1], 'threshold':1,'left':0,'right':-1}
    row={'target':'T','model_ids':['c','d'],'model':model,'reference':{'kind':'constant','value':-.5},
         'predictions':[0,-1],'metrics':metrics([0,-1],[0,-1],[-.5,-.5])}
    d={'inputs':{'f.csv':sha256(tmp_path/'f.csv')},'frame':'f.csv','training_groups':['a','b'],
       'test_groups':['c','d'],'results':[row]}
    return f,d

def run(tmp_path,d):
    p=tmp_path/'v.json'; p.write_text(json.dumps(d)); return verify(p,tmp_path)

def test_worked_certificate(tmp_path):
    _,d=fixture(tmp_path); assert run(tmp_path,d)==1

@pytest.mark.parametrize('fault',['score','prediction','hash','overlap','incomplete','target_feature'])
def test_reject_wrong_candidate(tmp_path,fault):
    f,d=fixture(tmp_path)
    if fault=='score': d['results'][0]['metrics']['mse']=.3
    if fault=='prediction': d['results'][0]['predictions'][0]=.4
    if fault=='hash': d['inputs']['f.csv']='0'*64
    if fault=='overlap':
        f.loc[2,'group']='a'; f.to_csv(tmp_path/'f.csv',index=False); d['inputs']['f.csv']=sha256(tmp_path/'f.csv')
    if fault=='incomplete': d['results'][0]['model_ids']=['c']
    if fault=='target_feature': d['results'][0]['model']['features']=['y:T']
    with pytest.raises((ValueError,AssertionError)): run(tmp_path,d)

def test_bh():
    np.testing.assert_allclose(bh([.01,.04,.03]),[.03,.04,.04])
