import argparse,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('mode',choices=['audit','trial']); a=p.parse_args()
if a.mode=='audit':
 d=json.loads((ROOT/'reports/data_audit.json').read_text())
 print(json.dumps({k:d[k] for k in ['Avana','KY','distinct_sanger_groups','overlapping_sanger_groups','split_counts','feature_count','caveat']},indent=2))
 print('Open: novelty review, normal-cell selectivity, upstream preprocessing, assay-specific artifacts.')
else:
 d=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())
 print(json.dumps({'candidate':d['primary_family'],'control':d['control_family'],'pairs':d['pairs'],'primary_comparison':d['primary_comparison']},indent=2))
 f=ROOT/'research/contributor-trial/summary.json'
 print(f.read_text() if f.exists() else 'Trial validation pending; no outcome claimed.')
