"""Prospective contributor trial: literature pairs versus blind compact models."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']: os.environ[key]='1'
import argparse,json,pathlib,time
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from core import assert_disjoint,dumps,metrics,predict,sha256
from models import features_for,linear_fit,preprocess,splits
from benchmark import load,inputs
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'research/initial'; OUT=ROOT/'research/contributor-trial'

def pair_features(frame,y,target,family,protocol):
    if family=='biology_pair':
        features=protocol['pairs'][target]
        if any(f not in frame for f in features): raise ValueError('Missing prespecified pair')
        return features
    features=features_for(frame,'all'); x,_=preprocess(frame,features)
    x=x-x.mean(axis=0); yy=y-y.mean()
    scale=np.sqrt((x*x).sum(axis=0)*(yy@yy)); corr=np.divide(abs(x.T@yy),scale,out=np.zeros(len(features)),where=scale>1e-12)
    rank=sorted(range(len(features)),key=lambda i:(-corr[i],features[i]))[:2]
    return [features[i] for i in rank]

def fit_pair(frame,y,target,family,cfg,protocol):
    scores=[]
    for alpha in protocol['ridge_alphas']:
        loss=0
        for a,b in splits(frame,cfg['inner_folds'],cfg['inner_seed']):
            f=pair_features(frame.iloc[a],y[a],target,family,protocol)
            m=linear_fit(frame.iloc[a],y[a],f,'ridge',alpha,cfg)
            loss+=np.sum((y[b]-predict(m,frame.iloc[b]))**2)
        scores.append((float(loss/len(y)),alpha))
    _,alpha=min(scores); features=pair_features(frame,y,target,family,protocol)
    model=linear_fit(frame,y,features,'ridge',alpha,cfg)
    model['selection']={'family':family,'alpha_scores':[{'inner_mse':s,'alpha':a} for s,a in scores]}
    return model

def develop(out):
    cfg,primary,dev,test=load(); protocol=json.loads((OUT/'protocol.json').read_text()); start=time.time()
    rows=[]; predictions=[]; frozen={}; scales={}; folds=[]; loo=[]
    base_outer=pd.read_csv(BASE/'outer_predictions.csv'); base_metrics=pd.read_csv(BASE/'outer_metrics.csv')
    best={}
    for target in cfg['targets']:
        f=dev[dev['y:'+target].notna()].reset_index(drop=True); y=f['y:'+target].to_numpy(float)
        scales[target]=float(np.var(y))
        opts=base_metrics[(base_metrics.target==target)&base_metrics.model.isin(['self_expression','ridge_expr','ridge_all','elastic_expr','elastic_all'])]
        best[target]=opts.groupby('model').mse.mean().idxmin()
        for seed in cfg['outer_seeds']:
            for fold,(a,b) in enumerate(splits(f,cfg['outer_folds'],seed)):
                tr=f.iloc[a]; te=f.iloc[b]; assert_disjoint(tr,te)
                br=base_outer[(base_outer.target==target)&(base_outer.seed==seed)&(base_outer.fold==fold)&(base_outer.model=='rule_all')].set_index('model_id')
                ref=br.loc[te.model_id,'predicted'].to_numpy()
                for family in ['biology_pair','blind_pair']:
                    model=fit_pair(tr,y[a],target,family,cfg,protocol); pred=predict(model,te)
                    rows.append({'target':target,'seed':seed,'fold':fold,'model':family,**metrics(y[b],pred,ref)})
                    folds.append({'target':target,'seed':seed,'fold':fold,'family':family,'model':model})
                    for mid,yy,pp,rr in zip(te.model_id,y[b],pred,ref):
                        predictions.append({'target':target,'seed':seed,'fold':fold,'model':family,'model_id':mid,'observed':yy,'predicted':pp,'rule_prediction':rr})
        frozen[target]={family:fit_pair(f,y,target,family,cfg,protocol) for family in ['biology_pair','blind_pair']}
        for label,n in f.lineage.value_counts().sort_index().items():
            if n<cfg['lineage_min_test'] or len(f)-n<cfg['lineage_min_train']: continue
            tr=f[f.lineage!=label]; te=f[f.lineage==label]
            ref=np.full(len(te),tr['y:'+target].mean())
            for family in ['biology_pair','blind_pair']:
                model=fit_pair(tr,tr['y:'+target].to_numpy(float),target,family,cfg,protocol)
                loo.append({'target':target,'lineage':label,'model':family,**metrics(te['y:'+target],predict(model,te),ref)})
        print('TRIAL DEVELOPED',target,'best comparator',best[target],flush=True)
    for name,data in [('outer_metrics',rows),('outer_predictions',predictions),('lineage_metrics',loo)]:
        pd.DataFrame(data).to_csv(out/(name+'.csv'),index=False,float_format='%.12g')
    (out/'fold_models.json').write_text(dumps(folds))
    frozen={'models':frozen,'scales':scales,'best_linear':best,'inputs':inputs(),
        'trial_code_sha256':sha256(ROOT/'src/trial.py'),'protocol_sha256':sha256(OUT/'protocol.json'),
        'baseline_frozen_sha256':sha256(BASE/'frozen.json'),'elapsed_seconds':time.time()-start}
    (out/'frozen.json').write_text(dumps(frozen))
    print('TRIAL FROZEN',round(time.time()-start,2),'seconds',flush=True)

def macro_summary(frame,protocol):
    # One independent observation is a cell-line identity; targets stay together.
    loss=frame.groupby('model_id')[['candidate_loss','reference_loss']].mean().to_numpy()
    rng=np.random.default_rng(protocol['bootstrap_seed'])
    ix=rng.integers(0,len(loss),size=(protocol['bootstrap_replicates'],len(loss)))
    boot=loss[ix].sum(axis=1); values=1-boot[:,0]/boot[:,1]
    return {'n_independent_models':len(loss),'normalized_mse_skill':float(1-loss[:,0].sum()/loss[:,1].sum()),
            'ci95':[float(x) for x in np.quantile(values,[.025,.975])]}

def finalize(out):
    cfg,primary,dev,test=load(); protocol=json.loads((OUT/'protocol.json').read_text())
    frozen=json.loads((out/'frozen.json').read_text()); base=json.loads((BASE/'frozen.json').read_text())
    if frozen['inputs']!=inputs() or frozen['trial_code_sha256']!=sha256(ROOT/'src/trial.py') or frozen['protocol_sha256']!=sha256(OUT/'protocol.json') or frozen['baseline_frozen_sha256']!=sha256(BASE/'frozen.json'):
        raise ValueError('Changed since freeze')
    ext=pd.read_csv(ROOT/'data/panel/sanger.csv'); ext=ext[ext.partition=='external']; assert_disjoint(primary,ext)
    rows=[]; cert=[]; losses=[]; extrows=[]
    for target in cfg['targets']:
        f=test[test['y:'+target].notna()]; y=f['y:'+target].to_numpy(float); ref=predict(base['models'][target]['rule_all'],f)
        for family,model in frozen['models'][target].items():
            pred=predict(model,f); score=metrics(y,pred,ref)
            rows.append({'target':target,'model':family,**score})
            cert.append({'target':target,'name':family,'model':model,'reference':base['models'][target]['rule_all'],
                         'model_ids':f.model_id.tolist(),'predictions':pred.tolist(),'metrics':score})
            for comparator,cm in [('rule_all',base['models'][target]['rule_all']),('blind_pair',frozen['models'][target]['blind_pair']),
                                   ('best_linear',base['models'][target][frozen['best_linear'][target]])]:
                cp=predict(cm,f)
                for mid,yy,pp,rr in zip(f.model_id,y,pred,cp):
                    losses.append({'target':target,'model_id':mid,'family':family,'comparator':comparator,
                        'candidate_loss':float((yy-pp)**2/frozen['scales'][target]),'reference_loss':float((yy-rr)**2/frozen['scales'][target])})
            ex=ext[ext['y:'+target].notna()]
            if len(ex): extrows.append({'target':target,'model':family,**metrics(ex['y:'+target],predict(model,ex),predict(base['models'][target]['rule_all'],ex))})
    lf=pd.DataFrame(losses); summaries={}
    for (family,comp),part in lf.groupby(['family','comparator']): summaries[family+'_vs_'+comp]=macro_summary(part,protocol)
    outer=pd.read_csv(out/'outer_predictions.csv'); outer['candidate_loss']=(outer.observed-outer.predicted)**2/outer.target.map(frozen['scales'])
    outer['reference_loss']=(outer.observed-outer.rule_prediction)**2/outer.target.map(frozen['scales'])
    pooled=outer.groupby(['model','seed','fold'])[['candidate_loss','reference_loss']].mean().reset_index()
    stability={}
    for family,f in pooled.groupby('model'): stability[family]=float((f.candidate_loss<f.reference_loss).mean())
    primary_result=summaries['biology_pair_vs_rule_all']
    result={'comparisons':summaries,'outer_positive_fraction':stability,
       'passes_trial_gate':bool(primary_result['normalized_mse_skill']>=protocol['minimum_macro_skill'] and primary_result['ci95'][0]>0 and stability['biology_pair']>=protocol['minimum_positive_outer_folds']),
       'scope':'Prospective fixed-family computational prediction comparison; known priors, no new biological discovery.'}
    (out/'summary.json').write_text(dumps(result))
    for name,data in [('final_metrics',rows),('final_losses',losses),('external_metrics',extrows)]: pd.DataFrame(data).to_csv(out/(name+'.csv'),index=False,float_format='%.12g')
    package={'frame':'data/panel/primary.csv','inputs':inputs(),'training_groups':sorted(dev.group),'test_groups':sorted(test.group),
       'results':cert,'trial_frozen_sha256':sha256(out/'frozen.json')}
    (out/'VERIFY.json').write_text(dumps(package))
    print(dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('phase',choices=['develop','finalize']); p.add_argument('--out',default='research/contributor-trial')
    a=p.parse_args(); out=ROOT/a.out; out.mkdir(parents=True,exist_ok=True)
    if (out/('frozen.json' if a.phase=='develop' else 'VERIFY.json')).exists(): raise SystemExit('Refusing overwrite; choose new output directory')
    with threadpool_limits(limits=1): (develop if a.phase=='develop' else finalize)(out)
