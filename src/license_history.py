"""Resolve only the exact non-scientific documents superseded by license notices."""
import hashlib
from pathlib import Path

# Immutable versions from 730abd211ea8438c42efb6404cb2a465464efd60.
# Scientific source, inputs, results and manifests must never be added here.
SNAPSHOTS = {
    'DATA_LICENSE.md': '83b78613340a45b2fe34140e8512c0d7e4053e46e8fae31c99fa51009cca9491',
    'README.md': '4feb06fe6d1f76387862e27daee2d1dda8640bbc12ba1242e4ce37b270d1b058',
    'QUICKSTART.md': '05252fcd2b47088a267f474393a24adb4e0f5e911379946da8402cee967913f8',
    'src/check_history.py': 'ba39c4a32a03d7454148ad77ebb32d73609831f6d549703f57f3e985c24e46c9',
    'research/program-v2-20261021/check_manifest.py': 'b071bb54a19bdd715c4dfcb06af0fe56ce44fc1ec12237967d4f63f73d3b8854',
}


def evidence_path(root: Path, name: str, expected: str) -> Path:
    """Unrecognized hashes/paths always resolve to the actual current file."""
    if name not in SNAPSHOTS or expected != SNAPSHOTS[name]:
        return root / name
    path = root / 'research/license-20261022/historical' / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Changed license-history snapshot: ' + name)
    return path
