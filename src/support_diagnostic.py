"""Outcome-free diagnostic of frozen rule support under cohort transfer.

No response files, model fitting or threshold recalibration. All targets and panel
genes are retained. Resampling intervals are descriptive reference distributions,
not uncertainty intervals for causal effects or multiplicity-adjusted tests.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

from core import dumps, sha256
import transfer_trial as transfer

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/contributor-support-20261021'
RUN = ROOT / 'research/transfer-trial-20261021/run'


def describe(values):
    values = np.asarray(values, float)
    finite = values[np.isfinite(values)]
    return {'n': len(values), 'finite': len(finite), 'missing': int(np.isnan(values).sum()),
            'quantiles': dict(zip(('min', 'q05', 'q25', 'median', 'q75', 'q95', 'max'),
                                 np.quantile(finite, [0, .05, .25, .5, .75, .95, 1]).tolist()))
            if len(finite) else None}


def lineage_decomposition(train, external, train_left, external_left, replicates, seed):
    """Exact common-lineage decomposition and fixed-source composition reference."""
    train_left, external_left = np.asarray(train_left, bool), np.asarray(external_left, bool)
    if len(train) != len(train_left) or len(external) != len(external_left):
        raise ValueError('Branch/identity length mismatch')
    common = sorted(set(train.lineage) & set(external.lineage))
    train_common = train.lineage.isin(common).to_numpy()
    external_common = external.lineage.isin(common).to_numpy()
    if not train_common.any() or not external_common.any():
        raise ValueError('No shared lineage support')
    old_common_rate = float(train_left[train_common].mean())
    new_common_rate = float(external_left[external_common].mean())
    expected_count = 0.
    simulated_count = np.zeros(replicates, dtype=int)
    rng = np.random.default_rng(seed)
    tables = []
    for lineage in sorted(set(train.lineage) | set(external.lineage)):
        old = train_left[(train.lineage == lineage).to_numpy()]
        new = external_left[(external.lineage == lineage).to_numpy()]
        row = {'lineage': lineage, 'training_n': len(old), 'external_n': len(new),
               'training_left': int(old.sum()), 'external_left': int(new.sum()),
               'training_left_fraction': float(old.mean()) if len(old) else None,
               'external_left_fraction': float(new.mean()) if len(new) else None}
        if len(old) and len(new):
            expected_count += len(new) * float(old.mean())
            # Same deterministic row draws across rules preserve their correlation.
            draws = rng.integers(0, len(old), size=(replicates, len(new)))
            simulated_count += old[draws].sum(axis=1)
        tables.append(row)
    new_n = int(external_common.sum())
    mix_rate = expected_count / new_n
    interval = np.quantile(simulated_count, [.025, .975]).tolist()
    return {'lineages': tables, 'common_lineages': common,
            'training_common_n': int(train_common.sum()), 'external_common_n': new_n,
            'external_unmatched_ids': external.loc[~external_common, 'model_id'].tolist(),
            'training_full_left_fraction': float(train_left.mean()),
            'training_common_left_fraction': old_common_rate,
            'lineage_reweighted_training_left_fraction': float(mix_rate),
            'external_common_left_fraction': new_common_rate,
            'common_total_shift': new_common_rate - old_common_rate,
            'composition_component': mix_rate - old_common_rate,
            'within_lineage_component': new_common_rate - mix_rate,
            'composition_reference_expected_left_count': float(expected_count),
            'composition_reference_count_interval95': interval,
            'observed_common_left_count': int(external_left[external_common].sum()),
            'outside_reference_interval': not interval[0] <= int(external_left[external_common].sum()) <= interval[1],
            'reference_interpretation': 'Empirical old-cohort distributions fixed within exact lineage labels; descriptive only, no causal attribution or significance claim'}


def analyze(train, external, frozen, protocol):
    for name, frame in [('training', train), ('external', external)]:
        if frame.model_id.duplicated().any() or frame.group.duplicated().any():
            raise ValueError('Duplicate ' + name + ' identity')
        if frame.lineage.isna().any() or frame.model_id.isna().any():
            raise ValueError('Missing lineage/identity')
    if set(train.model_id) & set(external.model_id):
        raise ValueError('Known model identity overlap')
    rules, distributions = {}, {}
    for gene in frozen['protocol']['predictors']:
        key = 'expr:' + gene
        old, new = train[key].to_numpy(float), external[key].to_numpy(float)
        if np.isinf(old).any() or not np.isfinite(new).all() or np.any(new < 0):
            raise ValueError('Invalid expression values')
        a, b = describe(old), describe(new)
        if a['finite'] == 0:
            raise ValueError('No observed development expression')
        oldq, newq = a['quantiles'], b['quantiles']
        iqr = oldq['q75'] - oldq['q25']
        distributions[gene] = {'training': a, 'external': b,
            'external_outside_training_range': int(((new < oldq['min']) | (new > oldq['max'])).sum()),
            'median_shift_in_training_iqr': (newq['median'] - oldq['median']) / iqr if iqr > 0 else None}
    for target in frozen['protocol']['targets']:
        rule = frozen['targets'][target]['models']['rule_expression']
        if rule['kind'] != 'rule':
            rules[target] = {'kind': rule['kind'], 'support': 'No molecular threshold'}
            continue
        feature = rule['features'][0]
        old_values = train[feature].fillna(rule['medians'][0]).to_numpy(float)
        new_values = external[feature].to_numpy(float)
        old, new = old_values <= rule['threshold'], new_values <= rule['threshold']
        old_counts = [int(old.sum()), int((~old).sum())]
        if old_counts != rule['support_train']:
            raise ValueError('Frozen training support mismatch: ' + target)
        counts = [int(new.sum()), int((~new).sum())]
        decomposition = lineage_decomposition(train, external, old, new,
            protocol['bootstrap_replicates'], protocol['bootstrap_seed'])
        if not np.isclose(decomposition['common_total_shift'], decomposition['composition_component'] + decomposition['within_lineage_component'], atol=1e-14):
            raise ValueError('Decomposition identity failed')
        rules[target] = {'kind': 'rule', 'feature': feature, 'threshold': rule['threshold'],
                         'training_branch_counts': old_counts, 'external_branch_counts': counts,
                         'adequate_external_branches': min(counts) >= protocol['minimum_rule_branch_units'],
                         'constant_external_branch': min(counts) == 0, 'decomposition': decomposition}
    return {'schema': 'expression-support-diagnostic/v1', 'training_n': len(train),
            'external_n': len(external), 'features': distributions, 'rules': rules,
            'small_training_lineages': sorted(label for label, n in train.lineage.value_counts().items()
                if label in set(external.lineage) and n < protocol['minimum_lineage_training_units_for_flag']),
            'limitations': ['Outcome-free support audit; no predictive improvement tested.',
                           'Common-lineage decomposition is descriptive and cannot separate biology from assay processing.',
                           'Broad was already exposed; same author, no independent confirmation.',
                           'Lineage labels are exact metadata strings; unresolved donor relationships remain.',
                           'Reference intervals condition on empirical training distributions; no training-distribution uncertainty or multiplicity adjustment.']}


def compute(inputs):
    protocol = json.loads((PACKAGE / 'protocol.json').read_text())
    frozen = transfer.load_freeze(RUN)
    locked = json.loads((RUN / 'predictions.json').read_text())
    if locked['freeze_sha256'] != sha256(RUN / 'frozen.json'):
        raise ValueError('Changed prediction/freeze binding')
    development = ROOT / 'research/readiness-20261021/development.csv'
    columns = ['model_id', 'group', 'lineage'] + ['expr:' + g for g in frozen['protocol']['predictors']]
    train = pd.read_csv(development, usecols=columns)
    external = pd.DataFrame(locked['rows'])[columns]
    source = ROOT / 'research/transfer-results-20261021/source-manifest.json'
    source_data = json.loads(source.read_text())
    expression = inputs / source_data['expression_file']
    if sha256(expression) != source_data['expression_sha256']:
        raise ValueError('Changed expression input')
    raw, missing = transfer.matrix(expression, frozen['protocol']['predictors'], frozen['gene_map']['expr'], set(external.model_id))
    if missing:
        raise ValueError('Missing stable gene IDs')
    for row in external.to_dict('records'):
        if row['model_id'] not in raw:
            raise ValueError('Missing raw expression identity')
        for gene in frozen['protocol']['predictors']:
            if raw[row['model_id']][gene] != row['expr:' + gene]:
                raise ValueError('Expression mapping/extraction differs')
    if len(train) != 773 or len(external) != 77:
        raise ValueError('Frozen cohort size changed')
    result = analyze(train, external, frozen, protocol)
    bound = [PACKAGE / 'protocol.json', Path(__file__), development, RUN / 'frozen.json',
             RUN / 'predictions.json', source, ROOT / 'src/transfer_trial.py', ROOT / 'src/core.py']
    result['bindings'] = {str(p.relative_to(ROOT)): sha256(p) for p in bound}
    result['expression_sha256'] = source_data['expression_sha256']
    result['input_validation'] = 'All 77 x 30 raw expression values reproduce the locked extract exactly by stable Entrez ID; no response file read'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['run', 'verify'])
    parser.add_argument('--inputs', type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    result = compute(args.inputs)
    path = PACKAGE / 'diagnostic.json'
    if args.phase == 'run':
        with path.open('x') as handle:
            handle.write(dumps(result))
    elif result != json.loads(path.read_text()):
        raise ValueError('Diagnostic replay differs')
    print(f'PASS {args.phase}: 30 genes, 12 rules, 77 external models; {time.perf_counter()-start:.3f} seconds')


if __name__ == '__main__':
    main()
