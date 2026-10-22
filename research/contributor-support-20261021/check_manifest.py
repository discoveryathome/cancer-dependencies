"""Verify the local contributor artifact and its historical input bindings."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((HERE / 'manifest.json').read_text())
for name, expected in manifest['files'].items():
    with (ROOT / name).open('rb') as handle:
        actual = hashlib.file_digest(handle, 'sha256').hexdigest()
    if actual != expected:
        raise SystemExit(f'FAIL changed contributor evidence: {name}')
print(f"PASS {len(manifest['files'])} contributor/input hashes; author-checked, scientific acceptance pending")
