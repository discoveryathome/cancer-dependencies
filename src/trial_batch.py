"""Development-only batch transfer for the two fixed contributor-trial families."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import json,pathlib
import pandas as pd
from threadpoolctl import threadpool_limits
from benchmark import load
from core import metrics,predict,assert_disjoint
from models import lineage
from trial import fit_pair
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    cfg,primary,dev,test=load();protocol=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())
    bm=pd.read_csv(ROOT/'data/batch-metadata.csv');bm=bm[bm.library=='Avana'][['model_id','batches']]
    f=dev.merge(bm,on='model_id',how='left',validate='one_to_one');f['batches']=f.batches.fillna('unknown')
    labels=sorted({x for s in f.batches for x in s.split(';') if x!='unknown'});rows=[]
    for batch in labels:
        tr=f[~f.batches.str.split(';').apply(lambda v:batch in v)];te=f[f.batches==batch]
        if len(tr)<200 or len(te)<30:continue
        assert_disjoint(tr,te)
        for target in cfg['targets']:
            train=tr[tr['y:'+target].notna()];test=te[te['y:'+target].notna()]
            if len(test)<30:continue
            y=train['y:'+target].to_numpy(float);ref=predict(lineage(train,y,cfg),test)
            for family in ['biology_pair','blind_pair']:
                model=fit_pair(train,y,target,family,cfg,protocol)
                rows.append({'target':target,'batch':batch,'family':family,**metrics(test['y:'+target],predict(model,test),ref)})
        print('TRIAL BATCH',batch,flush=True)
    pd.DataFrame(rows).to_csv(ROOT/'reports/trial_batch_holdouts.csv',index=False,float_format='%.12g')
if __name__=='__main__':
    with threadpool_limits(limits=1):main()
