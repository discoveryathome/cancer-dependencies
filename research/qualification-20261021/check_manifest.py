"""Offline integrity check; does not confer scientific acceptance."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((HERE / 'manifest.json').read_text())
for name, expected in manifest['files'].items():
    path = ROOT / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'FAIL changed qualification artifact: {name}')
print(f"PASS {len(manifest['files'])} qualification hashes; scientific acceptance pending")
