import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import pathlib,sys,time,json
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from benchmark import load
from models import rule_grid,rule_bank,preprocess
cfg,primary,dev,test=load(); train=dev.iloc[:500]; held=dev.iloc[500:]; grid=rule_grid(train,cfg)
# Synthetic responses: benchmark engineering, no biological association inspected.
y=np.random.default_rng(7).normal(size=len(train))
features=list(dict.fromkeys(f for f,q in grid)); x,med=preprocess(train,features); ids=np.array([features.index(f) for f,q in grid])
start=time.process_time()
for _ in range(20):
 slow=np.array([.5 if q is None else np.quantile(x[:,i],q) for i,(f,q) in zip(ids,grid)])
slow_time=time.process_time()-start
start=time.process_time()
for _ in range(20):
 quantiles=np.quantile(x,cfg['rule_quantiles'],axis=0)
 fast=np.array([.5 if q is None else quantiles[cfg['rule_quantiles'].index(q),i] for i,(f,q) in zip(ids,grid)])
fast_time=time.process_time()-start
np.testing.assert_array_equal(slow,fast)
print(json.dumps({'slow_cpu_seconds':slow_time,'vectorized_cpu_seconds':fast_time,'speedup_threshold_calculation':slow_time/fast_time,'thresholds_exactly_equal':True,'loops':20}))
