"""Development-only compact-model preparation; no final or external evaluation."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[key]='1'
import argparse,json,pathlib,time
import numpy as np
import pandas as pd
from core import dumps,sha256,predict,metrics,assert_disjoint
from models import fit_models,splits
from trial import fit_pair
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'

def load_development():
    lock=json.loads((OUT/'development-lock.json').read_text())
    for name,digest in lock['files'].items():
        if sha256(ROOT/name)!=digest:raise ValueError('Preparation input/source changed: '+name)
    f=pd.read_csv(OUT/'development.csv')
    if set(f.partition)!={'development'} or f.group.duplicated().any():raise ValueError('Development cohort invalid')
    return json.loads((ROOT/'config/benchmark.json').read_text()),f,lock

def validate_model(model,frame,cap=3):
    if model.get('kind') not in ('constant','rule','linear'):raise ValueError('Unsupported compact-model kind')
    if model['kind']=='constant':
        if not np.isfinite(float(model['value'])):raise ValueError('Nonfinite constant')
        return
    features=model['features']
    if not isinstance(features,list) or not 1<=len(features)<=cap or len(features)!=len(set(features)):raise ValueError('Feature budget/duplicates')
    if any(x not in frame or not x.startswith(('expr:','cn:','damaging:','hotspot:')) for x in features):raise ValueError('Forbidden feature')
    arrays=['medians']+(['center','scale','coef'] if model['kind']=='linear' else [])
    for name in arrays:
        a=np.asarray(model[name],float)
        if a.shape!=(len(features),) or not np.isfinite(a).all():raise ValueError('Malformed numeric model')
    if model['kind']=='linear':
        if np.any(np.asarray(model['scale'])<=0) or not np.isfinite(model['intercept']):raise ValueError('Invalid scale/intercept')
    else:
        if len(features)!=1 or any(not np.isfinite(model[n]) for n in ('threshold','left','right')):raise ValueError('Invalid rule')

def summarize(frame,target,folds,reference):
    y=[];pred=[];refs={n:[] for n in ('mean','lineage','rule','strong_linear')};lineages=[];counts=[]
    if len(folds)!=len(reference):raise ValueError('Incomplete folds')
    for row,expected in zip(folds,reference):
        if any(row.get(k)!=expected[k] for k in ('fold','train_groups','test_ids')):raise ValueError('Wrong frozen fold/identity coverage')
        train=frame[frame.group.isin(row['train_groups'])];test=frame.set_index('model_id').loc[row['test_ids']].reset_index();assert_disjoint(train,test)
        validate_model(row['model'],frame);prediction=predict(row['model'],test)
        if not np.isfinite(prediction).all():raise ValueError('Nonfinite predictions')
        y.extend(test['y:'+target]);pred.extend(prediction);lineages.extend(test.lineage)
        counts.append(len(row['model'].get('features',[])))
        for name in refs:refs[name].extend(predict(expected['models'][name],test))
    seen=[x for r in folds for x in r['test_ids']]
    if len(seen)!=len(set(seen)) or set(seen)!=set(frame.loc[frame['y:'+target].notna(),'model_id']):raise ValueError('Incomplete eligible cohort')
    result=dict(n=len(y),mse=metrics(y,pred)['mse'],max_features=max(counts),
      skill_vs={k:metrics(y,pred,v)['skill'] for k,v in refs.items()},lineages=[])
    y=np.asarray(y);pred=np.asarray(pred);lineages=np.asarray(lineages);strong=np.asarray(refs['strong_linear'])
    for label in sorted(set(lineages)):
        mask=lineages==label
        result['lineages'].append(dict(lineage=label,n=int(mask.sum()),mse=float(np.mean((y[mask]-pred[mask])**2)),
           strong_linear_mse=float(np.mean((y[mask]-strong[mask])**2)),support='descriptive; small groups are not confirmation'))
    return result

def verify(file,refit=False):
    cfg,frame,lock=load_development();d=json.loads(pathlib.Path(file).read_text());target=d.get('target')
    if target not in cfg['targets'] or d.get('version')!='compact-development-v1':raise ValueError('Wrong target/version')
    if d.get('development_lock_sha256')!=sha256(OUT/'development-lock.json'):raise ValueError('Wrong development binding')
    portfolio=json.loads((OUT/'portfolio.json').read_text());card=next(c for c in portfolio['targets'] if c['target']==target)
    refpath=ROOT/card['baseline']
    if sha256(refpath)!=card['baseline_sha256']:raise ValueError('Reference artifact changed')
    ref=json.loads(refpath.read_text());expected=summarize(frame,target,d['folds'],ref['folds'])
    if d.get('metrics')!=expected:raise ValueError('Candidate metrics/completeness mismatch')
    if refit:
        import compact_candidate
        if d.get('candidate_source_sha256')!=sha256(ROOT/'src/compact_candidate.py'):raise ValueError('Candidate source binding changed')
        for row in d['folds']:
            tr=frame[frame.group.isin(row['train_groups'])].reset_index(drop=True)
            model=compact_candidate.fit(tr,tr['y:'+target].to_numpy(float),target,cfg)
            if dumps(model)!=dumps(row['model']):raise ValueError('Training-fold refit differs')
    return dict(valid=True,target=target,**expected,interpretation='Exploratory development comparison only. Fold models do not prove honest training; source/refit review and new confirmation are required.')

def propose(target,output):
    import compact_candidate
    cfg,frame,_=load_development()
    if target not in cfg['targets']:raise ValueError('Unknown target')
    path=pathlib.Path(output)
    if path.exists():raise ValueError('Refusing to overwrite a contribution')
    card=next(c for c in json.loads((OUT/'portfolio.json').read_text())['targets'] if c['target']==target)
    refpath=ROOT/card['baseline']
    if sha256(refpath)!=card['baseline_sha256']:raise ValueError('Baseline binding changed')
    ref=json.loads(refpath.read_text());folds=[];start=time.perf_counter()
    for row in ref['folds']:
        tr=frame[frame.group.isin(row['train_groups'])].reset_index(drop=True)
        model=compact_candidate.fit(tr,tr['y:'+target].to_numpy(float),target,cfg)
        folds.append({**{k:row[k] for k in ('fold','train_groups','test_ids')},'model':model})
    package=dict(version='compact-development-v1',target=target,development_lock_sha256=sha256(OUT/'development-lock.json'),candidate_source_sha256=sha256(ROOT/'src/compact_candidate.py'),folds=folds,metrics=summarize(frame,target,folds,ref['folds']),seconds=time.perf_counter()-start)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(dumps(package));verify(path,refit=True);print('PASS proposed and refit',path)

def build():
    cfg,frame,lock=load_development();protocol=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text());cards=[]
    (OUT/'baselines').mkdir(exist_ok=True);(OUT/'candidates').mkdir(exist_ok=True)
    for target in cfg['targets']:
        start=time.perf_counter();f=frame[frame['y:'+target].notna()].reset_index(drop=True);y=f['y:'+target].to_numpy(float);reference=[];candidate=[]
        for fold,(a,b) in enumerate(splits(f,cfg['outer_folds'],cfg['outer_seeds'][0])):
            tr=f.iloc[a];te=f.iloc[b];models,search=fit_models(tr,y[a],target,cfg)
            choices=[(r['inner_mse'],r['model']) for r in search['linear']]
            loss=0.
            for u,v in splits(tr,cfg['inner_folds'],cfg['inner_seed']):
                from models import linear_fit
                m=linear_fit(tr.iloc[u],y[a][u],['expr:'+target],'self');loss+=np.sum((y[a][v]-predict(m,tr.iloc[v]))**2)
            choices.append((float(loss/len(tr)),'self_expression'));best=min(choices)[1]
            common=dict(fold=fold,train_groups=sorted(tr.group),test_ids=te.model_id.tolist())
            reference.append(dict(**common,models=dict(mean=models['mean'],lineage=models['lineage'],rule=models['rule_all'],strong_linear=models[best]),strong_linear_name=best,inner_selection=choices))
            candidate.append(dict(**common,model=fit_pair(tr,y[a],target,'blind_pair',cfg,protocol)))
        baseline=OUT/f'baselines/{target}.json';baseline.write_text(dumps(dict(target=target,folds=reference)))
        package=dict(version='compact-development-v1',target=target,development_lock_sha256=sha256(OUT/'development-lock.json'),
          method='existing data-selected two-feature ridge; positive control, not a new method',folds=candidate,metrics=summarize(frame,target,candidate,reference))
        path=OUT/f'candidates/{target}.json';path.write_text(dumps(package))
        cards.append(dict(target=target,candidate=str(path.relative_to(ROOT)),baseline=str(baseline.relative_to(ROOT)),baseline_sha256=sha256(baseline),metrics=package['metrics'],seconds=time.perf_counter()-start))
        print(target,'skill vs strong linear',round(package['metrics']['skill_vs']['strong_linear'],4),flush=True)
    (OUT/'portfolio.json').write_text(dumps(dict(version=1,targets=cards,scope='12 targets, one seed x five outer folds on historical development identities. Baseline family/hyperparameters chosen inside each training fold. No new confirmation results.')))
    for c in cards:verify(ROOT/c['candidate'])
    print('PASS',len(cards),'candidate packages')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','verify','propose']);p.add_argument('--candidate');p.add_argument('--target');p.add_argument('--output');p.add_argument('--refit',action='store_true');a=p.parse_args()
    if a.action=='build':build()
    elif a.action=='propose':
        if not a.target or not a.output:p.error('--target and --output required')
        propose(a.target,a.output)
    else:
        if not a.candidate:p.error('--candidate required')
        print(dumps(verify(a.candidate,a.refit)))
if __name__=='__main__':main()
