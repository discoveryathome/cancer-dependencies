"""Strict reference-schema audit with one explicit local-proposal exception."""
import json,pathlib
from jsonschema import Draft202012Validator
ROOT=pathlib.Path(__file__).resolve().parents[1]
problems=[];known=[]
for data,schema in [('discover.json','manifest.schema.json'),('discover/frontier.json','frontier.schema.json'),('discover/catalog.json','catalog.schema.json')]:
    d=json.loads((ROOT/data).read_text());s=json.loads((ROOT/'setup/sources'/schema).read_text())
    for e in Draft202012Validator(s).iter_errors(d):
        if data=='discover.json' and list(e.path)==['maintainers'] and e.validator=='minItems' and d['maintainers']==[] and d['review']['paused'] and d['hubs']==[]:
            known.append('No appointed maintainer: reference manifest schema fails; local proposal only.')
        else: problems.append(data+': '+e.message)
for task in (ROOT/'research').glob('*/TASK.json'):
    schema=json.loads((ROOT/'setup/sources/package-task.schema.json').read_text())
    for e in Draft202012Validator(schema).iter_errors(json.loads(task.read_text())):problems.append(str(task)+': '+e.message)
cat=json.loads((ROOT/'discover/catalog.json').read_text());assert sum(t['weight'] for t in cat['tracks'])==100
for t in cat['tracks']:
    for c in t['tasks']:
        for p in c['starting_points']:
            if not (ROOT/p).exists():problems.append('Missing starting point '+p)
if problems:raise SystemExit('\n'.join(problems))
print('PASS: local files valid apart from explicitly disclosed maintainer prerequisite.')
for k in known:print('NOT DONOR-READY:',k)
