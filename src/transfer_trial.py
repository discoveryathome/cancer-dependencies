"""Frozen expression-only transfer trial: fit -> predict -> score -> verify.

Only `score`/`verify` open the external response CSV. No remote code or pickle is
loaded. A freeze binds development data, protocol, source and all model choices.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'

import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import re
import time

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits

from core import dumps, predict, sha256
from models import fit_models, linear_fit, splits
from readiness import load_development
from trial import fit_pair

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/transfer-trial-20261021'
QUALIFICATION = ROOT / 'research/qualification-20261021'
FAMILIES = ('mean', 'lineage', 'self_expression', 'rule_expression', 'strong_expression', 'compact_expression_pair')
CODE = ('src/transfer_trial.py', 'src/core.py', 'src/models.py', 'src/trial.py',
        'src/readiness.py', 'src/benchmark.py', 'src/compact_candidate.py')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create protects frozen artifacts from accidental replacement.
    with path.open('x') as handle:
        handle.write(dumps(value))


def bind(paths):
    return {str(Path(p).relative_to(ROOT)): sha256(p) for p in paths}


def check_bindings(bindings):
    for name, expected in bindings.items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f'Changed frozen input/source: {name}')


def load_protocol():
    protocol = read_json(PACKAGE / 'protocol.json')
    cfg = read_json(ROOT / 'config/benchmark.json')
    if protocol['targets'] != cfg['targets'] or protocol['predictors'] != cfg['predictors']:
        raise ValueError('Changed original target/predictor panel')
    if protocol['families'] != list(FAMILIES) or protocol['external_screen_type'] != '3DO':
        raise ValueError('Unsupported protocol')
    return protocol


def cohort():
    """Use only the previously frozen metadata graph; never inspect responses."""
    from qualification import audit
    audit_result = audit()
    if audit_result != read_json(QUALIFICATION / 'cohort-audit.json'):
        raise ValueError('Qualification audit no longer reproduces')
    candidates = [r for r in audit_result['broad_records'] if r['passing_screens'] and
                  r['expression_listed'] and r['annotation_eligible'] and
                  not r['old_identity_overlap'] and r['screen_types'] == ['3DO']]
    # Qualifying one representative per recorded component, chosen without outcomes.
    chosen = {}
    for row in sorted(candidates, key=lambda r: r['model_id']):
        chosen.setdefault(row['component'], row)
    screens = pd.read_csv(QUALIFICATION / 'sources/broad-screen_metadata.csv', dtype=str)
    result = []
    for group, row in sorted(chosen.items(), key=lambda pair: pair[1]['model_id']):
        matches = screens[(screens.ModelID == row['model_id']) & (screens.PassesQC == 'TRUE') &
                          (screens.ScreenType == '3DO') & (screens.Library == 'Humagne-CD')]
        if len(matches) != 1:
            raise ValueError('Ambiguous eligible screen: ' + row['model_id'])
        result.append({'model_id': row['model_id'], 'group': 'qualified-component-' + str(group),
                       'lineage': row['lineage'], 'screen_id': matches.iloc[0].ScreenID})
    if len(result) < 30:
        raise ValueError('Insufficient metadata cohort')
    return result


def select_models(frame, target, cfg):
    train = frame.loc[frame['y:' + target].notna()].reset_index(drop=True)
    y = train['y:' + target].to_numpy(float)
    models, search = fit_models(train, y, target, cfg)
    options = [(r['inner_mse'], r['model']) for r in search['linear']
               if r['model'] in ('ridge_expr', 'elastic_expr')]
    loss = 0.0
    for a, b in splits(train, cfg['inner_folds'], cfg['inner_seed']):
        model = linear_fit(train.iloc[a], y[a], ['expr:' + target], 'self')
        loss += float(np.sum((y[b] - predict(model, train.iloc[b])) ** 2))
    options.append((loss / len(train), 'self_expression'))
    winner = min(options)[1]
    selected = {'mean': models['mean'], 'lineage': models['lineage'],
                'self_expression': models['self_expression'], 'rule_expression': models['rule_expr'],
                'strong_expression': models[winner],
                'compact_expression_pair': fit_pair(train, y, target, 'blind_pair', cfg,
                                                     {'ridge_alphas': cfg['ridge_alphas']})}
    if any(not f.startswith('expr:') for m in selected.values() for f in m.get('features', [])):
        raise ValueError('Non-expression predictor leaked into trial')
    return {'models': selected, 'strong_expression_name': winner,
            'inner_selection': [list(option) for option in sorted(options)], 'training_groups': sorted(train.group),
            'training_n': len(train), 'training_target_variance': float(np.var(y))}


def freeze(out):
    if (out / 'frozen.json').exists():
        raise ValueError('Refusing to overwrite freeze')
    protocol = load_protocol()
    cfg, frame, _ = load_development()
    # The loader reads only the old development extract; remove all other modalities.
    columns = ['model_id', 'group', 'lineage'] + ['expr:' + g for g in protocol['predictors']] + ['y:' + g for g in protocol['targets']]
    frame = frame[columns]
    if not np.isfinite(frame.filter(like='y:').to_numpy(float)).all():
        raise ValueError('Development target missingness changed; review required')
    inputs = [ROOT / p for p in CODE] + [PACKAGE / 'protocol.json', ROOT / 'config/benchmark.json',
        ROOT / 'data/gene-map.json', ROOT / 'src/qualification.py', QUALIFICATION / 'cohort-audit.json',
        QUALIFICATION / 'source-lock.json', ROOT / 'research/readiness-20261021/development-lock.json']
    inputs += [ROOT / p for p in read_json(ROOT / 'research/readiness-20261021/development-lock.json')['files']]
    start = time.monotonic()
    models = {}
    with threadpool_limits(limits=1):
        for target in protocol['targets']:
            models[target] = select_models(frame, target, cfg)
            print('FROZEN', target, models[target]['strong_expression_name'], flush=True)
    artifact = {'schema': 'expression-transfer-freeze/v1', 'created_at': now(),
                'protocol': protocol, 'bindings': bind(inputs), 'cohort': cohort(), 'targets': models,
                'gene_map': read_json(ROOT / 'data/gene-map.json'), 'seconds': time.monotonic() - start,
                'exposure': 'No new external outcomes loaded during fit; published study summaries already known.',
                'evidence': 'author-frozen exploratory trial; no independent scientific acceptance'}
    write_new(out / 'frozen.json', artifact)
    print('PASS frozen models', sha256(out / 'frozen.json'))


def load_freeze(out):
    frozen = read_json(out / 'frozen.json')
    if frozen['schema'] != 'expression-transfer-freeze/v1':
        raise ValueError('Wrong frozen schema')
    check_bindings(frozen['bindings'])
    return frozen


def verify_fit(out):
    frozen = load_freeze(out)
    cfg, frame, _ = load_development()
    protocol = frozen['protocol']
    columns = ['model_id', 'group', 'lineage'] + ['expr:' + g for g in protocol['predictors']] + ['y:' + g for g in protocol['targets']]
    frame = frame[columns]
    with threadpool_limits(limits=1):
        for target in protocol['targets']:
            if select_models(frame, target, cfg) != frozen['targets'][target]:
                raise ValueError('Development source refit differs: ' + target)
    if cohort() != frozen['cohort']:
        raise ValueError('Frozen cohort differs from qualification evidence')
    print('PASS all 12 development source refits and cohort selection')


def matrix(path, genes, mapping, rows):
    """Parse a bounded wide matrix. Entrez IDs required; duplicate IDs fail closed."""
    path = Path(path)
    with path.open(newline='') as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(header) < 2 or len(set(header)) != len(header):
            raise ValueError('Missing/duplicate matrix headers')
        columns = {}
        for i, column in enumerate(header[1:], 1):
            match = re.fullmatch(r'(.+) \((\d+)\)', column)
            if match:
                gene_id = match[2]
                if gene_id in columns:
                    raise ValueError('Duplicate stable gene ID: ' + gene_id)
                columns[gene_id] = i
        positions, missing = {}, []
        for gene in genes:
            match = re.fullmatch(r'(.+) \((\d+)\)', mapping[gene])
            if not match:
                raise ValueError('Invalid frozen gene mapping')
            if match[2] in columns:
                positions[gene] = columns[match[2]]
            else:
                missing.append(gene)
        selected, seen = {}, set()
        for row in reader:
            if len(row) != len(header):
                raise ValueError('Ragged matrix row')
            identity = row[0]
            if not identity or identity in seen:
                raise ValueError('Missing/duplicate matrix identity')
            seen.add(identity)
            if identity not in rows:
                continue
            values = {}
            for gene, index in positions.items():
                text = row[index]
                if text in ('', 'NA', 'NaN', 'nan'):
                    values[gene] = None
                else:
                    number = float(text)
                    if not np.isfinite(number):
                        raise ValueError('Infinite/nonfinite matrix value')
                    values[gene] = number
            selected[identity] = values
    return selected, missing


def source_manifest(path):
    source = read_json(path)
    required = {'release', 'expression_file', 'response_file', 'expression_sha256', 'response_sha256',
                'expression_units', 'response_units', 'expression_row_id', 'response_row_id',
                'source_url', 'terms_url', 'terms_status'}
    if not required <= source.keys() or any(source[k] in (None, '', 'pending') for k in required):
        raise ValueError('Incomplete source/measurement manifest')
    if source['release'] != 'NextGen Model Manuscript 2026':
        raise ValueError('Release differs; 26Q3 is not a silent substitute')
    if source['expression_file'] != 'next_gen_expression.csv' or source['response_file'] != 'screen_gene_effect.csv':
        raise ValueError('Unexpected manuscript files')
    if source['expression_units'] != 'log2(TPM+1)' or source['response_units'] != 'Chronos gene effect':
        raise ValueError('Unapproved measurement scale')
    if source['expression_row_id'] != 'ModelID' or source['response_row_id'] != 'ScreenID':
        raise ValueError('Unapproved matrix identity unit')
    if source['terms_status'] != 'reviewed-for-local-research':
        raise ValueError('Source-specific local use terms unresolved')
    for key in ('expression_sha256', 'response_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', source[key]):
            raise ValueError('Invalid source checksum')
    return source


def build_predictions(frozen, expression_path):
    protocol = frozen['protocol']
    chosen = frozen['cohort']
    values, missing_genes = matrix(expression_path, protocol['predictors'], frozen['gene_map']['expr'],
                                  {r['model_id'] for r in chosen})
    if missing_genes:
        raise ValueError('Missing expression gene columns: ' + ','.join(missing_genes))
    included, excluded = [], []
    for row in chosen:
        value = values.get(row['model_id'])
        if value is None or any(value[g] is None for g in protocol['predictors']):
            excluded.append({'model_id': row['model_id'], 'reason': 'missing expression row or incomplete 30-gene panel'})
            continue
        if any(value[g] < 0 for g in protocol['predictors']):
            raise ValueError('Negative value inconsistent with log2(TPM+1)')
        included.append({**row, **{'expr:' + g: value[g] for g in protocol['predictors']}})
    if len(included) < protocol['minimum_external_units']:
        raise ValueError('Too few complete expression models; no evaluation')
    frame = pd.DataFrame(included)
    if frame.group.duplicated().any() or frame.model_id.duplicated().any() or frame.screen_id.duplicated().any():
        raise ValueError('Duplicate external identity/screen')
    predictions = {}
    for target in protocol['targets']:
        predictions[target] = {}
        for name in FAMILIES:
            model = frozen['targets'][target]['models'][name]
            predictions[target][name] = predict(model, frame).tolist()
    return {'rows': included, 'excluded': excluded, 'predictions': predictions}


def lock_predictions(out, inputs, manifest):
    frozen = load_freeze(out)
    source = source_manifest(manifest)
    expression_path = inputs / source['expression_file']
    if sha256(expression_path) != source['expression_sha256']:
        raise ValueError('Expression source checksum mismatch')
    data = build_predictions(frozen, expression_path)
    lock = {'schema': 'expression-transfer-predictions/v1', 'created_at': now(),
            'freeze_sha256': sha256(out / 'frozen.json'), 'source': source,
            'source_manifest_sha256': sha256(manifest), **data,
            'exposure': 'Predictions locked before external response parsing; expression inputs inspected.'}
    write_new(out / 'predictions.json', lock)
    print('PASS locked predictions', len(data['rows']), 'models; excluded', len(data['excluded']))


def spearman_rows(y, prediction):
    """Average ranks, pairwise finite rows; undefined for constants or <3 pairs."""
    y, prediction = np.broadcast_arrays(np.asarray(y, float), np.asarray(prediction, float))
    valid = np.isfinite(y) & np.isfinite(prediction)
    count = valid.sum(axis=1)
    a = rankdata(np.where(valid, y, np.nan), axis=1, method='average', nan_policy='omit')
    b = rankdata(np.where(valid, prediction, np.nan), axis=1, method='average', nan_policy='omit')
    a -= np.nansum(a, axis=1)[:, None] / np.maximum(count, 1)[:, None]
    b -= np.nansum(b, axis=1)[:, None] / np.maximum(count, 1)[:, None]
    numerator = np.nansum(a * b, axis=1)
    denominator = np.sqrt(np.nansum(a * a, axis=1) * np.nansum(b * b, axis=1))
    return np.divide(numerator, denominator, out=np.full(len(count), np.nan),
                     where=(denominator > 0) & (count >= 3))


def finite_or_none(number):
    return float(number) if np.isfinite(number) else None


def evaluate(frozen, locked, outcomes):
    protocol = frozen['protocol']
    rows = locked['rows']
    ids = [r['screen_id'] for r in rows]
    values, missing = matrix(outcomes, protocol['targets'], frozen['gene_map']['y'], set(ids))
    n = len(rows)
    rng = np.random.default_rng(protocol['bootstrap_seed'])
    # One selected row per recorded component; the same identity draws across targets.
    resamples = rng.integers(0, n, size=(protocol['bootstrap_replicates'], n))
    tables, contrasts, support, bootstrap = {}, [], [], []
    for target in protocol['targets']:
        yy = np.asarray([values.get(i, {}).get(target, np.nan) for i in ids], float)
        valid = np.isfinite(yy)
        target_result = {'n': int(valid.sum()), 'missing_target_column': target in missing,
                         'missing_response_models': [r['model_id'] for r, keep in zip(rows, valid) if not keep],
                         'models': {}, 'lineages': []}
        for family in FAMILIES:
            pp = np.asarray(locked['predictions'][target][family], float)
            rho = spearman_rows(yy[None, :], pp[None, :])[0]
            target_result['models'][family] = {'spearman': finite_or_none(rho),
                'mse_diagnostic': float(np.mean((yy[valid] - pp[valid]) ** 2)) if valid.any() else None}
        pair = np.asarray(locked['predictions'][target]['compact_expression_pair'])
        strong = np.asarray(locked['predictions'][target]['strong_expression'])
        pr = target_result['models']['compact_expression_pair']['spearman']
        sr = target_result['models']['strong_expression']['spearman']
        contrast = pr - sr if pr is not None and sr is not None else None
        target_result['paired_spearman_difference_vs_strong'] = contrast
        target_result['adequate_total_support'] = int(valid.sum()) >= protocol['minimum_external_units']
        rule = frozen['targets'][target]['models']['rule_expression']
        if rule['kind'] == 'rule':
            feature = rule['features'][0]
            left = np.asarray([r[feature] <= rule['threshold'] for r in rows]) & valid
            counts = [int(left.sum()), int(valid.sum() - left.sum())]
            target_result['rule_branch_support'] = counts
            target_result['adequate_rule_branch_support'] = min(counts) >= protocol['minimum_rule_branch_units']
        else:
            target_result['rule_branch_support'] = None
            target_result['adequate_rule_branch_support'] = False
        for lineage in sorted({r['lineage'] for r in rows}):
            mask = np.asarray([r['lineage'] == lineage for r in rows]) & valid
            target_result['lineages'].append({'lineage': lineage, 'n': int(mask.sum()),
                'pair_spearman': finite_or_none(spearman_rows(yy[None, mask], pair[None, mask])[0]),
                'strong_spearman': finite_or_none(spearman_rows(yy[None, mask], strong[None, mask])[0]),
                'interpretation': 'descriptive; no lineage-specific confirmation claim'})
        boot_delta = spearman_rows(yy[resamples], pair[resamples]) - spearman_rows(yy[resamples], strong[resamples])
        bootstrap.append(boot_delta)
        contrasts.append(contrast)
        support.append(target_result['adequate_total_support'])
        tables[target] = target_result
    complete = all(support) and all(x is not None for x in contrasts)
    boot = np.asarray(bootstrap).T
    valid_draws = np.isfinite(boot).all(axis=1)
    draws = boot[valid_draws].mean(axis=1)
    # Do not silently drop an unsupported target from the primary endpoint.
    interval = np.quantile(draws, [.025, .975]).tolist() if complete and valid_draws.mean() >= .95 else None
    return {'schema': 'expression-transfer-results/v1', 'targets': tables,
        'primary': {'name': 'macro target-wise Spearman difference: compact pair minus strong expression baseline',
                    'target_count': len(protocol['targets']), 'complete': complete,
                    'estimate': float(np.mean(contrasts)) if complete else None,
                    'conditional_identity_bootstrap_ci95': interval,
                    'valid_bootstrap_draws': int(valid_draws.sum()),
                    'total_bootstrap_draws': len(valid_draws)},
        'eligible_expression_models': n, 'excluded_expression_models': locked['excluded'],
        'evidence': 'exploratory transfer; provisional identity independence; no discovery or clinical claim',
        'limitations': ['Conditional on fitted models and recorded identity groups; missing donor mappings remain.',
                        'Shared upstream assay processing and culture differences remain.',
                        'MSE is an uncalibrated diagnostic, not the primary transfer endpoint.',
                        'No independent newcomer or scientific review; no multiplicity-adjusted target claims.',
                        'Strong comparator is restricted to the same 30-gene expression panel.']}


def score(out, inputs, manifest, verify=False):
    frozen = load_freeze(out)
    locked = read_json(out / 'predictions.json')
    if locked['freeze_sha256'] != sha256(out / 'frozen.json') or locked['schema'] != 'expression-transfer-predictions/v1':
        raise ValueError('Prediction/freeze binding mismatch')
    source = source_manifest(manifest)
    if locked['source'] != source or locked['source_manifest_sha256'] != sha256(manifest):
        raise ValueError('Source manifest changed after prediction lock')
    expression = inputs / source['expression_file']
    response = inputs / source['response_file']
    if sha256(expression) != source['expression_sha256'] or sha256(response) != source['response_sha256']:
        raise ValueError('Source bytes changed')
    expected = build_predictions(frozen, expression)
    if any(locked[key] != expected[key] for key in ('rows', 'excluded', 'predictions')):
        raise ValueError('Predictions/identity coverage failed independent arithmetic replay')
    exposure = {'freeze_sha256': sha256(out / 'frozen.json'), 'predictions_sha256': sha256(out / 'predictions.json'),
                'response_sha256': source['response_sha256'], 'scope': 'Broad manuscript 3DO exploratory outcomes; Sanger remains reserved'}
    if not verify:
        if (out / 'results.json').exists() or (out / 'exposure.json').exists():
            raise ValueError('Outcomes already opened; use verify for replay, not another trial')
        write_new(out / 'exposure.json', {'opened_at': now(), **exposure})
    else:
        recorded = read_json(out / 'exposure.json')
        if any(recorded.get(k) != v for k, v in exposure.items()):
            raise ValueError('Exposure record mismatch')
    result = evaluate(frozen, locked, response)
    result['bindings'] = exposure
    if verify:
        if result != read_json(out / 'results.json'):
            raise ValueError('Frozen result/score replay differs')
        print('PASS complete frozen external evaluation replay')
    else:
        write_new(out / 'results.json', result)
        print(dumps(result['primary']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('freeze', 'verify-fit', 'predict', 'score', 'verify'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--source-manifest', type=Path)
    args = parser.parse_args()
    if args.phase == 'freeze':
        freeze(args.out)
    elif args.phase == 'verify-fit':
        verify_fit(args.out)
    else:
        if args.inputs is None or args.source_manifest is None:
            parser.error('--inputs and --source-manifest required')
        if args.phase == 'predict':
            lock_predictions(args.out, args.inputs, args.source_manifest)
        else:
            score(args.out, args.inputs, args.source_manifest, verify=args.phase == 'verify')


if __name__ == '__main__':
    main()
