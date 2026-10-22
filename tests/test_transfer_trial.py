"""Synthetic negative controls. None of these fixtures is new biological evidence."""
import copy
import csv
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from scipy.stats import spearmanr

import transfer_trial as t


def csv_file(path, header, rows):
    with path.open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def fixture(tmp_path):
    n = 40
    cohort = [{'model_id': f'ACH-{i:06}', 'screen_id': f'SC-{i:06}.CD01',
               'group': f'identity-{i}', 'lineage': 'A' if i % 2 else 'B'} for i in range(n)]
    x = np.linspace(1, 5, n)
    features = tmp_path / 'next_gen_expression.csv'
    response = tmp_path / 'screen_gene_effect.csv'
    csv_file(features, ['ModelID', 'GENE (1)'], [[row['model_id'], value] for row, value in zip(cohort, x)])
    csv_file(response, ['ScreenID', 'TARGET (2)'], [[row['screen_id'], -value] for row, value in zip(cohort, x)])
    linear = {'kind': 'linear', 'features': ['expr:GENE'], 'medians': [3.], 'center': [0.],
              'scale': [1.], 'coef': [-1.], 'intercept': 0.}
    models = {family: copy.deepcopy(linear) for family in t.FAMILIES}
    models['mean'] = {'kind': 'constant', 'value': 0.}
    models['lineage'] = {'kind': 'lineage', 'means': {'A': -.5, 'B': -1.}, 'fallback': 0.}
    models['rule_expression'] = {'kind': 'rule', 'features': ['expr:GENE'], 'medians': [3.],
                                 'threshold': 3., 'left': -2., 'right': -4.}
    frozen = {'schema': 'expression-transfer-freeze/v1', 'bindings': {},
              'protocol': {'targets': ['TARGET'], 'predictors': ['GENE'], 'minimum_external_units': 30,
                           'minimum_rule_branch_units': 15, 'bootstrap_seed': 17, 'bootstrap_replicates': 50},
              'cohort': cohort, 'targets': {'TARGET': {'models': models}},
              'gene_map': {'expr': {'GENE': 'GENE (1)'}, 'y': {'TARGET': 'TARGET (2)'}}}
    t.write_new(tmp_path / 'frozen.json', frozen)
    source = {'release': 'NextGen Model Manuscript 2026', 'expression_file': features.name,
              'response_file': response.name, 'expression_sha256': t.sha256(features), 'response_sha256': t.sha256(response),
              'expression_units': 'log2(TPM+1)', 'response_units': 'Chronos gene effect',
              'expression_row_id': 'ModelID', 'response_row_id': 'ScreenID',
              'source_url': 'https://example.invalid/synthetic-test-only',
              'terms_url': 'https://example.invalid/synthetic-test-only',
              'terms_status': 'reviewed-for-local-research',
              'notes': 'TEST DOUBLE ONLY; does not represent publisher data or actual license review'}
    manifest = tmp_path / 'source.json'
    t.write_new(manifest, source)
    return frozen, features, response, manifest


def test_rank_metric_matches_independent_scipy_with_ties_and_missing():
    y = np.array([[1, 2, 2, 4, np.nan], [2, 4, 1, 1, 3]], float)
    p = np.array([[5, 3, 3, 1, 0], [1, np.nan, 2, 2, 0]], float)
    result = t.spearman_rows(y, p)
    for i in range(2):
        mask = np.isfinite(y[i]) & np.isfinite(p[i])
        assert result[i] == pytest.approx(spearmanr(y[i, mask], p[i, mask]).statistic)
    assert np.isnan(t.spearman_rows([[1, 2, 3]], [[7, 7, 7]])[0])
    assert np.isnan(t.spearman_rows([[1, 2]], [[2, 1]])[0])


def test_stable_gene_ids_duplicate_and_identity_rejection(tmp_path):
    path = tmp_path / 'matrix.csv'
    csv_file(path, ['ModelID', 'RENAMED (1)'], [['ACH-1', 2.]])
    selected, missing = t.matrix(path, ['OLD'], {'OLD': 'OLD (1)'}, {'ACH-1'})
    assert selected == {'ACH-1': {'OLD': 2.}} and missing == []
    csv_file(path, ['ModelID', 'OLD (1)', 'ALIAS (1)'], [['ACH-1', 2., 3.]])
    with pytest.raises(ValueError, match='Duplicate stable'):
        t.matrix(path, ['OLD'], {'OLD': 'OLD (1)'}, {'ACH-1'})
    csv_file(path, ['ModelID', 'OLD (1)'], [['ACH-1', 2.], ['ACH-1', 3.]])
    with pytest.raises(ValueError, match='duplicate matrix identity'):
        t.matrix(path, ['OLD'], {'OLD': 'OLD (1)'}, {'ACH-1'})


def test_prediction_lock_cannot_open_outcomes(tmp_path):
    _, _, response, manifest = fixture(tmp_path)
    original = Path.open

    def guarded(path, *args, **kwargs):
        assert path != response, 'Prediction phase accessed outcomes'
        return original(path, *args, **kwargs)

    with patch.object(Path, 'open', guarded):
        t.lock_predictions(tmp_path, tmp_path, manifest)
    assert not (tmp_path / 'exposure.json').exists()
    with pytest.raises(FileExistsError):
        t.lock_predictions(tmp_path, tmp_path, manifest)


def test_complete_pipeline_replay_and_forged_prediction_rejected(tmp_path):
    fixture(tmp_path)
    manifest = tmp_path / 'source.json'
    t.lock_predictions(tmp_path, tmp_path, manifest)
    t.score(tmp_path, tmp_path, manifest)
    result = t.read_json(tmp_path / 'results.json')
    assert result['primary']['complete']
    assert result['primary']['estimate'] == pytest.approx(0.)
    assert result['targets']['TARGET']['models']['mean']['spearman'] is None
    assert result['targets']['TARGET']['rule_branch_support'] == [20, 20]
    t.score(tmp_path, tmp_path, manifest, verify=True)
    with pytest.raises(ValueError, match='already opened'):
        t.score(tmp_path, tmp_path, manifest)
    p = t.read_json(tmp_path / 'predictions.json')
    p['predictions']['TARGET']['compact_expression_pair'][0] += 1
    (tmp_path / 'predictions.json').write_text(json.dumps(p))
    with pytest.raises(ValueError, match='arithmetic replay'):
        t.score(tmp_path, tmp_path, manifest, verify=True)


def test_source_change_and_wrong_units_fail_before_exposure(tmp_path):
    _, _, response, manifest = fixture(tmp_path)
    source = t.read_json(manifest)
    source['expression_units'] = 'TPM'
    manifest.write_text(json.dumps(source))
    with pytest.raises(ValueError, match='measurement scale'):
        t.lock_predictions(tmp_path, tmp_path, manifest)
    source['expression_units'] = 'log2(TPM+1)'
    manifest.write_text(json.dumps(source))
    t.lock_predictions(tmp_path, tmp_path, manifest)
    response.write_text(response.read_text() + '\n')
    with pytest.raises(ValueError, match='Source bytes changed'):
        t.score(tmp_path, tmp_path, manifest)
    assert not (tmp_path / 'exposure.json').exists()


def test_missing_features_fail_and_rows_are_explicitly_excluded(tmp_path):
    frozen, features, _, _ = fixture(tmp_path)
    csv_file(features, ['ModelID', 'OTHER (99)'], [['ACH-000000', 1.]])
    with pytest.raises(ValueError, match='Missing expression gene columns'):
        t.build_predictions(frozen, features)
    csv_file(features, ['ModelID', 'GENE (1)'], [[r['model_id'], 1.] for r in frozen['cohort'][:-1]])
    predicted = t.build_predictions(frozen, features)
    assert len(predicted['rows']) == 39 and len(predicted['excluded']) == 1
    # Missing outcomes cannot silently remove a target from the primary average.
    response = tmp_path / 'screen_gene_effect.csv'
    csv_file(response, ['ScreenID', 'OTHER (99)'], [[r['screen_id'], -1.] for r in predicted['rows']])
    result = t.evaluate(frozen, predicted, response)
    assert result['primary']['complete'] is False
    assert result['primary']['estimate'] is None
    assert result['targets']['TARGET']['missing_target_column']


def test_changed_source_binding_and_incomplete_manifest(tmp_path):
    _, _, _, manifest = fixture(tmp_path)
    with pytest.raises(ValueError, match='Changed frozen'):
        t.check_bindings({'src/transfer_trial.py': '0' * 64})
    source = t.read_json(manifest)
    source['terms_status'] = 'pending'
    manifest.write_text(json.dumps(source))
    with pytest.raises(ValueError, match='Incomplete'):
        t.source_manifest(manifest)


def test_duplicate_recorded_group_blocks_prediction(tmp_path):
    frozen, features, _, _ = fixture(tmp_path)
    frozen['cohort'][1]['group'] = frozen['cohort'][0]['group']
    with pytest.raises(ValueError, match='Duplicate external'):
        t.build_predictions(frozen, features)
