"""Two-stage benchmark: development freezes models; finalization never tunes them."""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ[name]='1'
import argparse, json, pathlib, time, platform, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from threadpoolctl import threadpool_limits
from core import assert_disjoint,bh,bootstrap,dumps,metrics,predict,sha256
from models import fit_models, rule_select, splits, lineage, permutation_statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]


def inputs():
    paths=['config/benchmark.json','config/PREREGISTRATION.md','data/panel/primary.csv','data/panel/sanger.csv',
           'data/source-lock.json','data/gene-map.json','data/model-metadata.csv','data/panel-lock.json',
           'requirements.lock','src/prepare.py','src/fetch_data.py','src/core.py','src/models.py','src/benchmark.py']
    return {p:sha256(ROOT/p) for p in paths}


def load():
    cfg=json.loads((ROOT/'config/benchmark.json').read_text())
    for p,h in json.loads((ROOT/'data/panel-lock.json').read_text()).items():
        if sha256(ROOT/p)!=h: raise ValueError('Panel hash mismatch')
    primary=pd.read_csv(ROOT/'data/panel/primary.csv')
    if primary.group.duplicated().any(): raise ValueError('Permutation units must be unique identities')
    dev=primary[primary.partition=='development'].reset_index(drop=True)
    final=primary[primary.partition=='final'].reset_index(drop=True)
    assert_disjoint(dev,final)
    return cfg,primary,dev,final


def develop(out):
    cfg,primary,dev,final=load(); start=time.time(); rows=[]; fold_rules=[]; predictions=[]; frozen={}; searches={}; nulls={}; loo=[]
    for ti,target in enumerate(cfg['targets']):
        f=dev[dev['y:'+target].notna()].reset_index(drop=True); y=f['y:'+target].to_numpy(float)
        if len(f)<200: raise ValueError('Insufficient development cohort')
        for seed in cfg['outer_seeds']:
            for fold,(a,b) in enumerate(splits(f,cfg['outer_folds'],seed)):
                tr=f.iloc[a]; te=f.iloc[b]; assert_disjoint(tr,te)
                models,search=fit_models(tr,y[a],target,cfg); ref=predict(models['lineage'],te)
                for name,model in models.items():
                    pred=predict(model,te)
                    rows.append({'target':target,'seed':seed,'fold':fold,'model':name,**metrics(y[b],pred,ref)})
                    for mid,true,hat,base in zip(te.model_id,y[b],pred,ref):
                        predictions.append({'target':target,'seed':seed,'fold':fold,'model':name,'model_id':mid,'observed':true,'predicted':hat,'lineage_prediction':base})
                fold_rules.append({'target':target,'seed':seed,'fold':fold,'rule':models['rule_all'],
                    'train_groups':sorted(tr.group),'test_groups':sorted(te.group)})
        # All development fitting and selection are completed before final outcomes are evaluated.
        frozen[target],searches[target]=fit_models(f,y,target,cfg)
        observed=searches[target]['observed_permutation_statistic']
        values=permutation_statistics(f,y,cfg,cfg['permutation_seed']+ti,cfg['permutation_replicates'])
        p=(1+sum(x>=observed for x in values))/(len(values)+1)
        nulls[target]={'statistic':observed,'null_statistics':values,'p':p,'n':len(f),'seed':cfg['permutation_seed']+ti}
        for label,n in f.lineage.value_counts().sort_index().items():
            if n<cfg['lineage_min_test'] or len(f)-n<cfg['lineage_min_train']: continue
            tr=f[f.lineage!=label]; te=f[f.lineage==label]; assert_disjoint(tr,te)
            models,search=fit_models(tr,tr['y:'+target].to_numpy(float),target,cfg)
            ref=predict(models['mean'],te)
            for name in ['rule_all','mean','lineage','self_expression','ridge_expr','ridge_all','elastic_expr','elastic_all']:
                pred=predict(models[name],te)
                loo.append({'target':target,'lineage':label,'model':name,**metrics(te['y:'+target],pred,ref),
                            'rule_feature':models[name].get('features',[None])[0] if name=='rule_all' else None})
        print('DEVELOPED',target,'n=',len(f),'rule=',frozen[target]['rule_all'].get('features'),'permutation p=',p,flush=True)
    q=bh([nulls[t]['p'] for t in cfg['targets']])
    for t,v in zip(cfg['targets'],q): nulls[t]['bh_q']=float(v)
    for name,data in [('outer_metrics',rows),('outer_predictions',predictions),('lineage_metrics',loo)]:
        pd.DataFrame(data).to_csv(out/(name+'.csv'),index=False,float_format='%.12g')
    (out/'outer_rules.json').write_text(dumps(fold_rules))
    (out/'search.json').write_text(dumps(searches))
    (out/'permutations.json').write_text(dumps(nulls))
    freeze={'version':cfg['version'],'inputs':inputs(),'models':frozen,
        'development_groups':sorted(dev.group),'final_groups':sorted(final.group),
        'phase':'development complete; final metrics not computed','python':sys.version,'platform':platform.platform(),
        'elapsed_seconds':time.time()-start}
    (out/'frozen.json').write_text(dumps(freeze))
    print('FROZEN',out/'frozen.json','seconds',round(time.time()-start,2),flush=True)


def finalize(out):
    cfg,primary,dev,test=load(); frozen=json.loads((out/'frozen.json').read_text())
    if inputs()!=frozen['inputs']: raise ValueError('Code, configuration or input changed after freeze')
    ext=pd.read_csv(ROOT/'data/panel/sanger.csv'); ext=ext[ext.partition=='external']
    assert_disjoint(primary,ext)
    rows=[]; results=[]; external=[]; audit=[]; decisions=[]
    nulls=json.loads((out/'permutations.json').read_text())
    outer=pd.read_csv(out/'outer_metrics.csv'); loo=pd.read_csv(out/'lineage_metrics.csv')
    for ti,target in enumerate(cfg['targets']):
        te=test[test['y:'+target].notna()].copy(); y=te['y:'+target].to_numpy(float)
        models=frozen['models'][target]; ref=predict(models['lineage'],te)
        for name,model in models.items():
            pred=predict(model,te); score=metrics(y,pred,ref)
            ci=bootstrap(y,pred,ref,te.group,cfg['split_seed']+ti,cfg['bootstrap_replicates'])
            row={'target':target,'model':name,**score,'skill_ci_low':ci[0],'skill_ci_high':ci[1],
                 'molecular_features':model['complexity']['molecular_features'],'parameters':model['complexity']['parameters']}
            rows.append(row)
            results.append({'target':target,'name':name,'model':model,'reference':models['lineage'],
                            'model_ids':te.model_id.tolist(),'predictions':pred.tolist(),'metrics':score})
            ex=ext[ext['y:'+target].notna()]
            if len(ex):
                external.append({'target':target,'model':name,**metrics(ex['y:'+target],predict(model,ex),predict(models['lineage'],ex))})
        model=models['rule_all']; pred=predict(model,te); residual=y-pred
        if model['kind']=='rule':
            x=te[model['features'][0]].fillna(model['medians'][0]); nleft=int((x<=model['threshold']).sum())
            support=[nleft,len(te)-nleft]
        else: support=[len(te),0]
        corr=spearmanr(residual,te.audit_screen_nnmd,nan_policy='omit').statistic
        for source,grp in te.groupby('expression_source'):
            ix=te.index.get_indexer(grp.index)
            audit.append({'target':target,'expression_source':source,'n':len(grp),'residual_mean':float(residual[ix].mean()),
                          'residual_mse':float(np.mean(residual[ix]**2)),
                          'screen_nnmd_residual_spearman':float(corr) if np.isfinite(corr) else None})
        a=outer[(outer.target==target)&(outer.model=='rule_all')]
        l=loo[(loo.target==target)&(loo.model=='rule_all')]
        final=next(r for r in rows if r['target']==target and r['model']=='rule_all')
        flags={'test_skill':final['skill']>=cfg['min_final_skill_vs_lineage'],
               'ci_positive':final['skill_ci_low']>0,'permutation_q':nulls[target]['bh_q']<=cfg['max_bh_q'],
               'outer_stability':float((a.skill>0).mean())>=cfg['min_outer_positive_fraction'],
               'lineage_transfer':len(l)>0 and float((l.skill>0).mean())>=cfg['min_lineage_positive_fraction']}
        decisions.append({'target':target,'rule':model,'final_support':support,
            'final_skill':final['skill'],'final_ci':[final['skill_ci_low'],final['skill_ci_high']],
            'permutation_p':nulls[target]['p'],'permutation_q':nulls[target]['bh_q'],
            'outer_positive_fraction':float((a.skill>0).mean()),'lineage_positive_fraction':float((l.skill>0).mean()) if len(l) else None,
            'eligible_lineages':len(l),'gates':flags,'passes_pilot_gate':all(flags.values()),
            'status':'computational research hypothesis; novelty and independent review unestablished'})
    for name,data in [('final_metrics',rows),('external_metrics',external),('batch_audit',audit)]:
        pd.DataFrame(data).to_csv(out/(name+'.csv'),index=False,float_format='%.12g')
    (out/'decisions.json').write_text(dumps(decisions))
    package={'frame':'data/panel/primary.csv','inputs':inputs(),'training_groups':sorted(dev.group),
             'test_groups':sorted(test.group),'results':results,'frozen_sha256':sha256(out/'frozen.json'),
             'verification_scope':'Hashes, group separation, final predictions and metrics; use full replay to verify fitting and selection.'}
    (out/'VERIFY.json').write_text(dumps(package))
    print('FINALIZED',len(results),'model-target evaluations; gates passed:',[d['target'] for d in decisions if d['passes_pilot_gate']],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('phase',choices=['develop','finalize']); p.add_argument('--out',default='research/initial')
    a=p.parse_args(); out=ROOT/a.out; out.mkdir(parents=True,exist_ok=True)
    sentinel=out/('frozen.json' if a.phase=='develop' else 'VERIFY.json')
    if sentinel.exists(): raise SystemExit('Refusing to overwrite existing phase; use a new --out directory for replay.')
    with threadpool_limits(limits=1):
        (develop if a.phase=='develop' else finalize)(out)
