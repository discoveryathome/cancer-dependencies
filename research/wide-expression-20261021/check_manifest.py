"""Verify this package's committed evidence and optional local raw inputs."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
m=json.loads((HERE/'manifest.json').read_text())
for name,want in {**m['files'],**(m.get('raw_files',{}) if a.raw else {})}.items():
    with (ROOT/name).open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=want:raise SystemExit('FAIL changed evidence '+name)
print('PASS',len(m['files']),'artifact hashes',('and '+str(len(m.get('raw_files',{})))+' raw hashes') if a.raw else '')
