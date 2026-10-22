"""A newcomer can choose work while scientific acceptance remains pending."""
import json
from pathlib import Path

import pytest

import research_program as program
from license_history import LAUNCH_SNAPSHOTS, evidence_path


def test_open_prerelease_session_can_pick_a_task_without_scientific_acceptance():
    state = program.check()
    assert state['intake'] == 'open'
    assert state['scientific_acceptance'] == 'pending'
    manifest = json.loads((program.ROOT / 'discover.json').read_text())
    assert manifest['review']['paused'] is False
    assert manifest['maintainers']
    assert manifest['permissions']['open_prs'] is True
    catalog = json.loads((program.ROOT / 'discover/catalog.json').read_text())
    task = program.choose(catalog, '0123456789abcdef0123456789abcdef')
    assert task['task']['id']
    assert task['task']['starting_points']


def test_pinned_launch_snapshots_remain_verifiable():
    root = Path(__file__).resolve().parents[1]
    for name, expected in LAUNCH_SNAPSHOTS.items():
        assert evidence_path(root, name, expected).is_file()
        assert evidence_path(root, name, 'unknown-version') == root / name


def test_corrupt_launch_snapshot_is_rejected(tmp_path):
    path = tmp_path / 'research/launch-20261021/pre-launch-entry/AGENTS.md'
    path.parent.mkdir(parents=True)
    path.write_text('changed')
    with pytest.raises(ValueError, match='Changed license-history snapshot'):
        evidence_path(tmp_path, 'AGENTS.md', LAUNCH_SNAPSHOTS['AGENTS.md'])
