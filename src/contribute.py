"""One-target, development-only starter task for short contributor sessions."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import argparse,json,pathlib,time
import numpy as np
from threadpoolctl import threadpool_limits
from benchmark import load
from models import rule_select,splits,lineage
from trial import fit_pair
from core import assert_disjoint,dumps,metrics,predict,sha256
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(target,out):
    start=time.time();cfg,primary,dev,_=load(); protocol=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())
    if target not in cfg['targets']:raise ValueError('Choose a preregistered target')
    f=dev[dev['y:'+target].notna()].reset_index(drop=True);y=f['y:'+target].to_numpy(float);folds=[]
    for fold,(a,b) in enumerate(splits(f,cfg['outer_folds'],cfg['outer_seeds'][0])):
        tr=f.iloc[a];te=f.iloc[b];assert_disjoint(tr,te)
        rules,_,_=rule_select(tr,y[a],cfg); models={k:rules[k] for k in ['rule_all']}
        for family in ['biology_pair','blind_pair']:models[family]=fit_pair(tr,y[a],target,family,cfg,protocol)
        base=lineage(tr,y[a],cfg);ref=predict(base,te)
        folds.append({'fold':fold,'train_groups':sorted(tr.group),'test_ids':te.model_id.tolist(),
            'models':models,'reference':base,'metrics':{name:metrics(y[b],predict(m,te),ref) for name,m in models.items()}})
    package={'target':target,'partition':'development only','seed':cfg['outer_seeds'][0],
        'input_sha256':sha256(ROOT/'data/panel/primary.csv'),'folds':folds,'elapsed_seconds':time.time()-start,
        'claim':'Exploratory development evidence only; requires independent fresh-cohort confirmation.'}
    out=ROOT/out;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise ValueError('Refusing to overwrite a contribution')
    out.write_text(dumps(package));print('Wrote',out,'in',round(time.time()-start,2),'seconds')
    for family in ['rule_all','biology_pair','blind_pair']:
        scores=[row['metrics'][family]['skill'] for row in folds]
        print(family,'mean fold skill vs lineage:',round(float(np.mean(scores)),4),'positive folds:',sum(s>0 for s in scores),'/ 5')

def verify(path):
    cfg,primary,dev,_=load();d=json.loads((ROOT/path).read_text());assert d['partition']=='development only'
    assert d['input_sha256']==sha256(ROOT/'data/panel/primary.csv')
    target=d['target'];seen=[]
    for row in d['folds']:
        tr=dev[dev.group.isin(row['train_groups'])];te=dev.set_index('model_id').loc[row['test_ids']].reset_index()
        assert_disjoint(tr,te);seen+=row['test_ids'];y=te['y:'+target]
        for name,m in row['models'].items():
            actual=metrics(y,predict(m,te),predict(row['reference'],te));stored=row['metrics'][name]
            for k,v in actual.items():
                if v is None:assert stored[k] is None
                else:np.testing.assert_allclose(v,stored[k],rtol=1e-8,atol=1e-9)
    assert len(seen)==len(set(seen)) and set(seen)==set(dev.loc[dev['y:'+target].notna(),'model_id'])
    print('PASS: every eligible development model predicted exactly once; fold separation and all 15 scores verified.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['run','verify']);p.add_argument('--target',default='SMARCA2');p.add_argument('--artifact',default='research/starter/RESULT.json')
    a=p.parse_args()
    with threadpool_limits(limits=1): (run(a.target,a.artifact) if a.action=='run' else verify(a.artifact))
