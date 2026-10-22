"""Meaningful controls for cohort composition, coverage and outcome isolation."""
import builtins
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import support_diagnostic as diagnostic


def frame(labels, prefix):
    return pd.DataFrame({'lineage': labels, 'model_id': [f'{prefix}{i}' for i in range(len(labels))],
                         'group': [f'{prefix}{i}' for i in range(len(labels))]})


def test_composition_only_shift_has_zero_within_lineage_component():
    old = frame(['A'] * 90 + ['B'] * 10, 'old')
    new = frame(['A'] * 10 + ['B'] * 90, 'new')
    d = diagnostic.lineage_decomposition(old, new, old.lineage == 'A', new.lineage == 'A', 100, 7)
    assert d['common_total_shift'] == pytest.approx(-.8)
    assert d['composition_component'] == pytest.approx(-.8)
    assert d['within_lineage_component'] == pytest.approx(0.)
    assert d['composition_reference_count_interval95'] == [10., 10.]
    assert d['outside_reference_interval'] is False


def test_within_lineage_shift_not_misattributed_to_composition():
    old = frame(['A'] * 50 + ['B'] * 50, 'old')
    new = frame(['A'] * 50 + ['B'] * 50, 'new')
    d = diagnostic.lineage_decomposition(old, new, np.arange(100) % 2 == 0, np.ones(100, bool), 500, 7)
    assert d['composition_component'] == pytest.approx(0.)
    assert d['within_lineage_component'] == pytest.approx(.5)
    assert d['composition_reference_expected_left_count'] == 50.
    assert d['outside_reference_interval'] is True


def test_unmatched_lineages_are_explicit_and_not_imputed():
    old = frame(['A'] * 8, 'old')
    new = frame(['A'] * 4 + ['C'] * 2, 'new')
    d = diagnostic.lineage_decomposition(old, new, [1, 0] * 4, [1, 0] * 3, 100, 7)
    assert d['external_common_n'] == 4
    assert d['external_unmatched_ids'] == ['new4', 'new5']
    assert d['composition_reference_expected_left_count'] == 2.
    with pytest.raises(ValueError, match='No shared lineage'):
        diagnostic.lineage_decomposition(old, frame(['Z'], 'z'), [1] * 8, [1], 10, 1)


def synthetic():
    old, new = frame(['A'] * 8, 'old'), frame(['A'] * 6, 'new')
    old['expr:GENE'] = np.arange(8, dtype=float)
    new['expr:GENE'] = np.arange(6, dtype=float)
    frozen = {'protocol': {'predictors': ['GENE'], 'targets': ['TARGET']},
              'targets': {'TARGET': {'models': {'rule_expression': {'kind': 'rule', 'features': ['expr:GENE'],
                  'medians': [3.5], 'threshold': 3.5, 'support_train': [4, 4]}}}}}
    protocol = {'minimum_rule_branch_units': 2, 'bootstrap_replicates': 50, 'bootstrap_seed': 7,
                'minimum_lineage_training_units_for_flag': 10}
    return old, new, frozen, protocol


def test_outcomes_do_not_change_diagnostic_and_id_errors_fail():
    old, new, frozen, protocol = synthetic()
    expected = diagnostic.analyze(old, new, frozen, protocol)
    old['y:TARGET'] = np.arange(len(old))
    new['y:TARGET'] = -np.arange(len(new))
    assert diagnostic.analyze(old, new, frozen, protocol) == expected
    new.loc[1, 'group'] = new.loc[0, 'group']
    with pytest.raises(ValueError, match='Duplicate external'):
        diagnostic.analyze(old, new, frozen, protocol)
    old, new, frozen, protocol = synthetic()
    frozen['targets']['TARGET']['models']['rule_expression']['support_train'] = [3, 5]
    with pytest.raises(ValueError, match='training support mismatch'):
        diagnostic.analyze(old, new, frozen, protocol)


def test_real_diagnostic_never_opens_response_or_sanger_files(monkeypatch):
    raw = diagnostic.ROOT / 'data/raw/transfer-trial-20261021'
    if not (raw / 'next_gen_expression.csv').exists():
        pytest.skip('Optional local publisher expression matrix unavailable')
    original_open, original_path_open = builtins.open, Path.open
    opened = []

    def check(path):
        if isinstance(path, (str, Path)):
            text = str(path)
            assert 'screen_gene_effect.csv' not in text
            assert 'sanger' not in text.lower()
            assert 'data/panel/' not in text
            assert not text.endswith('/results.json')
            opened.append(text)

    def guarded_open(path, *args, **kwargs):
        check(path)
        return original_open(path, *args, **kwargs)

    def guarded_path_open(path, *args, **kwargs):
        check(path)
        return original_path_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', guarded_open)
    monkeypatch.setattr(Path, 'open', guarded_path_open)
    result = diagnostic.compute(raw)
    assert len(result['features']) == 30 and len(result['rules']) == 12
    assert result['training_n'] == 773 and result['external_n'] == 77
    assert any('next_gen_expression.csv' in p for p in opened)
