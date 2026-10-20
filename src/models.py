"""Training-only preprocessing, finite rule search, and nested baseline selection."""
import warnings
import numpy as np
from sklearn.linear_model import Ridge, ElasticNet, LinearRegression
from core import predict

def splits(frame,k,seed):
    groups=np.array(sorted(frame.group.unique())); np.random.default_rng(seed).shuffle(groups)
    for test in np.array_split(groups,k):
        mask=frame.group.isin(test).to_numpy()
        yield np.flatnonzero(~mask),np.flatnonzero(mask)

def preprocess(frame,features):
    x=frame[features].to_numpy(float)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        med=np.nanmedian(x,axis=0)
    med=np.nan_to_num(med,nan=0.0)
    return np.where(np.isnan(x),med,x),med

def mean(y): return {'kind':'constant','value':float(np.mean(y)),'complexity':{'parameters':1,'molecular_features':0}}

def lineage(frame,y,cfg):
    fallback=float(np.mean(y)); labels=frame.lineage.to_numpy(); s=cfg['lineage_shrinkage']
    means={l:float((np.sum(y[labels==l])+s*fallback)/(np.sum(labels==l)+s)) for l in sorted(set(labels))}
    return {'kind':'lineage','means':means,'fallback':fallback,'shrinkage':s,
            'complexity':{'parameters':len(means)+1,'molecular_features':0,'lineage_levels':len(means)}}

def features_for(frame,modality):
    prefix={'expr':('expr:',),'cn':('cn:',),'mut':('damaging:','hotspot:'),
            'all':('expr:','cn:','damaging:','hotspot:')}[modality]
    return sorted(c for c in frame if c.startswith(prefix))

def rule_grid(frame,cfg):
    return [(f,q) for f in features_for(frame,'all') for q in
            ([None] if f.startswith(('damaging:','hotspot:')) else cfg['rule_quantiles'])]

def rule_bank(train,y,test,grid,cfg):
    features=list(dict.fromkeys(f for f,q in grid)); x,med=preprocess(train,features)
    xt=test[features].to_numpy(float); xt=np.where(np.isnan(xt),med,xt)
    ids=np.array([features.index(f) for f,q in grid])
    thresholds=np.array([.5 if q is None else np.quantile(x[:,i],q) for i,(f,q) in zip(ids,grid)])
    left=x[:,ids]<=thresholds; n=left.sum(axis=0); right_n=len(y)-n
    valid=(n>=cfg['min_leaf'])&(right_n>=cfg['min_leaf'])
    yl=(left.T@y)/np.maximum(n,1); yr=(np.sum(y)-left.T@y)/np.maximum(right_n,1)
    yl=np.where(valid,yl,np.mean(y)); yr=np.where(valid,yr,np.mean(y))
    preds=np.where(xt[:,ids]<=thresholds,yl,yr)
    return preds,{'med':med[ids],'threshold':thresholds,'left':yl,'right':yr,'valid':valid,'n_left':n,'n_right':right_n}

def rule_select(train,y,cfg,cv=None):
    grid=rule_grid(train,cfg); cv=list(splits(train,cfg['inner_folds'],cfg['inner_seed'])) if cv is None else cv
    losses=np.zeros(len(grid)); valid=np.ones(len(grid),bool); baseline_loss=0.
    for a,b in cv:
        pred,params=rule_bank(train.iloc[a],y[a],train.iloc[b],grid,cfg)
        losses+=np.sum((y[b,None]-pred)**2,axis=0); valid &= params['valid']
        baseline_loss+=np.sum((y[b]-predict(lineage(train.iloc[a],y[a],cfg),train.iloc[b]))**2)
    losses/=len(y); baseline_loss/=len(y)
    _,params=rule_bank(train,y,train.iloc[:0],grid,cfg); valid &=params['valid']
    selections={}; details=[]
    for i,(feature,q) in enumerate(grid):
        details.append({'feature':feature,'quantile':q,'inner_mse':float(losses[i]),'valid_all_folds':bool(valid[i])})
    for modality in ['expr','cn','mut','all']:
        allowed=set(features_for(train,modality)); mask=valid&np.array([f in allowed for f,q in grid])
        if not mask.any():
            selections['rule_'+modality]=mean(y); continue
        index=int(np.argmin(np.where(mask,losses,np.inf))); f,q=grid[index]
        selections['rule_'+modality]={'kind':'rule','features':[f],'quantile':q,'medians':[float(params['med'][index])],
            'threshold':float(params['threshold'][index]),'left':float(params['left'][index]),'right':float(params['right'][index]),
            'support_train':[int(params['n_left'][index]),int(params['n_right'][index])],
            'complexity':{'molecular_features':1,'thresholds':1,'leaves':2,'parameters':3,'imputation_parameters':1},
            'inner_mse':float(losses[index])}
    # Score the selection procedure under the same inner-CV objective, including null reruns.
    best=float(np.min(losses[valid])) if valid.any() else float(np.var(y))
    return selections,details,float(baseline_loss-best)

def linear_fit(train,y,features,kind,alpha=0,cfg=None):
    x,med=preprocess(train,features); center=x.mean(axis=0); scale=x.std(axis=0); scale[scale<1e-12]=1
    z=(x-center)/scale
    estimator=LinearRegression() if kind=='self' else (Ridge(alpha=alpha) if kind=='ridge' else
              ElasticNet(alpha=alpha,l1_ratio=cfg['elastic_l1_ratio'],max_iter=10000,tol=1e-7,selection='cyclic'))
    estimator.fit(z,y)
    coef=np.asarray(estimator.coef_)
    return {'kind':'linear','features':features,'medians':med.tolist(),'center':center.tolist(),'scale':scale.tolist(),
        'coef':coef.tolist(),'intercept':float(estimator.intercept_),'alpha':alpha,'estimator':kind,
        'complexity':{'parameters':int(np.count_nonzero(abs(coef)>1e-12))+1,
                      'molecular_features':int(np.count_nonzero(abs(coef)>1e-12)),
                      'preprocessing_features':len(features),'preprocessing_parameters':3*len(features)}}

def fit_models(train,y,target,cfg):
    cv=list(splits(train,cfg['inner_folds'],cfg['inner_seed']))
    models,search,stat=rule_select(train,y,cfg,cv)
    models.update({'mean':mean(y),'lineage':lineage(train,y,cfg),
                   'self_expression':linear_fit(train,y,['expr:'+target],'self')})
    tuning=[]
    for kind in ['ridge','elastic']:
        for modality in ['expr','all']:
            feats=features_for(train,modality); candidates=[]
            for alpha in cfg[kind+'_alphas']:
                loss=0.
                for a,b in cv:
                    m=linear_fit(train.iloc[a],y[a],feats,kind,alpha,cfg)
                    loss+=np.sum((y[b]-predict(m,train.iloc[b]))**2)
                candidates.append((float(loss/len(y)),alpha))
                tuning.append({'model':kind+'_'+modality,'alpha':alpha,'inner_mse':float(loss/len(y))})
            _,alpha=min(candidates)
            models[kind+'_'+modality]=linear_fit(train,y,feats,kind,alpha,cfg)
    return models,{'rules':search,'linear':tuning,'observed_permutation_statistic':stat,
                   'rule_candidate_count':len(search),'inner_folds':len(cv)}
