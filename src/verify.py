"""Recompute predictions and metrics; fail closed on tampering or train/test overlap."""
import argparse, json, pathlib
import numpy as np
import pandas as pd
from core import assert_disjoint, metrics, predict, sha256
ROOT=pathlib.Path(__file__).resolve().parents[1]

def verify(package, root=ROOT):
    package=pathlib.Path(package)
    d=json.loads(package.read_text())
    for name,expected in d['inputs'].items():
        p=(root/name).resolve()
        if not p.is_relative_to(root.resolve()): raise ValueError('Unsafe input path')
        if sha256(p)!=expected: raise ValueError('Input hash mismatch: '+name)
    f=pd.read_csv(root/d['frame'])
    if f.model_id.duplicated().any(): raise ValueError('Duplicate model identity')
    train=f[f.partition=='development']; test=f[f.partition=='final']
    assert_disjoint(train,test)
    if set(d['training_groups'])!=set(train.group): raise ValueError('Training identity manifest mismatch')
    if set(d['test_groups'])!=set(test.group): raise ValueError('Test identity manifest mismatch')
    count=0
    for row in d['results']:
        actual=test.set_index('model_id').loc[row['model_ids']].reset_index()
        if actual.model_id.duplicated().any(): raise ValueError('Duplicate predictions')
        col='y:'+row['target']
        eligible=test.loc[test[col].notna(),'model_id']
        if set(eligible)!=set(row['model_ids']): raise ValueError('Incomplete final cohort')
        p=predict(row['model'],actual); ref=predict(row['reference'],actual)
        if not np.allclose(p,row['predictions'],atol=1e-9,rtol=1e-8): raise ValueError('Prediction mismatch')
        for key,value in metrics(actual[col],p,ref).items():
            got=row['metrics'][key]
            if value is None:
                if got is not None: raise ValueError('Undefined metric mismatch')
            elif got is None or not np.isclose(value,got,atol=1e-9,rtol=1e-8):
                raise ValueError('Metric mismatch: '+key)
        count+=1
    if count==0: raise ValueError('Empty package')
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('package',nargs='?',default=str(ROOT/'research/initial/VERIFY.json'))
    a=p.parse_args(); print('PASS:',verify(a.package),'model/target results recomputed; hashes and identity separation verified.')
