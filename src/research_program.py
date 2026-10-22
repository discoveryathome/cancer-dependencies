"""Read-only task routing and declaration validation; not scientific approval."""
import argparse
import json
from pathlib import Path
import secrets
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['question','intended_decision','hypothesis','data_and_cohort','targets','baseline','metrics','search_space','budget','exposure_status','evaluation_plan','success_and_failure','outside_review']

def proposal(d):
    for field in REQUIRED:
        if not isinstance(d.get(field),str) or not d[field].strip(): raise ValueError('Missing declaration: '+field)
    if d.get('track') not in ['comparable-improvements','exploration']: raise ValueError('Unknown track')
    if d.get('status') not in ['example','proposed','frozen']: raise ValueError('Unknown proposal status')
    return {'valid_declarations':True,'status':d['status'],'scientific_approval':False}

def check():
    catalog=json.loads((ROOT/'discover/catalog.json').read_text())
    Draft202012Validator(json.loads((ROOT/'setup/sources/catalog.schema.json').read_text())).validate(catalog)
    if sum(t['weight'] for t in catalog['tracks'])!=100: raise ValueError('Track weights must sum to100')
    seen=set()
    for track in catalog['tracks']:
        for card in track['tasks']:
            if card['id'] in seen: raise ValueError('Duplicate card')
            seen.add(card['id'])
            for path in card['starting_points']:
                if not (ROOT/path).is_file(): raise ValueError('Missing starting point '+path)
    proposal(json.loads((ROOT/'research/program-v2-20261021/proposal-example.json').read_text()))
    return {'cards':len(seen),'tracks':len(catalog['tracks']),'status':'Valid declarations; private pilot, review and intake pending'}

def choose(catalog,seed):
    if len(seed)!=32: raise ValueError('Seed must be32 hexadecimal characters')
    number=int(seed,16); slot=number%100; number//=100
    for track in catalog['tracks']:
        if slot<track['weight']:
            return {'seed':seed,'track':track['id'],'task':track['tasks'][number%len(track['tasks'])]}
        slot-=track['weight']
    raise ValueError('Invalid weights')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','pick','proposal']);p.add_argument('--seed');p.add_argument('--path',type=Path);a=p.parse_args()
    if a.action=='check':result=check()
    elif a.action=='pick':
        check();result=choose(json.loads((ROOT/'discover/catalog.json').read_text()),a.seed or secrets.token_hex(16))
    else:
        if not a.path:p.error('--path required')
        result=proposal(json.loads(a.path.read_text()))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
