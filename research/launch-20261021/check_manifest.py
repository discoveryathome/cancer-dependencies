"""Verify the program-v2 package against the current checkout, resolving launch snapshots.

The 2026-10-21 launch edited entry documents that research/program-v2-20261021/manifest.json
binds by hash. Their pre-launch bytes are kept in pre-launch-entry/. This check accepts a
bound file only if the live file or its pre-launch snapshot matches the recorded hash;
nothing else is resolved through the snapshots.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SNAPSHOTS = HERE / 'pre-launch-entry'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / 'research/program-v2-20261021/manifest.json').read_text())
    archived = 0
    for name, want in manifest['files'].items():
        if sha256(ROOT / name) == want:
            continue
        snapshot = SNAPSHOTS / name
        if snapshot.is_file() and sha256(snapshot) == want:
            archived += 1
            continue
        raise SystemExit('FAIL changed evidence ' + name)
    print(f'PASS program-v2: {len(manifest["files"])} hashes ({archived} from pre-launch snapshots)')


if __name__ == '__main__':
    main()
