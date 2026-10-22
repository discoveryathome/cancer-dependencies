from unittest.mock import patch

import pytest

import qualification as q


def test_transitive_aliases_and_grouping():
    records = [
        {'ModelID': 'old', 'StrippedCellLineName': 'HCMABC1', 'PatientID': 'patient1'},
        {'ModelID': 'new', 'Cell Line Name': 'HCM-ABC-1'},
        {'ModelID': 'second', 'PatientID': 'patient1'},
        {'sample_ID': 'sanger1', 'individual_group': 'sanger-person'},
        {'sample_ID': 'sanger2', 'individual_group': 'sanger-person', 'Alias': 'HCM-ABC-1'},
        {'sample_ID': 'unrelated', 'Alias': 'NA', 'PatientID': ''},
        {'sample_ID': 'unrelated2', 'Alias': None},
    ]
    groups, edges = q.connected(records)
    assert len(set(groups[:5])) == 1
    assert groups[5] != groups[6] != groups[0]
    assert len(edges) == 4


def test_flags_fail_closed_and_duplicate_records_rejected():
    assert q.truth('TRUE') and q.truth('Yes')
    assert not q.truth('FALSE')
    for value in ('', None, 'Maybe', '0', 0, 1):
        with pytest.raises(ValueError):
            q.truth(value)
    with pytest.raises(ValueError):
        q.unique_index([{'id': 'one'}, {'id': 'one'}], 'id')


def test_audit_never_reads_response_or_feature_matrices():
    original = q.Path.open
    allowed = {
        q.OUT / 'source-lock.json', q.ROOT / 'data/model-metadata.csv',
        q.ROOT / 'research/readiness-20261021/sources/Model.csv',
        *list((q.OUT / 'sources').iterdir()),
    }

    def guarded(path, *args, **kwargs):
        assert path in allowed, f'Unexpected audit I/O: {path}'
        return original(path, *args, **kwargs)

    with patch.object(q.Path, 'open', guarded):
        result = q.audit()
    assert not result['confirmation_ready']
    # Every selected Sanger component is absent from the entire Broad metadata set
    # and historical release, and cannot have the publisher overlap flag.
    representatives = set(result['sanger_provisional_reserve']['component_representatives'])
    for row in result['sanger_records']:
        if row['sample_id'] in representatives:
            assert not any(row[k] for k in ('old_identity_overlap', 'broad_identity_overlap', 'broad_flagged_overlap'))
    assert result['sanger_provisional_reserve']['identity_components'] < result['sanger_provisional_reserve']['models']
    broad_representatives = set(result['broad_provisional_reserve']['component_representatives'])
    assert 'ACH-003722' not in broad_representatives  # Publisher marks non-cancerous adenoma.
    assert all(r['annotation_eligible'] for r in result['broad_records'] if r['model_id'] in broad_representatives)


def test_changed_input_is_rejected():
    original = q.digest

    def altered(path):
        return '0' * 64 if path.name == 'broad-aliases.json' else original(path)

    with patch.object(q, 'digest', altered), pytest.raises(ValueError, match='Changed audit input'):
        q.verify_sources()
