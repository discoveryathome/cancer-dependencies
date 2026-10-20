"""Assay-batch metadata extraction and development-only batch-holdout sensitivity."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import argparse,json,pathlib
import numpy as np
import pandas as pd
from core import dumps,metrics,predict,sha256,assert_disjoint
from models import rule_select,lineage
from benchmark import load
from threadpoolctl import threadpool_limits
ROOT=pathlib.Path(__file__).resolve().parents[1]

def prepare():
    lock=json.loads((ROOT/'data/source-lock.json').read_text())
    for name in ['ScreenSequenceMap.csv','AchillesSequenceQCReport.csv','AchillesScreenQCReport.csv']:
        row=next(r for r in lock['files'] if r['name']==name)
        assert sha256(ROOT/'data/raw'/name)==row['sha256']
    s=pd.read_csv(ROOT/'data/raw/ScreenSequenceMap.csv');q=pd.read_csv(ROOT/'data/raw/AchillesSequenceQCReport.csv')
    screens=pd.read_csv(ROOT/'data/raw/AchillesScreenQCReport.csv')
    valid=set(screens.loc[(screens.PassesQC==True)&(screens.CanInclude==True)&(screens.ScreenType=='2DS'),'ScreenID'])
    valid_seq=set(q.loc[(q.PassesQC==True)&(q.CanInclude==True),'SequenceID'])
    s=s[s.ScreenID.isin(valid)&s.SequenceID.isin(valid_seq)&(s.PassesQC==True)]
    rows=[]
    for (mid,lib),part in s.groupby(['ModelID','Library']):
        rows.append({'model_id':mid,'library':lib,'batches':';'.join(sorted(part.pDNABatch.dropna().unique())),
                     'n_sequences':len(part),'n_screens':part.ScreenID.nunique()})
    pd.DataFrame(rows).to_csv(ROOT/'data/batch-metadata.csv',index=False)
    print('Wrote',len(rows),'model/library batch assignments.')

def evaluate():
    cfg,primary,dev,test=load();bm=pd.read_csv(ROOT/'data/batch-metadata.csv')
    bm=bm[bm.library=='Avana'][['model_id','batches']]
    f=dev.merge(bm,on='model_id',how='left',validate='one_to_one'); f['batches']=f.batches.fillna('unknown')
    labels=sorted({x for s in f.batches for x in s.split(';') if x!='unknown'})
    rows=[]
    for batch in labels:
        tr=f[~f.batches.str.split(';').apply(lambda v:batch in v)]
        te=f[f.batches==batch]
        if len(tr)<200 or len(te)<30:continue
        assert_disjoint(tr,te)
        for target in cfg['targets']:
            train=tr[tr['y:'+target].notna()]; test=te[te['y:'+target].notna()]
            if len(test)<30 or len(train)<200: continue
            rules,_,_=rule_select(train,train['y:'+target].to_numpy(float),cfg)
            ref=predict(lineage(train,train['y:'+target].to_numpy(float),cfg),test)
            rows.append({'batch':batch,'target':target,'n_train':len(train),
                'feature':rules['rule_all'].get('features',[None])[0],
                **metrics(test['y:'+target],predict(rules['rule_all'],test),ref)})
        print('BATCH CHECK',batch,len(tr),len(te),flush=True)
    pd.DataFrame(rows).to_csv(ROOT/'reports/batch_holdouts.csv',index=False,float_format='%.12g')
    (ROOT/'reports/batch_metadata_audit.json').write_text(dumps({'development_batch_counts':f.batches.value_counts().to_dict(),
        'n_missing_batch':int((f.batches=='unknown').sum()),'n_checks':len(rows),
        'design':'Development-only. Test models exposed to exactly one pDNA batch; remove all training models exposed to that batch. Reselect rule inside remaining training data.',
        'limitations':'pDNA batch is one assay-batch proxy. Shared upstream score estimation remains; no causal adjustment for all technical differences. Results are descriptive sensitivity checks.'}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','evaluate']);a=p.parse_args()
    with threadpool_limits(limits=1):(prepare if a.phase=='prepare' else evaluate)()
