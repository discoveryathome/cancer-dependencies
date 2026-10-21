"""Bounded expression breadth trial; fold-local feature selection and ridge tuning.

check/train/predict do not read external dependency outcomes. Broad scoring is
exploratory: the cohort was exposed in earlier work. Sanger is never an input.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='1'
import argparse
import csv
import json
from pathlib import Path
import re
import time
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from threadpoolctl import threadpool_limits

from core import dumps,sha256
from models import splits
import transfer_trial as transfer

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'research/wide-expression-20261021'
OLD=ROOT/'data/raw/OmicsExpressionProteinCodingGenesTPMLogp1.csv'
NEW=ROOT/'data/raw/transfer-trial-20261021/next_gen_expression.csv'
DEVELOPMENT=ROOT/'research/readiness-20261021/development.csv'
FROZEN=ROOT/'research/transfer-trial-20261021/run/frozen.json'
FAMILIES=['wide300','panel30','lineage']


def protocol():
    return transfer.read_json(PACKAGE/'protocol.json')


def headers(path, allow_ambiguous=False):
    with path.open(newline='') as f: head=next(csv.reader(f))
    if len(head)!=len(set(head)):raise ValueError('Duplicate headers')
    mapping={};ambiguous=set()
    for index,name in enumerate(head[1:],1):
        match=re.fullmatch(r'(.+) \((\d+)\)',name)
        if not match:raise ValueError('Unrecognized gene header '+name)
        gid=match[2]
        if gid in mapping:
            if not allow_ambiguous:raise ValueError('Duplicate EntrezID')
            ambiguous.add(gid)
        mapping[gid]={'position':index,'name':name}
    for gid in ambiguous:del mapping[gid]
    return head,mapping


def read_rows(path,ids,genes):
    head,mapping=headers(path,allow_ambiguous=True)
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate requested model identity')
    if any(g not in mapping for g in genes):raise ValueError('Absent stable gene')
    positions=[mapping[g]['position'] for g in genes];wanted=set(ids);rows={};seen=set()
    with path.open(newline='') as f:
        reader=csv.reader(f);next(reader)
        for row in reader:
            if len(row)!=len(head):raise ValueError('Ragged matrix')
            if not row[0] or row[0] in seen:raise ValueError('Missing/duplicate matrix model')
            seen.add(row[0])
            if row[0] not in wanted:continue
            values=np.array([np.nan if row[i] in ('','NA','NaN','nan') else float(row[i]) for i in positions])
            if np.isinf(values).any() or (values<0).any():raise ValueError('Invalid expression')
            rows[row[0]]=values
    if set(rows)!=wanted:raise ValueError('Missing requested model rows')
    return np.array([rows[i] for i in ids])


def input_spec():
    original=transfer.load_freeze(FROZEN.parent)
    p=protocol()
    if p['targets']!=original['protocol']['targets']:raise ValueError('Changed target panel')
    source=transfer.read_json(ROOT/'data/source-lock.json')
    old_hash=next(r['sha256'] for r in source['files'] if r['name']==OLD.name)
    new_source=transfer.read_json(ROOT/'research/transfer-results-20261021/source-manifest.json')
    return original,old_hash,new_source


def inputs():
    original,old_hash,new_source=input_spec()
    if sha256(OLD)!=old_hash or sha256(NEW)!=new_source['expression_sha256']:raise ValueError('Changed expression input')
    p=protocol();cols=['model_id','group','lineage']+['expr:'+g for g in original['protocol']['predictors']]+['y:'+g for g in p['targets']]
    frame=pd.read_csv(DEVELOPMENT,usecols=cols)
    if len(frame)!=773 or frame.model_id.duplicated().any() or frame.group.duplicated().any():raise ValueError('Invalid development identities')
    _,a=headers(OLD,allow_ambiguous=True);_,b=headers(NEW,allow_ambiguous=True);genes=sorted(set(a)&set(b),key=int)
    x=read_rows(OLD,frame.model_id.tolist(),genes)
    panel=[re.fullmatch(r'(.+) \((\d+)\)',original['gene_map']['expr'][g])[2] for g in original['protocol']['predictors']]
    panel_index=[genes.index(g) for g in panel]
    for gene,index in zip(original['protocol']['predictors'],panel_index):
        if not np.allclose(x[:,index],frame['expr:'+gene],atol=1e-9,rtol=0,equal_nan=True):raise ValueError('Historical expression extract differs')
    return frame,x,genes,panel_index,{g:a[g]['name'] for g in genes},original,new_source


def select_features(x,y,genes,scope,panel_index,top=300):
    if not np.isfinite(y).all() or len(x)!=len(y):raise ValueError('Invalid training responses')
    if scope not in ['wide300','panel30']:raise ValueError('Unknown scope')
    eligible=np.flatnonzero(np.isfinite(x).mean(axis=0)>=.9)
    if scope=='panel30':
        if not set(panel_index)<=set(eligible):raise ValueError('Incomplete panel30 training support')
        eligible=np.array(panel_index)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        med=np.nanmedian(x[:,eligible],axis=0)
    filled=np.where(np.isnan(x[:,eligible]),med,x[:,eligible]);scale=filled.std(axis=0)
    variable=scale>1e-12
    if scope=='panel30' and not variable.all():raise ValueError('Constant panel30 feature')
    eligible=eligible[variable];med=med[variable];filled=filled[:,variable];scale=scale[variable]
    if scope=='wide300':
        if len(eligible)<top:raise ValueError('Too few eligible broad features')
        centered=filled-filled.mean(axis=0);dy=y-y.mean()
        denominator=np.sqrt(np.sum(centered*centered,axis=0)*np.sum(dy*dy))
        scores=np.divide(np.abs(centered.T@dy),denominator,out=np.zeros(len(eligible)),where=denominator>0)
        # Stable gene IDs break correlation ties; no test data or response consulted.
        chosen=np.lexsort((np.array([int(genes[i]) for i in eligible]),-scores))[:top]
        eligible=eligible[chosen];med=med[chosen];filled=filled[:,chosen];scale=scale[chosen]
    return eligible,med,filled.mean(axis=0),scale


def transform(x,selection):
    indices,med,center,scale=selection
    data=x[:,indices];return (np.where(np.isnan(data),med,data)-center)/scale


def fit_once(x,y,genes,scope,panel_index,alpha):
    selection=select_features(x,y,genes,scope,panel_index)
    model=Ridge(alpha=alpha,solver='cholesky').fit(transform(x,selection),y)
    indices,med,center,scale=selection
    return {'features':[genes[i] for i in indices],'medians':med.tolist(),'center':center.tolist(),
        'scale':scale.tolist(),'coef':model.coef_.tolist(),'intercept':float(model.intercept_),'alpha':alpha}


def predict(model,x,genes):
    lookup={g:i for i,g in enumerate(genes)}
    selection=(np.array([lookup[g] for g in model['features']]),np.array(model['medians']),np.array(model['center']),np.array(model['scale']))
    result=model['intercept']+transform(x,selection)@np.array(model['coef'])
    if not np.isfinite(result).all():raise ValueError('Nonfinite prediction')
    return result


def fit_nested(frame,x,y,genes,scope,panel_index,p):
    losses={alpha:0. for alpha in p['alphas']};ledger=[]
    for fold,(a,b) in enumerate(splits(frame,p['inner_folds'],p['inner_seed'])):
        selection=select_features(x[a],y[a],genes,scope,panel_index)
        train,test=transform(x[a],selection),transform(x[b],selection)
        row={'fold':fold,'train_groups':frame.iloc[a].group.tolist(),'test_ids':frame.iloc[b].model_id.tolist(),
             'features':[genes[i] for i in selection[0]],'squared_errors':{}}
        for alpha in p['alphas']:
            fitted=Ridge(alpha=alpha,solver='cholesky').fit(train,y[a])
            error=float(np.sum((y[b]-fitted.predict(test))**2));losses[alpha]+=error;row['squared_errors'][str(alpha)]=error
        ledger.append(row)
    best=min(losses,key=lambda alpha:(losses[alpha],-alpha))
    return fit_once(x,y,genes,scope,panel_index,best),{'inner_mse':{str(k):v/len(y) for k,v in losses.items()},'chosen_alpha':best,'folds':ledger}


def lineage_predict(train,y,test):
    mean=float(np.mean(y));labels=train.lineage.to_numpy()
    mapping={label:float((y[labels==label].sum()+10*mean)/((labels==label).sum()+10)) for label in set(labels)}
    return np.array([mapping.get(label,mean) for label in test.lineage])


def rho(y,pred):
    return float(spearmanr(y,pred).statistic) if len(y)>=3 and np.ptp(y)>0 and np.ptp(pred)>0 else None


def train_compute():
    frame,x,genes,panel_index,names,original,source=inputs();p=protocol();start=time.perf_counter()
    results={};references={};summary={}
    for target in p['targets']:
        valid=np.isfinite(frame['y:'+target].to_numpy(float));f=frame.loc[valid].reset_index(drop=True);xx=x[valid];y=f['y:'+target].to_numpy(float)
        predictions={s:np.full(len(y),np.nan) for s in FAMILIES};folds=[]
        for fold,(a,b) in enumerate(splits(f,p['outer_folds'],p['outer_seed'])):
            if time.perf_counter()-start>p['limits']['training_wall_minutes']*60:raise TimeoutError('Declared training budget reached')
            row={'fold':fold,'train_groups':f.iloc[a].group.tolist(),'test_ids':f.iloc[b].model_id.tolist(),'models':{},'selection':{}}
            for scope in ['wide300','panel30']:
                model,ledger=fit_nested(f.iloc[a],xx[a],y[a],genes,scope,panel_index,p)
                predictions[scope][b]=predict(model,xx[b],genes);row['models'][scope]=model;row['selection'][scope]=ledger
            predictions['lineage'][b]=lineage_predict(f.iloc[a],y[a],f.iloc[b]);folds.append(row)
        final={};selection={}
        for scope in ['wide300','panel30']:
            final[scope],selection[scope]=fit_nested(f,xx,y,genes,scope,panel_index,p)
        by_family={s:{'spearman':rho(y,v),'mse':float(np.mean((y-v)**2))} for s,v in predictions.items()}
        if any(not np.isfinite(v).all() for v in predictions.values()):raise ValueError('Incomplete OOF coverage')
        results[target]={'n':len(y),'model_ids':f.model_id.tolist(),'excluded_missing_target':frame.loc[~valid,'model_id'].tolist(),
            'oof_predictions':{s:v.tolist() for s,v in predictions.items()},'metrics':by_family,'folds':folds,
            'final_models':final,'final_selection':selection}
        summary[target]=by_family
        print('FIT',target,{k:round(v['spearman'],4) if v['spearman'] is not None else None for k,v in by_family.items()},flush=True)
    if any(summary[t][s]['spearman'] is None for t in p['targets'] for s in ['wide300','panel30']):raise ValueError('Undefined primary target')
    aggregate={s:float(np.mean([summary[t][s]['spearman'] for t in p['targets']])) for s in FAMILIES}
    bindings=transfer.bind([Path(__file__),PACKAGE/'protocol.json',PACKAGE/'gene-identity-amendment.json',DEVELOPMENT,FROZEN,ROOT/'src/core.py',ROOT/'src/models.py',ROOT/'src/transfer_trial.py',ROOT/'data/source-lock.json',ROOT/'research/transfer-results-20261021/source-manifest.json'])
    return {'schema':'wide-expression-models/v1','targets':results,'gene_universe':genes,'gene_names':names,
        'panel_indices':panel_index,'development_ids':frame.model_id.tolist(),'bindings':bindings,
        'raw_hashes':{str(OLD.relative_to(ROOT)):sha256(OLD),str(NEW.relative_to(ROOT)):source['expression_sha256']},
        'aggregate_oof_spearman':aggregate,'primary_wide_minus_panel30':aggregate['wide300']-aggregate['panel30']}


def load_models():
    data=transfer.read_json(PACKAGE/'models.json');transfer.check_bindings(data['bindings'])
    for name,h in data['raw_hashes'].items():
        if sha256(ROOT/name)!=h:raise ValueError('Changed raw input')
    return data


def predict_compute():
    data=load_models();frozen=transfer.load_freeze(FROZEN.parent)
    rows=frozen['cohort'];ids=[r['model_id'] for r in rows]
    if len(ids)!=77 or len(set(r['group'] for r in rows))!=77:raise ValueError('Changed external cohort')
    genes=data['gene_universe'];x=read_rows(NEW,ids,genes);predictions={};missing={}
    previous=transfer.read_json(FROZEN.parent/'predictions.json')
    if ids!=[r['model_id'] for r in previous['rows']]:raise ValueError('Changed external order')
    for target,row in data['targets'].items():
        predictions[target]={};missing[target]={}
        for scope,model in row['final_models'].items():
            predictions[target][scope]=predict(model,x,genes).tolist()
            subset=x[:,[genes.index(g) for g in model['features']]]
            missing[target][scope]={'selected_features':len(model['features']),'missing_values':int(np.isnan(subset).sum()),
                'per_model_missing':dict(zip(ids,np.isnan(subset).sum(axis=1).tolist()))}
        for family in ['lineage','strong_expression','compact_expression_pair']:
            predictions[target][family]=previous['predictions'][target][family]
    return {'schema':'wide-expression-predictions/v1','rows':rows,'predictions':predictions,'missingness':missing,
        'models_sha256':sha256(PACKAGE/'models.json'),'original_predictions_sha256':sha256(FROZEN.parent/'predictions.json'),
        'source_sha256':sha256(NEW),'scope':'Already exposed Broad cohort; current predictions frozen before this round score, not independent confirmation'}


def evaluate(pred,response):
    data=load_models();frozen=transfer.load_freeze(FROZEN.parent);p=protocol();rows=pred['rows'];ids=[r['screen_id'] for r in rows]
    ymap,missing=transfer.matrix(response,p['targets'],frozen['gene_map']['y'],set(ids))
    if missing or set(ymap)!=set(ids):raise ValueError('Incomplete external outcomes')
    rng=np.random.default_rng(20261021);draws=rng.integers(0,len(ids),size=(2000,len(ids)))
    tables={};boot={'panel30':[],'strong_expression':[]}
    for target in p['targets']:
        y=np.array([ymap[i][target] for i in ids],float)
        if not np.isfinite(y).all():raise ValueError('Incomplete target coverage')
        scores={s:{'spearman':rho(y,np.array(v)),'mse':float(np.mean((y-np.array(v))**2))} for s,v in pred['predictions'][target].items()}
        strata=[]
        for label in sorted(set(r['lineage'] for r in rows)):
            keep=np.array([r['lineage']==label for r in rows]);strata.append({'lineage':label,'n':int(keep.sum()),
                'scores':{s:rho(y[keep],np.array(v)[keep]) for s,v in pred['predictions'][target].items()}})
        tables[target]={'n':len(y),'models':scores,'lineages':strata}
        wide=np.array(pred['predictions'][target]['wide300'])
        for ref in boot:
            baseline=np.array(pred['predictions'][target][ref])
            boot[ref].append(transfer.spearman_rows(y[draws],wide[draws])-transfer.spearman_rows(y[draws],baseline[draws]))
    aggregate={s:float(np.mean([v['models'][s]['spearman'] for v in tables.values()])) for s in ['wide300','panel30','strong_expression','compact_expression_pair']}
    contrasts={}
    for ref,values in boot.items():
        matrix=np.array(values).T;valid=np.isfinite(matrix).all(axis=1)
        contrasts[ref]={'estimate':aggregate['wide300']-aggregate[ref],
            'ci95':np.quantile(matrix[valid].mean(axis=1),[.025,.975]).tolist() if valid.mean()>=.95 else None,
            'valid_bootstrap_draws':int(valid.sum()),'total_bootstrap_draws':2000}
    return {'schema':'wide-expression-transfer/v1','targets':tables,'aggregate_spearman':aggregate,'wide_minus':contrasts,
        'prediction_sha256':sha256(PACKAGE/'predictions.json'),'response_sha256':sha256(response),
        'interpretation':'Exploratory same-author Broad transfer. Conditional intervals omit model selection/training uncertainty. No multiplicity-adjusted target claim or fresh confirmation.'}


def equivalent(actual,expected,path='root'):
    if isinstance(actual,dict):
        if set(actual)!=set(expected):raise ValueError('Keys differ '+path)
        for k in actual:equivalent(actual[k],expected[k],path+'/'+k)
    elif isinstance(actual,list):
        if len(actual)!=len(expected):raise ValueError('Length differs '+path)
        for i,(a,b) in enumerate(zip(actual,expected)):equivalent(a,b,path+'/'+str(i))
    elif isinstance(actual,float):
        if not np.isclose(actual,expected,atol=1e-10,rtol=1e-10,equal_nan=False):raise ValueError('Numeric replay differs '+path)
    elif actual!=expected:raise ValueError('Replay differs '+path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['check','train','verify-fit','predict','score','verify']);args=parser.parse_args();start=time.perf_counter()
    if args.phase=='check':
        original,_,_=input_spec();print('PASS bounded protocol and inherited model bindings;12targets;raw data needed for fitting, not this check');return
    with threadpool_limits(limits=1):
        if args.phase in ['train','verify-fit']:
            if args.phase=='train' and (PACKAGE/'models.json').exists():raise ValueError('Refusing overwrite')
            data=train_compute()
            if args.phase=='train':transfer.write_new(PACKAGE/'models.json',data)
            else:equivalent(data,transfer.read_json(PACKAGE/'models.json'))
            print('PRIMARY',data['primary_wide_minus_panel30'],data['aggregate_oof_spearman'])
        else:
            data=predict_compute()
            if args.phase=='predict':transfer.write_new(PACKAGE/'predictions.json',data)
            else:
                equivalent(data,transfer.read_json(PACKAGE/'predictions.json'))
                _,_,source=input_spec();response=NEW.parent/source['response_file']
                exposure={'predictions_sha256':sha256(PACKAGE/'predictions.json'),'response_sha256':source['response_sha256'],'scope':'Previously exposed Broad77, all12targets; Sanger reserved'}
                if args.phase=='score':transfer.write_new(PACKAGE/'exposure.json',{'opened_at':transfer.now(),**exposure})
                else:
                    record=transfer.read_json(PACKAGE/'exposure.json')
                    if any(record[k]!=v for k,v in exposure.items()):raise ValueError('Exposure record changed')
                if sha256(response)!=source['response_sha256']:raise ValueError('Changed response source')
                result=evaluate(data,response)
                if args.phase=='score':transfer.write_new(PACKAGE/'results.json',result)
                else:equivalent(result,transfer.read_json(PACKAGE/'results.json'))
                print('TRANSFER',dumps({'aggregate':result['aggregate_spearman'],'contrasts':result['wide_minus']}))
    elapsed=time.perf_counter()-start
    if args.phase in ['train','predict','score']:transfer.write_new(PACKAGE/(args.phase+'-timing.json'),{'phase':args.phase,'seconds':elapsed,'completed_at':transfer.now()})
    print('PASS',args.phase,'seconds',round(elapsed,3))
if __name__=='__main__':main()
