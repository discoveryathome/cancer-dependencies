"""License documentation updates must not weaken evidence verification."""
import hashlib
from pathlib import Path

import pytest

from license_history import SNAPSHOTS, evidence_path


def test_all_archived_versions_are_byte_identical():
    root = Path(__file__).resolve().parents[1]
    for name, expected in SNAPSHOTS.items():
        assert hashlib.sha256(evidence_path(root, name, expected).read_bytes()).hexdigest() == expected


def test_unknown_versions_and_scientific_files_are_never_redirected(tmp_path):
    assert evidence_path(tmp_path, 'DATA_LICENSE.md', 'different-version') == tmp_path / 'DATA_LICENSE.md'
    digest = SNAPSHOTS['DATA_LICENSE.md']
    assert evidence_path(tmp_path, 'src/transfer_trial.py', digest) == tmp_path / 'src/transfer_trial.py'
    assert evidence_path(tmp_path, 'research/wide-expression-20261021/results.json', digest) == tmp_path / 'research/wide-expression-20261021/results.json'


def test_tampered_snapshot_fails(tmp_path):
    path = tmp_path / 'research/license-20261022/historical/DATA_LICENSE.md'
    path.parent.mkdir(parents=True)
    path.write_text('tampered')
    with pytest.raises(ValueError, match='Changed license-history snapshot'):
        evidence_path(tmp_path, 'DATA_LICENSE.md', SNAPSHOTS['DATA_LICENSE.md'])
