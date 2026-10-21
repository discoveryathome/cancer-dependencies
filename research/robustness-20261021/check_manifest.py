"""Check frozen robustness artifacts and optional local publisher input hashes."""
import argparse
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

parser=argparse.ArgumentParser(); parser.add_argument('--raw',action='store_true'); args=parser.parse_args()
m=json.loads((HERE/'manifest.json').read_text())
for name,h in m['files'].items():
    if digest(ROOT/name)!=h: raise SystemExit('FAIL changed artifact '+name)
if args.raw:
    for name,h in m['raw_files'].items():
        if digest(ROOT/name)!=h: raise SystemExit('FAIL changed raw input '+name)
    print(f"PASS {len(m['raw_files'])} local raw input hashes")
print(f"PASS {len(m['files'])} robustness/input hashes; author-checked, scientific review pending")
