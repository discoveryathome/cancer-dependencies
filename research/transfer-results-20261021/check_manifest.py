"""Check committed result provenance and optionally the local publisher inputs."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--inputs', type=Path)
args = parser.parse_args()
manifest = json.loads((HERE / 'manifest.json').read_text())
for name, expected in manifest['files'].items():
    if digest(ROOT / name) != expected:
        raise SystemExit(f'FAIL changed result/provenance: {name}')
if args.inputs:
    source = json.loads((HERE / 'source-manifest.json').read_text())
    for filename, expected in [(source['expression_file'], source['expression_sha256']),
                               (source['response_file'], source['response_sha256']),
                               ('README.txt', source['readme_sha256'])]:
        path = args.inputs / filename
        if path.stat().st_size != source['file_bytes'][filename] or digest(path) != expected:
            raise SystemExit(f'FAIL changed publisher input: {filename}')
    print('PASS all three exact local publisher input hashes and byte counts')
print(f"PASS {len(manifest['files'])} result/provenance hashes; scientific review pending")
