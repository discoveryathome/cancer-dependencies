"""Serializable prediction and evaluation primitives; no executable model artifacts."""
import hashlib, json
import numpy as np


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()


def dumps(obj):
    return json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n'


def predict(model, frame):
    kind=model['kind']
    if kind=='constant': return np.full(len(frame),model['value'])
    if kind=='lineage':
        return np.array([model['means'].get(str(x),model['fallback']) for x in frame.lineage])
    features=model['features']
    if any(not x.startswith(('expr:','cn:','damaging:','hotspot:')) for x in features):
        raise ValueError('Only prespecified molecular features are permitted')
    x=frame[features].to_numpy(float)
    x=np.where(np.isnan(x),np.asarray(model['medians']),x)
    if not np.isfinite(x).all(): raise ValueError('Non-finite features')
    if kind=='rule': return np.where(x[:,0]<=model['threshold'],model['left'],model['right'])
    if kind=='linear': return model['intercept']+((x-model['center'])/model['scale'])@np.asarray(model['coef'])
    raise ValueError('Unknown model kind')


def metrics(y,p,reference=None):
    y=np.asarray(y); p=np.asarray(p)
    assert len(y)==len(p) and len(y)>0 and np.isfinite(y).all() and np.isfinite(p).all()
    mse=float(np.mean((y-p)**2)); var=float(np.var(y))
    out={'n':len(y),'mse':mse,'mae':float(np.mean(abs(y-p))),
         'r2':1-mse/var if var>1e-15 else None,
         'pearson':float(np.corrcoef(y,p)[0,1]) if np.std(p)>1e-12 and np.std(y)>1e-12 else None}
    if reference is not None:
        ref=float(np.mean((y-np.asarray(reference))**2))
        out['skill']=1-mse/ref if ref>1e-15 else None
        out['mse_improvement']=ref-mse
    return out


def assert_disjoint(a,b):
    overlap=set(a.group)&set(b.group)
    if overlap: raise ValueError('Biological identity leakage: '+str(sorted(overlap)[:5]))


def bh(p):
    p=np.asarray(p,float); order=np.argsort(p); out=np.empty(len(p))
    out[order]=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1].clip(0,1)
    return out


def bootstrap(y,p,ref,groups,seed,n=2000):
    # Cluster resample, keeping all rows from a biological identity together.
    y=np.asarray(y); p=np.asarray(p); ref=np.asarray(ref); groups=np.asarray(groups)
    unique=np.unique(groups); sums=[]
    for g in unique:
        k=groups==g
        sums.append([np.sum((y[k]-p[k])**2),np.sum((y[k]-ref[k])**2)])
    sums=np.asarray(sums); rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(unique),size=(n,len(unique))); scores=sums[idx].sum(axis=1)
    vals=1-scores[:,0]/np.maximum(scores[:,1],1e-15)
    return [float(x) for x in np.quantile(vals,[.025,.975])]
