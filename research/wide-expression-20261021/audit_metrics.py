"""Separate arithmetic/coverage audit, no import of the trial implementation."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
m=json.loads((HERE/'models.json').read_text());p=json.loads((HERE/'predictions.json').read_text());r=json.loads((HERE/'results.json').read_text())
dev=pd.read_csv(ROOT/'research/readiness-20261021/development.csv').set_index('model_id')
checks=0;primary=[]
for target,row in m['targets'].items():
    ids=row['model_ids'];y=dev.loc[ids,'y:'+target].to_numpy(float)
    assert len(ids)==len(set(ids))==row['n']
    assert set(ids)==set(dev.index[dev['y:'+target].notna()])
    tests=[]
    for fold in row['folds']:
        assert not set(fold['train_groups']) & set(dev.loc[fold['test_ids'],'group'])
        tests.extend(fold['test_ids'])
        for scope,ledger in fold['selection'].items():
            validation=[]
            for inner in ledger['folds']:
                assert set(inner['train_groups'])<=set(fold['train_groups'])
                assert set(dev.loc[inner['test_ids'],'group'])<=set(fold['train_groups'])
                assert not set(inner['train_groups']) & set(dev.loc[inner['test_ids'],'group'])
                validation.extend(inner['test_ids'])
            expected=set(dev.index[dev.group.isin(fold['train_groups'])])
            assert len(validation)==len(set(validation)) and set(validation)==expected
        assert len(fold['models']['wide300']['features'])==300
        assert len(fold['models']['panel30']['features'])==30
    assert len(tests)==len(set(tests)) and set(tests)==set(ids)
    for scope,pred in row['oof_predictions'].items():
        expected=row['metrics'][scope];actual=float(spearmanr(y,pred).statistic)
        assert abs(actual-expected['spearman'])<1e-12
        assert abs(float(np.mean((y-np.array(pred))**2))-expected['mse'])<1e-12
        checks+=1
    primary.append(row['metrics']['wide300']['spearman']-row['metrics']['panel30']['spearman'])
assert abs(np.mean(primary)-m['primary_wide_minus_panel30'])<1e-12
freeze=json.loads((ROOT/'research/transfer-trial-20261021/run/frozen.json').read_text())
source=json.loads((ROOT/'research/transfer-results-20261021/source-manifest.json').read_text())
raw=ROOT/'data/raw/transfer-trial-20261021'/source['response_file']
with raw.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source['response_sha256']
ids={row['screen_id'] for row in p['rows']};outcomes={}
with raw.open(newline='') as f:
    reader=csv.DictReader(f);key=reader.fieldnames[0]
    for row in reader:
        if row[key] in ids:outcomes[row[key]]={t:float(row[freeze['gene_map']['y'][t]]) for t in m['targets']}
assert len(ids)==77 and set(outcomes)==ids
for target,models in p['predictions'].items():
    y=np.array([outcomes[row['screen_id']][target] for row in p['rows']]);assert np.isfinite(y).all()
    assert r['targets'][target]['n']==77
    for scope,values in models.items():
        expected=r['targets'][target]['models'][scope]
        assert abs(float(spearmanr(y,values).statistic)-expected['spearman'])<1e-12
        assert abs(float(np.mean((y-np.array(values))**2))-expected['mse'])<1e-12
        checks+=1
for scope,value in r['aggregate_spearman'].items():
    assert abs(np.mean([row['models'][scope]['spearman'] for row in r['targets'].values()])-value)<1e-12
print('PASS separate SciPy audit:',checks,'rho/MSE pairs; complete development folds, inner/outer identity isolation, all77x12 outcomes and aggregate scores')
