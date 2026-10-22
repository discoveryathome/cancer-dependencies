"""Check the frozen preparation base before starting a contribution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).resolve().parent
manifest=json.loads((PACKAGE/'manifest.json').read_text())
for path,expected in manifest['files'].items():
    file=ROOT/path
    if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:
        raise ValueError('Preparation binding changed: '+path)
print('PASS',len(manifest['files']),'preparation file hashes; scientific acceptance remains pending')
