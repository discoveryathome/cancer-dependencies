"""Replay exact-ID bridge availability without reading dependency outcomes."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def ids(path, column):
    with path.open(newline='') as handle:
        reader = csv.reader(handle)
        header = next(reader)
        position = header.index(column) if column else 0
        result = [row[position] for row in reader]
    if len(result) != len(set(result)) or any(not value for value in result):
        raise ValueError('Duplicate or empty identity')
    return set(result)


parser = argparse.ArgumentParser()
parser.add_argument('--inputs', type=Path, required=True)
args = parser.parse_args()
expression = args.inputs / 'next_gen_expression.csv'
source = json.loads((ROOT / 'research/transfer-results-20261021/source-manifest.json').read_text())
with expression.open('rb') as handle:
    assert hashlib.file_digest(handle, 'sha256').hexdigest() == source['expression_sha256']
development = ROOT / 'research/readiness-20261021/development.csv'
freeze = json.loads((ROOT / 'research/transfer-trial-20261021/run/frozen.json').read_text())
with development.open('rb') as handle:
    assert hashlib.file_digest(handle, 'sha256').hexdigest() == freeze['bindings'][str(development.relative_to(ROOT))]
old, new = ids(development, 'model_id'), ids(expression, None)
assert (len(old), len(new), len(old & new)) == (773, 309, 0)
print('PASS exact-ID bridge availability: 773 development, 309 NextGen, 0 matched ModelIDs; paired comparison unavailable')
