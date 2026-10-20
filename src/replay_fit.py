"""Refit every full-development model in a fresh process, without outer-CV replay."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']: os.environ[k]='1'
import json,pathlib,time
import numpy as np
from threadpoolctl import threadpool_limits
from benchmark import load,inputs
from core import predict
from models import fit_models
from trial import fit_pair
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    start=time.time(); cfg,primary,dev,test=load()
    base=json.loads((ROOT/'research/initial/frozen.json').read_text())
    trial=json.loads((ROOT/'research/contributor-trial/frozen.json').read_text())
    protocol=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())
    assert inputs()==base['inputs']==trial['inputs']
    checked=0
    for target in cfg['targets']:
        f=dev[dev['y:'+target].notna()].reset_index(drop=True); y=f['y:'+target].to_numpy(float)
        models,search=fit_models(f,y,target,cfg)
        for name,m in models.items():
            old=base['models'][target][name]
            assert m.get('features')==old.get('features'),(target,name)
            np.testing.assert_allclose(predict(m,test),predict(old,test),rtol=1e-7,atol=1e-8)
            checked+=1
        for family in ['biology_pair','blind_pair']:
            m=fit_pair(f,y,target,family,cfg,protocol); old=trial['models'][target][family]
            assert m['features']==old['features'],(target,family)
            np.testing.assert_allclose(predict(m,test),predict(old,test),rtol=1e-7,atol=1e-8)
            checked+=1
        print('REFIT VERIFIED',target,flush=True)
    print('PASS:',checked,'models reselected and refitted; seconds',round(time.time()-start,2))
if __name__=='__main__':
    with threadpool_limits(limits=1): main()
