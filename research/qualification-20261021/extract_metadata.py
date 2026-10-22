"""Extract only model identity/availability fields; never read response worksheets.

Optional source replay needs openpyxl. Normal qualification checks use committed JSON
and Python's standard library. Original workbooks stay in ignored data/raw/.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def rows(path, sheet, required):
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        iterator = workbook[sheet].iter_rows(values_only=True)
        header = next(iterator)
        if not set(required) <= set(header):
            raise ValueError(f"Changed schema: {sheet}")
        positions = {key: header.index(key) for key in required}
        result = []
        for row in iterator:
            if row[positions[required[0]]] is None:
                continue
            result.append({key: row[index] for key, index in positions.items()})
        return result
    finally:
        workbook.close()


def extract(raw):
    broad = rows(raw / 'broad-supplementary-table1.xlsx', 'NextGen Model Metadata',
                 ['Model ID', 'Cell Line Name', 'Alias', 'Lineage', 'Culture Format',
                  'HasExprData', 'HasWGS', 'HasCNData', 'HasCRISPRData'])
    sanger = rows(raw / 'supplementary_table_2_revision.xlsx', 'data_availability',
                  ['sample_ID', 'sanger_ID', 'individual_ID', 'primary_tumour_type',
                   'overlap_Broad_DepMap', 'WGS_available', 'RNAseq_available', 'CRISPR_available'])
    for row in sanger:
        individual = row.pop('individual_ID')
        if individual is None:
            raise ValueError('Missing Sanger individual grouping identifier')
        row['individual_group'] = hashlib.sha256(
            ('sanger-organoid-individual:' + str(individual)).encode()).hexdigest()
    return {'broad-aliases.json': broad, 'sanger-availability.json': sanger}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, default=ROOT / 'data/raw/qualification-20261021')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for name, value in extract(args.raw).items():
        path = HERE / 'sources' / name
        text = json.dumps(value, indent=2, sort_keys=True) + '\n'
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        elif path.read_text() != text:
            raise ValueError(f'Extraction differs: {name}')
    print('PASS: identity/availability extraction; no clinical or response worksheet inspected')
