"""Verify historical evidence, resolving only explicitly archived entry documents."""
import hashlib
import json
from pathlib import Path
from license_history import evidence_path
ROOT=Path(__file__).resolve().parents[1]
MIGRATION=ROOT/'research/program-v2-20261021/migration.json'
PACKAGES=['readiness','qualification','transfer-trial','transfer-results','contributor-support','robustness']

def check():
    migration=json.loads(MIGRATION.read_text())['archived_entries']
    allowed={'README.md','DISCOVERY.md','QUICKSTART.md','AGENTS.md','discover.json','discover/catalog.json','discover/priority-log.md'}
    if set(migration)!=allowed:raise ValueError('Migration may archive only declared entry documents')
    for name,record in migration.items():
        expected_path='research/program-v2-20261021/historical-entry/'+name
        if record['snapshot']!=expected_path:raise ValueError('Invalid snapshot path')
        if hashlib.sha256((ROOT/expected_path).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Changed entry snapshot '+name)
    for package in PACKAGES:
        manifest=json.loads((ROOT/f'research/{package}-20261021/manifest.json').read_text())
        archived=0
        for name,expected in manifest['files'].items():
            if name in migration:
                record=migration[name]
                if record['sha256'] != expected: raise ValueError('Unrecognized historical version: '+name)
                path=ROOT/record['snapshot']; archived+=1
            else: path=evidence_path(ROOT,name,expected)
            if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: raise ValueError('Changed historical evidence: '+name)
        print(f'PASS {package}: {len(manifest["files"])} hashes ({archived} explicit entry snapshots)')

if __name__=='__main__': check()
