"""Recompute statistical summaries; optionally rerun the selection-aware nulls."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import argparse,json,pathlib
import numpy as np
import pandas as pd
from core import assert_disjoint,bh,bootstrap,metrics,predict
from models import permutation_statistics
from benchmark import load
from threadpoolctl import threadpool_limits
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main(rerun_nulls):
    cfg,primary,dev,test=load(); base=ROOT/'research/initial'
    package=json.loads((base/'VERIFY.json').read_text()); final=pd.read_csv(base/'final_metrics.csv')
    nulls=json.loads((base/'permutations.json').read_text()); pvalues=[]
    for t in cfg['targets']:
        r=nulls[t]; p=(1+sum(v>=r['statistic'] for v in r['null_statistics']))/(1+len(r['null_statistics']))
        np.testing.assert_allclose(r['p'],p,atol=1e-14);pvalues.append(p)
        if rerun_nulls:
            f=dev[dev['y:'+t].notna()].reset_index(drop=True)
            actual=permutation_statistics(f,f['y:'+t].to_numpy(float),cfg,r['seed'],cfg['permutation_replicates'])
            np.testing.assert_allclose(actual,r['null_statistics'],rtol=1e-10,atol=1e-12)
            print('NULL REPLAY',t,flush=True)
    for t,q in zip(cfg['targets'],bh(pvalues)):np.testing.assert_allclose(q,nulls[t]['bh_q'],atol=1e-14)
    for r in package['results']:
        te=test.set_index('model_id').loc[r['model_ids']].reset_index(); y=te['y:'+r['target']].to_numpy()
        ci=bootstrap(y,predict(r['model'],te),predict(r['reference'],te),te.group,
                     cfg['split_seed']+cfg['targets'].index(r['target']),cfg['bootstrap_replicates'])
        stored=final[(final.target==r['target'])&(final.model==r['name'])].iloc[0]
        np.testing.assert_allclose(ci,[stored.skill_ci_low,stored.skill_ci_high],atol=1e-9,rtol=1e-8)
    for sub in ['initial','contributor-trial']:
        folder=ROOT/'research'/sub; outer=pd.read_csv(folder/'outer_predictions.csv'); scores=pd.read_csv(folder/'outer_metrics.csv')
        refcol='lineage_prediction' if sub=='initial' else 'rule_prediction'
        for (t,seed,model),part in outer.groupby(['target','seed','model']):
            eligible=set(dev.loc[dev['y:'+t].notna(),'model_id'])
            assert set(part.model_id)==eligible and not part.model_id.duplicated().any()
        for (t,seed,fold,model),part in outer.groupby(['target','seed','fold','model']):
            yy=dev.set_index('model_id').loc[part.model_id,'y:'+t].to_numpy()
            np.testing.assert_allclose(yy,part.observed,atol=1e-10,rtol=1e-9)
            row=scores[(scores.target==t)&(scores.seed==seed)&(scores.fold==fold)&(scores.model==model)].iloc[0]
            actual=metrics(yy,part.predicted,part[refcol])
            for k,v in actual.items():
                if v is None: assert pd.isna(row[k])
                else: np.testing.assert_allclose(v,row[k],atol=1e-9,rtol=1e-8)
    rules=json.loads((base/'outer_rules.json').read_text()); outer=pd.read_csv(base/'outer_predictions.csv')
    for r in rules:
        tr=dev[dev.group.isin(r['train_groups'])];te=dev[dev.group.isin(r['test_groups'])];assert_disjoint(tr,te)
        part=outer[(outer.target==r['target'])&(outer.seed==r['seed'])&(outer.fold==r['fold'])&(outer.model=='rule_all')]
        te=te.set_index('model_id').loc[part.model_id].reset_index()
        np.testing.assert_allclose(predict(r['rule'],te),part.predicted,atol=1e-9,rtol=1e-8)
    decisions=json.loads((base/'decisions.json').read_text())
    om=pd.read_csv(base/'outer_metrics.csv'); lm=pd.read_csv(base/'lineage_metrics.csv')
    for d in decisions:
        t=d['target'];row=final[(final.target==t)&(final.model=='rule_all')].iloc[0]
        o=om[(om.target==t)&(om.model=='rule_all')];l=lm[(lm.target==t)&(lm.model=='rule_all')]
        flags={'test_skill':bool(row.skill>=cfg['min_final_skill_vs_lineage']),
          'ci_positive':bool(row.skill_ci_low>0),'permutation_q':bool(nulls[t]['bh_q']<=cfg['max_bh_q']),
          'outer_stability':bool((o.skill>0).mean()>=cfg['min_outer_positive_fraction']),
          'lineage_transfer':bool(len(l)>0 and (l.skill>0).mean()>=cfg['min_lineage_positive_fraction'])}
        assert flags==d['gates'] and all(flags.values())==d['passes_pilot_gate']
    print('PASS: cohort completeness, outer metrics/rule predictions, paired CIs, selection-null p-values, BH correction and all decision gates recomputed.')
    print('Null selections rerun:',rerun_nulls,'; full lineage fitting replay remains in the full benchmark command.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nulls',action='store_true');a=p.parse_args()
    with threadpool_limits(limits=1):main(a.nulls)
