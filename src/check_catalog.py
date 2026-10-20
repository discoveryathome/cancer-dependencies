"""Run every documented first step and preserve its actual output."""
import json,pathlib,subprocess
from core import dumps
ROOT=pathlib.Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'discover/catalog.json').read_text());rows=[]
for track in d['tracks']:
    for card in track['tasks']:
        command=card['first_step']['command'];r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=180)
        rows.append({'card':card['id'],'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:raise SystemExit(card['id']+': '+r.stdout+r.stderr)
        print('PASS:',card['id'],flush=True)
(ROOT/'setup/logs/catalog-first-steps.json').write_text(dumps(rows))
print('PASS:',len(rows),'catalogue first steps.')
