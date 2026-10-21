"""Separate SciPy arithmetic check of all corrected/uncorrected target metrics."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
freeze=json.loads((ROOT/'research/transfer-trial-20261021/run/frozen.json').read_text())
original=json.loads((ROOT/'research/transfer-trial-20261021/run/predictions.json').read_text())
corrected=json.loads((HERE/'predictions.json').read_text())
result=json.loads((HERE/'results.json').read_text())
source=json.loads((ROOT/'research/transfer-results-20261021/source-manifest.json').read_text())
raw=ROOT/'data/raw/transfer-trial-20261021'/source['response_file']
with raw.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==source['response_sha256']
ids={r['screen_id'] for r in original['rows']}; outcomes={}
with raw.open(newline='') as f:
    reader=csv.DictReader(f); idcol=reader.fieldnames[0]
    for row in reader:
        if row[idcol] in ids:
            assert row[idcol] not in outcomes
            outcomes[row[idcol]]={t:float(row[col]) for t,col in freeze['gene_map']['y'].items() if t in freeze['protocol']['targets']}
assert set(outcomes)==ids and len(ids)==77
checks=0
for variant,pred in [('uncorrected',original),('corrected',corrected)]:
    contrast=[]
    for target in freeze['protocol']['targets']:
        yy=np.array([outcomes[r['screen_id']][target] for r in pred['rows']]); assert np.isfinite(yy).all()
        reported=result[variant]['targets'][target]; assert reported['n']==77
        metrics={}
        for family,pp in pred['predictions'][target].items():
            pp=np.array(pp); rho=float(spearmanr(yy,pp).statistic) if np.ptp(pp)>0 else None
            stored=reported['models'][family]
            if rho is None: assert stored['spearman'] is None
            else: assert abs(rho-stored['spearman'])<1e-12
            assert abs(float(np.square(yy-pp).mean())-stored['mse_diagnostic'])<1e-12
            metrics[family]=rho; checks+=1
        contrast.append(metrics['compact_expression_pair']-metrics['strong_expression'])
        rule=freeze['targets'][target]['models']['rule_expression']; feature=rule['features'][0]
        count=sum(r[feature]<=rule['threshold'] for r in pred['rows'])
        assert reported['rule_branch_support']==[count,77-count]
    assert abs(np.mean(contrast)-result[variant]['primary']['estimate'])<1e-12
for target in freeze['protocol']['targets']:
    for family in ['compact_expression_pair','strong_expression','self_expression']:
        a=original['predictions'][target][family]; b=corrected['predictions'][target][family]
        assert np.array_equal(rankdata(a),rankdata(b))
assert result['uncorrected']['primary']==result['corrected']['primary']
print(f'PASS separate SciPy audit: {checks} target-family rho/MSE pairs,24 support counts,all77x12 outcomes,two aggregate endpoints,36 unchanged rankings')
