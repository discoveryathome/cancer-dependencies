"""Offline scaffold integrity; neither scoring nor scientific acceptance."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((HERE / 'manifest.json').read_text())
for name, expected in manifest['files'].items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'FAIL changed transfer scaffold: {name}')
print(f"PASS {len(manifest['files'])} transfer scaffold hashes; external scoring and scientific review pending")
