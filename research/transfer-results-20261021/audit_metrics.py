"""Separate SciPy arithmetic audit of the completed exploratory evaluation.

Reads only the selected screens' 12 response values into numerical arrays.
Does not fit, select or modify candidates. This is author checking, not an
independent scientific review. The main verifier replays the bootstrap too.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import warnings

import numpy as np
from scipy.stats import ConstantInputWarning, spearmanr

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'research/transfer-trial-20261021/run'
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    args = parser.parse_args()
    source = json.loads((HERE / 'source-manifest.json').read_text())
    frozen = json.loads((RUN / 'frozen.json').read_text())
    predictions = json.loads((RUN / 'predictions.json').read_text())
    result = json.loads((RUN / 'results.json').read_text())
    response = args.inputs / source['response_file']
    with response.open('rb') as handle:
        assert hashlib.file_digest(handle, 'sha256').hexdigest() == source['response_sha256']
    ids = [row['screen_id'] for row in predictions['rows']]
    assert len(ids) == len(set(ids)) == 77
    targets = frozen['protocol']['targets']
    values = {}
    with response.open(newline='') as handle:
        reader = csv.reader(handle)
        header = next(reader)
        columns = {re.search(r'\((\d+)\)$', name).group(1): i
                   for i, name in enumerate(header) if re.search(r'\((\d+)\)$', name)}
        selected = {gene: columns[re.search(r'\((\d+)\)$', frozen['gene_map']['y'][gene]).group(1)]
                    for gene in targets}
        for row in reader:
            if row[0] in ids:
                assert row[0] not in values
                values[row[0]] = {g: float(row[i]) if row[i] else np.nan for g, i in selected.items()}
    contrasts = []
    checked = 0
    for target in targets:
        y = np.array([values.get(identity, {}).get(target, np.nan) for identity in ids])
        keep = np.isfinite(y)
        assert int(keep.sum()) == result['targets'][target]['n'] == 77
        correlations = {}
        for family, numbers in predictions['predictions'][target].items():
            p = np.asarray(numbers)
            assert len(p) == len(y) and np.isfinite(p).all()
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', ConstantInputWarning)
                rho = float(spearmanr(y[keep], p[keep]).statistic)
            recorded = result['targets'][target]['models'][family]
            if np.isnan(rho):
                assert recorded['spearman'] is None
            else:
                assert abs(rho - recorded['spearman']) < 1e-12
            assert abs(float(np.mean((y[keep] - p[keep]) ** 2)) - recorded['mse_diagnostic']) < 1e-12
            correlations[family] = rho
            checked += 1
        contrasts.append(correlations['compact_expression_pair'] - correlations['strong_expression'])
    assert abs(float(np.mean(contrasts)) - result['primary']['estimate']) < 1e-12
    print(f'PASS separate SciPy audit: {checked} model/target metrics, all 12 targets x 77 responses, primary contrast')


if __name__ == '__main__':
    main()
