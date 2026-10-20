"""Read-only task orientation; never displays final-test performance."""
import argparse,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('mode',choices=['audit','trial','target']);p.add_argument('--target');a=p.parse_args()
if a.mode=='audit':
 d=json.loads((ROOT/'reports/data_audit.json').read_text())
 print(json.dumps({k:d[k] for k in ['Avana','KY','distinct_sanger_groups','overlapping_sanger_groups','split_counts','feature_count','caveat']},indent=2))
 print('Open: novelty review, normal-cell selectivity, upstream preprocessing, assay-specific artifacts.')
else:
 d=json.loads((ROOT/'research/contributor-trial/protocol.json').read_text())
 if a.mode=='target':
  if a.target not in d['pairs']:raise SystemExit('Choose a target in config/benchmark.json')
  print(json.dumps({'target':a.target,'literature_pair':d['pairs'][a.target],
    'next_command':['.venv/bin/python','src/contribute.py','run','--target',a.target,'--artifact','research/my-attempt/RESULT.json'],
    'evaluation':'Development only; every new confirmation requires a fresh cohort after public final-test inspection.'},indent=2))
 else:
  print(json.dumps({'candidate':d['primary_family'],'control':d['control_family'],'pairs':d['pairs'],'primary_comparison':d['primary_comparison']},indent=2))
  print('Development outputs: research/contributor-trial/outer_metrics.csv. Final scores deliberately not displayed.')
