"""Shi et al. (2024) elastic-net dependency predictor on the 773-identity development cohort.

Published recipe (xushiabbvie/TDtool 6d7ef3a, build_model_predict_TCGADEPMAP.R): genome-wide
expression z-scored per gene, glmnet alpha=0.5, lambda.min from 10-fold cv.glmnet, default
100-lambda path. Two arms:
  exact    all 773 identities, the authors' in-sample ("resubstitution") correlation
  adapted  same objective inside the saved wide300 outer folds (seed 1701), fold-local
           imputation/scaling and inner lambda selection, scored out of fold
Reads the pinned 24Q2 expression matrix and committed development outcomes only. No Broad,
historical-final or Sanger outcomes are inputs. Celligner/TCGA alignment is not reproduced.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='1'
import argparse
import csv
import json
import multiprocessing
from pathlib import Path
import re
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import enet_path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'src'))
from core import dumps,sha256  # noqa: E402
from models import splits  # noqa: E402

OLD=ROOT/'data/raw/OmicsExpressionProteinCodingGenesTPMLogp1.csv'
CACHE=ROOT/'data/raw/published-reference-20261030-expression.npy'
PATHS=ROOT/'data/raw/published-reference-20261030-paths.npz'
DEVELOPMENT=ROOT/'research/readiness-20261021/development.csv'
WIDE=ROOT/'research/wide-expression-20261021/models.json'


def protocol():
    return json.loads((HERE/'protocol.json').read_text())


def wide():
    return json.loads(WIDE.read_text())


def extract():
    """773 x 18,953 matrix in the saved wide300 universe/row order, checked against the panel extract."""
    lock=json.loads((ROOT/'data/source-lock.json').read_text())
    want=next(r['sha256'] for r in lock['files'] if r['name']==OLD.name)
    if sha256(OLD)!=want:raise ValueError('Changed expression input')
    w=wide();genes=w['gene_universe'];ids=w['development_ids']
    with OLD.open(newline='') as f:head=next(csv.reader(f))
    positions={};ambiguous=set()
    for index,name in enumerate(head[1:],1):
        gid=re.fullmatch(r'(.+) \((\d+)\)',name)[2]
        if gid in positions:ambiguous.add(gid)
        positions[gid]=index
    if ambiguous&set(genes):raise ValueError('Ambiguous gene in saved universe')
    table=pd.read_csv(OLD,header=None,skiprows=1,index_col=0,dtype={0:str})
    if table.index.duplicated().any():raise ValueError('Duplicate matrix model')
    x=table.loc[ids,[positions[g] for g in genes]].to_numpy(float)
    if np.isinf(x).any() or (x<0).any():raise ValueError('Invalid expression')
    frame=pd.read_csv(DEVELOPMENT)
    if frame.model_id.tolist()!=ids or frame.group.duplicated().any():raise ValueError('Development rows differ from saved reference')
    for index in w['panel_indices']:
        gene=re.fullmatch(r'(.+) \(\d+\)',w['gene_names'][genes[index]])[1]
        if not np.allclose(x[:,index],frame['expr:'+gene],atol=1e-9,rtol=0,equal_nan=True):raise ValueError('Panel extract differs '+gene)
    np.save(CACHE,x)
    return {'rows':len(ids),'genes':len(genes),'missing_values':int(np.isnan(x).sum()),'expression_sha256':want}


def inputs():
    frame=pd.read_csv(DEVELOPMENT);x=np.load(CACHE)
    if x.shape!=(773,18953) or len(frame)!=773:raise ValueError('Run extract first')
    return frame,x


def prepare(x):
    """Training-only: median imputation, drop constant genes, population-SD z-score (glmnet standardize=TRUE)."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        med=np.nanmedian(x,axis=0)
    med=np.nan_to_num(med,nan=0.0);filled=np.where(np.isnan(x),med,x)
    center=filled.mean(axis=0);scale=filled.std(axis=0);keep=np.flatnonzero(scale>1e-12)
    return keep,med[keep],center[keep],scale[keep]


def apply(x,prep):
    keep,med,center,scale=prep;data=x[:,keep]
    return np.asfortranarray((np.where(np.isnan(data),med,data)-center)/scale)


def grid(xs,yc,p):
    """glmnet default path: nlambda log-spaced from lambda_max down to lambda.min.ratio (0.01 when n<p)."""
    top=np.max(np.abs(xs.T@yc))/(len(yc)*p['l1_ratio'])
    return np.geomspace(top,top*p['lambda_min_ratio'],p['n_lambda'])


def path(xs,yc,alphas,p):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',ConvergenceWarning)
        _,coefs,_=enet_path(xs,yc,l1_ratio=p['l1_ratio'],alphas=alphas,max_iter=p['max_iter'],tol=p['tol'])
    return coefs,sum(issubclass(c.category,ConvergenceWarning) for c in caught)


def nested(frame,x,y,folds,seed,p,refit=True):
    """cv.glmnet analogue: lambda grid from the full training set, re-prepared inner folds, min pooled MSE."""
    prep=prepare(x);xs=apply(x,prep);mean=float(y.mean());alphas=grid(xs,y-mean,p)
    cv=np.full((len(y),len(alphas)),np.nan);warned=0
    for a,b in splits(frame,folds,seed):
        inner=prepare(x[a]);coefs,w=path(apply(x[a],inner),y[a]-y[a].mean(),alphas,p);warned+=w
        cv[b]=apply(x[b],inner)@coefs+y[a].mean()
    losses=((y[:,None]-cv)**2).sum(axis=0)
    best=int(np.argmin(losses))  # first minimum on a descending grid = larger penalty on exact ties
    coefs=None
    if refit:coefs,w=path(xs,y-mean,alphas[:best+1],p);warned+=w  # warm-started path stops at lambda.min
    return {'prep':prep,'alphas':alphas,'coefs':coefs,'mean':mean,'best':best,'cv':cv,
            'inner_mse':(losses/len(y)).tolist(),'convergence_warnings':warned}


def summary(fit,genes):
    keep=fit['prep'][0];coef=fit['coefs'][:,fit['best']];nz=np.flatnonzero(coef)
    return {'lambda_index':fit['best'],'lambda':float(fit['alphas'][fit['best']]),
            'lambda_boundary':fit['best'] in (0,len(fit['alphas'])-1),'nonzero':len(nz),
            'convergence_warnings':fit['convergence_warnings'],'inner_mse':fit['inner_mse'],
            'coefficients':{genes[keep[i]]:float(coef[i]) for i in nz[np.argsort(-np.abs(coef[nz]))]}}


def rho(y,pred):
    return float(spearmanr(y,pred).statistic) if np.ptp(pred)>0 else None


def outcome(frame,target):
    y=frame['y:'+target].to_numpy(float)
    if not np.isfinite(y).all():raise ValueError('Unexpected missing outcome')
    return y


def price_target(target):
    """Stage 1, favorable best case: the whole outer-fold path, so lambda can be chosen with test outcomes."""
    p=protocol();frame,x=inputs();y=outcome(frame,target)
    start=time.perf_counter();along=np.full((len(y),p['n_lambda']),np.nan);folds=[]
    for fold,(a,b) in enumerate(splits(frame,p['outer_folds'],p['outer_seed'])):
        prep=prepare(x[a]);xs=apply(x[a],prep);mean=float(y[a].mean());alphas=grid(xs,y[a]-mean,p)
        coefs,warned=path(xs,y[a]-mean,alphas,p);along[b]=apply(x[b],prep)@coefs+mean
        folds.append({'fold':fold,'lambdas':alphas.tolist(),'nonzero':(coefs!=0).sum(axis=0).tolist(),'convergence_warnings':warned})
    if not np.isfinite(along).all():raise ValueError('Incomplete path coverage')
    curve=[rho(y,along[:,k]) for k in range(p['n_lambda'])]
    best=int(np.nanargmax(np.array(curve,dtype=float)))
    return target,{'path_oof':along,'spearman_by_position':curve,'best_position':best,
                   'best_spearman':curve[best],'folds':folds,'seconds':time.perf_counter()-start}


def adapted_target(target):
    """Stage 2: inner-CV lambda per outer fold; the outer path is rerun only down to the chosen lambda."""
    p=protocol();frame,x=inputs();genes=wide()['gene_universe'];y=outcome(frame,target)
    cached=np.load(PATHS)[target]
    start=time.perf_counter();oof=np.full(len(y),np.nan);folds=[];drift=0.
    for fold,(a,b) in enumerate(splits(frame,p['outer_folds'],p['outer_seed'])):
        fit=nested(frame.iloc[a],x[a],y[a],p['inner_folds'],p['inner_seed'],p,refit=False)
        coefs,warned=path(apply(x[a],fit['prep']),y[a]-fit['mean'],fit['alphas'][:fit['best']+1],p)
        fit['coefs']=coefs;fit['convergence_warnings']+=warned
        oof[b]=apply(x[b],fit['prep'])@coefs[:,-1]+fit['mean']
        drift=max(drift,float(np.max(np.abs(oof[b]-cached[b,fit['best']]))))
        folds.append({'fold':fold,'test_ids':frame.model_id.iloc[b].tolist(),**summary(fit,genes)})
    if not np.isfinite(oof).all():raise ValueError('Incomplete OOF coverage')
    if drift>1e-9:raise ValueError('Stage 2 path differs from stage 1 cache')
    return target,{'oof':oof.tolist(),'max_abs_difference_from_stage1_path':drift,'folds':folds,'seconds':time.perf_counter()-start}


def exact_target(target):
    p=protocol();frame,x=inputs();genes=wide()['gene_universe']
    y=frame['y:'+target].to_numpy(float);start=time.perf_counter()
    fit=nested(frame,x,y,p['exact_cv_folds'],p['exact_cv_seed'],p)
    fitted=apply(x,fit['prep'])@fit['coefs'][:,fit['best']]+fit['mean']
    cv=fit['cv'][:,fit['best']]
    def pearson(pred):return float(pearsonr(y,pred).statistic) if np.ptp(pred)>0 else None
    return target,{'resubstitution_pearson':pearson(fitted),'resubstitution_spearman':rho(y,fitted),
                   'cv_at_lambda_min_pearson':pearson(cv),'cv_at_lambda_min_spearman':rho(y,cv),
                   **summary(fit,genes),'seconds':time.perf_counter()-start}


def run(kind,targets,workers):
    func={'price':price_target,'adapted':adapted_target,'exact':exact_target}[kind]
    out=HERE/f'{kind}.json'
    if out.exists():raise SystemExit('Refusing to overwrite '+out.name)
    start=time.perf_counter();code=sha256(Path(__file__))
    with multiprocessing.get_context('fork').Pool(workers) as pool:
        results=dict(pool.imap_unordered(func,targets))
    if kind=='price':
        np.savez(PATHS,**{t:results[t].pop('path_oof') for t in targets})
    for t in targets:print(kind.upper(),t,round(results[t]['seconds'],1),'s',flush=True)
    record={'schema':f'published-reference-{kind}/v1','protocol_sha256':sha256(HERE/'protocol.json'),
            'code_sha256':code,'expression_sha256':sha256(OLD),
            'wall_seconds':time.perf_counter()-start,'workers':workers,'targets':{t:results[t] for t in targets}}
    out.write_text(dumps(record))


def score():
    p=protocol();frame=pd.read_csv(DEVELOPMENT);w=wide();out=HERE/'results.json'
    if out.exists():raise SystemExit('Refusing to overwrite results.json')
    price=json.loads((HERE/'price.json').read_text())['targets']
    adapted=json.loads((HERE/'adapted.json').read_text())['targets'];exact=json.loads((HERE/'exact.json').read_text())['targets']
    preds={t:{'elastic_net':np.array(adapted[t]['oof']),**{s:np.array(w['targets'][t]['oof_predictions'][s]) for s in ['wide300','panel30','lineage']}} for t in p['targets']}
    ys={t:outcome(frame,t) for t in p['targets']}
    for t in p['targets']:
        if w['targets'][t]['model_ids']!=frame.model_id.tolist():raise ValueError('Row order differs '+t)
    families=['elastic_net','wide300','panel30','lineage'];per={}
    for t in p['targets']:
        y=ys[t];row={}
        for s in families:
            v=preds[t][s];row[s]={'spearman':rho(y,v),'pearson':float(pearsonr(y,v).statistic),'mse':float(np.mean((y-v)**2))}
        if abs(row['wide300']['spearman']-w['targets'][t]['metrics']['wide300']['spearman'])>1e-12:raise ValueError('Saved metric mismatch '+t)
        row['elastic_net'].update({'nonzero_by_fold':[f['nonzero'] for f in adapted[t]['folds']],
            'lambda_index_by_fold':[f['lambda_index'] for f in adapted[t]['folds']],
            'boundary_hits':sum(f['lambda_boundary'] for f in adapted[t]['folds']),
            'convergence_warnings':sum(f['convergence_warnings'] for f in adapted[t]['folds'])})
        row['stage1_ceiling_spearman']=price[t]['best_spearman'];row['stage1_ceiling_position']=price[t]['best_position']
        row['exact']={k:exact[t][k] for k in ['resubstitution_pearson','resubstitution_spearman','cv_at_lambda_min_pearson',
            'cv_at_lambda_min_spearman','nonzero','lambda_index','lambda_boundary','convergence_warnings']}
        per[t]=row
    mean=lambda key,s:float(np.mean([per[t][s][key] for t in p['targets']]))
    aggregate={s:{'spearman':mean('spearman',s),'pearson':mean('pearson',s)} for s in families}
    ceiling=float(np.mean([per[t]['stage1_ceiling_spearman'] for t in p['targets']]))
    rng=np.random.default_rng(20261030);n=len(frame);draws={'wide300':[],'panel30':[]}
    for _ in range(2000):
        idx=rng.integers(0,n,n)
        en=np.mean([rho(ys[t][idx],preds[t]['elastic_net'][idx]) for t in p['targets']])
        for s in draws:draws[s].append(en-np.mean([rho(ys[t][idx],preds[t][s][idx]) for t in p['targets']]))
    interval={s:[float(np.percentile(v,2.5)),float(np.percentile(v,97.5))] for s,v in draws.items()}
    passes=lambda vals:sum(v is not None and v>0.2 for v in vals)
    record={'schema':'published-reference-results/v1','protocol_sha256':sha256(HERE/'protocol.json'),
        'aggregate':aggregate,'primary_elastic_net_minus_wide300':aggregate['elastic_net']['spearman']-aggregate['wide300']['spearman'],
        'elastic_net_minus_panel30':aggregate['elastic_net']['spearman']-aggregate['panel30']['spearman'],
        'bootstrap_95':interval,'stage1_ceiling_mean_spearman':ceiling,
        'price_rule_triggered':ceiling<=aggregate['wide300']['spearman'],
        'exact_mean_resubstitution_pearson':float(np.mean([per[t]['exact']['resubstitution_pearson'] for t in p['targets']])),
        'exact_mean_cv_at_lambda_min_pearson':float(np.mean([per[t]['exact']['cv_at_lambda_min_pearson'] for t in p['targets']])),
        'r_above_0_2':{'resubstitution':passes([per[t]['exact']['resubstitution_pearson'] for t in p['targets']]),
            'cv_at_lambda_min':passes([per[t]['exact']['cv_at_lambda_min_pearson'] for t in p['targets']]),
            'adapted_oof':passes([per[t]['elastic_net']['pearson'] for t in p['targets']])},
        'targets':per}
    record['h2_resubstitution_minus_oof_pearson']=record['exact_mean_resubstitution_pearson']-aggregate['elastic_net']['pearson']
    out.write_text(dumps(record))
    return {k:v for k,v in record.items() if k!='targets'}


def control(target):
    """Positive control: the saved wide300/panel30 OOF predictions replay from this extraction."""
    import wide_expression as we
    p=we.protocol();frame,x=inputs();w=wide();genes=w['gene_universe']
    y=frame['y:'+target].to_numpy(float);saved=w['targets'][target]['oof_predictions'];worst={}
    for scope in ['wide300','panel30']:
        pred=np.full(len(y),np.nan)
        for a,b in splits(frame,p['outer_folds'],p['outer_seed']):
            model,_=we.fit_nested(frame.iloc[a],x[a],y[a],genes,scope,w['panel_indices'],p)
            pred[b]=we.predict(model,x[b],genes)
        worst[scope]=float(np.max(np.abs(pred-np.array(saved[scope]))))
    return worst


def main():
    a=argparse.ArgumentParser()
    a.add_argument('action',choices=['extract','control','price','adapted','exact','score'])
    a.add_argument('--target',default='MDM2');a.add_argument('--targets',nargs='*');a.add_argument('--workers',type=int,default=2)
    args=a.parse_args()
    if args.action=='extract':print(json.dumps(extract(),indent=2))
    elif args.action=='control':print(json.dumps(control(args.target),indent=2))
    elif args.action=='score':print(json.dumps(score(),indent=2))
    else:run(args.action,args.targets or protocol()['targets'],args.workers)


if __name__=='__main__':main()
