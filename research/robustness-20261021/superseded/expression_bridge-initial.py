"""Outcome-free matched-development expression audit and one offset falsification.

An offset is a release-bridge sensitivity model, not an identified assay effect.
No dependency values, historical final rows or Sanger data are read.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from core import dumps, sha256
import transfer_trial as transfer

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/robustness-20261021'
RUN = ROOT / 'research/transfer-trial-20261021/run'
DEVELOPMENT = ROOT / 'research/readiness-20261021/development.csv'


def paired_audit(old, new, genes, rules):
    """Aligned model rows only; all genes reported, complete cases for offset CV."""
    if old.model_id.duplicated().any() or old.group.duplicated().any():
        raise ValueError('Duplicate development identity')
    if new.model_id.duplicated().any():
        raise ValueError('Duplicate new model')
    if old.model_id.tolist() != new.model_id.tolist():
        raise ValueError('Unaligned model identities')
    columns = ['expr:' + g for g in genes]
    a, b = old[columns].to_numpy(float), new[columns].to_numpy(float)
    if np.isinf(a).any() or np.isinf(b).any() or (a < 0).any() or (b < 0).any():
        raise ValueError('Invalid expression')
    valid = np.isfinite(a) & np.isfinite(b)
    complete = valid.all(axis=1)
    ids = old.loc[complete, 'model_id'].tolist()
    groups = old.loc[complete, 'group'].tolist()
    order = sorted(range(len(groups)), key=lambda i: hashlib.sha256(groups[i].encode()).hexdigest())
    folds = np.empty(len(groups), int)
    for k, i in enumerate(order):
        folds[i] = k % 5
    x, y = a[complete], b[complete]
    enough = len(x) >= 100
    offsets = np.median(y - x, axis=0) if len(x) else np.full(len(genes), np.nan)
    corrected = np.full(y.shape, np.nan)
    fold_offsets = {}
    if enough:
        for fold in range(5):
            offset = np.median(y[folds != fold] - x[folds != fold], axis=0)
            corrected[folds == fold] = y[folds == fold] - offset
            fold_offsets[str(fold)] = dict(zip(genes, offset.tolist()))
    features, before_scaled, after_scaled = {}, [], []
    improved = 0
    for j, gene in enumerate(genes):
        mask = valid[:, j]
        av, bv = a[mask, j], b[mask, j]
        delta = bv - av
        full_old = a[np.isfinite(a[:, j]), j]
        iqr = float(np.subtract(*np.quantile(full_old, [.75, .25]))) if len(full_old) else 0.
        rho = float(spearmanr(av, bv).statistic) if len(av) >= 2 and np.ptp(av) > 0 and np.ptp(bv) > 0 else None
        row = {'paired_n': int(mask.sum()), 'missing_pairs': old.loc[~mask, 'model_id'].tolist(),
               'spearman': rho, 'old_paired_iqr': iqr,
               'paired_delta_quantiles': dict(zip(['min', 'q05', 'q25', 'median', 'q75', 'q95', 'max'], np.quantile(delta, [0,.05,.25,.5,.75,.95,1]).tolist())) if len(delta) else None,
               'mean_absolute_delta': float(np.abs(delta).mean()) if len(delta) else None,
               'equal_within_1e_9': int(np.isclose(av, bv, atol=1e-9, rtol=0).sum()),
               'all_complete_offset': float(offsets[j]) if len(x) else None,
               'lineage_median_deltas': {str(label): {'n': int(np.sum(mask & (old.lineage == label).to_numpy())), 'median': float(np.median((b-a)[mask & (old.lineage == label).to_numpy(), j]))}
                   for label in sorted(old.loc[mask, 'lineage'].unique())}}
        if enough and iqr > 0:
            before = float(np.mean(np.abs(y[:, j] - x[:, j])))
            after = float(np.mean(np.abs(corrected[:, j] - x[:, j])))
            row['oof'] = {'before_mae': before, 'after_mae': after, 'mae_change': after-before,
                          'before_scaled_mae': before/iqr, 'after_scaled_mae': after/iqr}
            before_scaled.append(before/iqr); after_scaled.append(after/iqr)
            improved += int(after < before)
        else:
            row['oof'] = None
        features[gene] = row
    rule_results = {}
    for target, rule in rules.items():
        if rule['kind'] != 'rule':
            rule_results[target] = {'kind': rule['kind']}
            continue
        j = columns.index(rule['features'][0]); mask = valid[:, j]
        old_left, new_left = a[mask, j] <= rule['threshold'], b[mask, j] <= rule['threshold']
        rule_results[target] = {'feature': rule['features'][0], 'threshold': rule['threshold'],
            'paired_n': int(mask.sum()), 'old_left': int(old_left.sum()), 'new_left': int(new_left.sum()),
            'branch_flips': int((old_left != new_left).sum()),
            'old_left_to_new_right': int((old_left & ~new_left).sum()),
            'old_right_to_new_left': int((~old_left & new_left).sum())}
    before = float(np.mean(before_scaled)) if before_scaled else None
    after = float(np.mean(after_scaled)) if after_scaled else None
    gain = 1-after/before if before and after is not None else None
    gate = enough and len(before_scaled) == len(genes) and gain is not None and gain >= .1 and improved >= 20
    return {'matched_n':len(old), 'complete_n':len(x), 'matched_ids':old.model_id.tolist(),
        'incomplete_ids':old.loc[~complete, 'model_id'].tolist(),
        'features':features, 'rules':rule_results,
        'offset_validation':{'folds':dict(zip(ids, folds.tolist())), 'fold_offsets':fold_offsets,
            'features_improved':improved, 'before_mean_scaled_mae':before,
            'after_mean_scaled_mae':after, 'relative_reduction':gain,
            'numerical_gate_passed':bool(gate),
            'interpretation':'Five-fold held-out expression agreement, no outcome use; heuristic gate, not statistical significance'},
        'offsets':dict(zip(genes, offsets.tolist())) if len(x) else None}


def compute(inputs):
    frozen = transfer.load_freeze(RUN)
    genes = frozen['protocol']['predictors']
    columns = ['model_id', 'group', 'lineage'] + ['expr:' + g for g in genes]
    development = pd.read_csv(DEVELOPMENT, usecols=columns)
    if len(development) != 773:
        raise ValueError('Changed development cohort')
    manifest = transfer.read_json(PACKAGE / 'source-manifest.json')
    path = inputs / manifest['file']
    if path.stat().st_size != manifest['bytes'] or sha256(path) != manifest['sha256']:
        raise ValueError('Changed manuscript input')
    values, missing = transfer.matrix(path, genes, frozen['gene_map']['expr'], set(development.model_id))
    if missing:
        raise ValueError('Missing stable genes: ' + ', '.join(missing))
    old = development[development.model_id.isin(values)].sort_values('model_id').reset_index(drop=True)
    new = pd.DataFrame([{'model_id':mid, **{'expr:'+g:values[mid][g] for g in genes}} for mid in old.model_id])
    if new.empty:
        raise ValueError('No paired development models')
    rules = {t: frozen['targets'][t]['models']['rule_expression'] for t in frozen['protocol']['targets']}
    result = paired_audit(old, new, genes, rules)
    # The actual gate denominator is the original development IQR. Here every
    # development model must be matched for the paired-IQR version of the gate.
    result['development_n'] = len(development)
    result['unmatched_development_ids'] = sorted(set(development.model_id)-set(old.model_id))
    if len(old) != len(development):
        result['offset_validation']['numerical_gate_passed'] = False
        result['offset_validation']['gate_note'] = 'Incomplete model overlap; paired IQR differs from protocol full-development IQR, defer correction.'
    source_lock = transfer.read_json(ROOT / 'data/source-lock.json')
    profile_names = ['OmicsProfiles.csv', 'OmicsDefaultModelProfiles.csv']
    for name in profile_names:
        expected = next(r['sha256'] for r in source_lock['files'] if r['name'] == name)
        if sha256(ROOT/'data/raw'/name) != expected:
            raise ValueError('Changed old RNA metadata')
    profiles = pd.read_csv(ROOT/'data/raw/OmicsProfiles.csv', dtype=str)
    defaults = pd.read_csv(ROOT/'data/raw/OmicsDefaultModelProfiles.csv', dtype=str)
    defaults = defaults[(defaults.ProfileType == 'rna') & defaults.ModelID.isin(old.model_id)]
    if defaults.ModelID.duplicated().any():
        raise ValueError('Ambiguous old default RNA profile')
    rna = defaults.merge(profiles, on=['ProfileID','ModelID'], how='left', validate='one_to_one')
    metadata_path = ROOT / 'research/qualification-20261021/sources/broad-model_metadata.csv'
    metadata = pd.read_csv(metadata_path, dtype=str)
    if metadata.ModelID.duplicated().any():
        raise ValueError('Ambiguous manuscript metadata')
    matched_meta = metadata.set_index('ModelID').reindex(old.model_id)
    result['provenance'] = {
        'old_rna_profiles':rna.fillna('').to_dict('records'),
        'old_missing_default_modelids':sorted(set(old.model_id)-set(rna.ModelID)),
        'old_datatypes':rna.Datatype.value_counts(dropna=False).to_dict(),
        'old_strandedness':rna.Stranded.fillna('missing').value_counts().to_dict(),
        'old_sources':rna.Source.fillna('missing').value_counts().to_dict(),
        'manuscript_metadata_columns':metadata.columns.tolist(),
        'matched_manuscript_traditional_status':matched_meta.IsTraditional2D.fillna('missing').value_counts().to_dict(),
        'manuscript_missing_modelids':matched_meta[matched_meta.IsTraditional2D.isna()].index.tolist(),
        'new_sample_or_profile_id_available':False,
        'conclusion':'ModelID pairs established. Supplied manuscript metadata has no RNA ProfileID or ModelCondition identifiers; same-sample continuity is unresolved. Offsets cannot be interpreted as isolated processing effects.'}
    bound = [Path(__file__), PACKAGE/'protocol.json', PACKAGE/'source-manifest.json', DEVELOPMENT,
             RUN/'frozen.json', metadata_path, ROOT/'data/source-lock.json', ROOT/'src/transfer_trial.py', ROOT/'src/core.py',
             ROOT/'setup/sources/depmap-24q2-README.txt', ROOT/'data/raw/transfer-trial-20261021/README.txt']
    result['bindings'] = transfer.bind(bound)
    result['traditional_expression_sha256'] = manifest['sha256']
    result['schema'] = 'matched-expression-audit/v1'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['run','verify'])
    parser.add_argument('--inputs', type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter(); result = compute(args.inputs)
    path = PACKAGE/'audit.json'
    if args.phase == 'run':
        transfer.write_new(path, result)
    elif transfer.read_json(path) != result:
        raise ValueError('Audit replay differs')
    print(dumps({'phase':args.phase,'matched':result['matched_n'],'complete':result['complete_n'],
        'gate':{k:v for k,v in result['offset_validation'].items() if k not in ['folds','fold_offsets']},
        'seconds':time.perf_counter()-start}))

if __name__ == '__main__':
    main()
