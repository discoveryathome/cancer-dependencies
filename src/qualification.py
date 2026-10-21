"""Reproduce a metadata-only feasibility audit. No response or feature-matrix I/O."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/qualification-20261021'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value in ('TRUE', 'True', 'Yes'):
        return True
    if isinstance(value, str) and value in ('FALSE', 'False', 'No'):
        return False
    raise ValueError(f'Unknown availability flag: {value!r}')


def name_key(value):
    if value is None or str(value).strip().lower() in ('', 'na', 'n/a', 'nan', 'none', 'unknown'):
        return None
    return re.sub('[^A-Z0-9]', '', str(value).upper()) or None


def tokens(row):
    result = set()
    for key in ('ModelID', 'PatientID', 'RRID', 'SangerModelID', 'COSMICID', 'individual_group'):
        value = str(row.get(key, '')).strip()
        if not name_key(value):
            continue
        if key == 'COSMICID' and value.endswith('.0'):
            value = value[:-2]
        result.add((key, value))
    for field in ('StrippedCellLineName', 'Cell Line Name', 'sample_ID', 'sanger_ID'):
        value = name_key(row.get(field))
        if value:
            result.add(('model_name', value))
    # Delimiters observed in alias metadata; do not split hyphens or underscores.
    for alias in re.split(r'[;,|\n]', str(row.get('Alias') or '')):
        value = name_key(alias)
        if value:
            result.add(('model_name', value))
    return result


def connected(records):
    parent = list(range(len(records)))
    seen, edges = {}, []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, row in enumerate(records):
        for key in sorted(tokens(row)):
            if key in seen:
                j = seen[key]
                if find(i) != find(j):
                    edges.append({'left': i, 'right': j, 'namespace': key[0], 'value': key[1]})
                    parent[find(i)] = find(j)
            else:
                seen[key] = i
    return [find(i) for i in range(len(records))], edges


def read_csv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def unique_index(rows, key):
    output = {}
    for row in rows:
        value = row[key]
        if not value or value in output:
            raise ValueError(f'Duplicate or missing {key}: {value}')
        output[value] = row
    return output


def verify_sources():
    lock = json.loads((OUT / 'source-lock.json').read_text())
    for path, expected in lock['audit_inputs'].items():
        if digest(ROOT / path) != expected:
            raise ValueError(f'Changed audit input: {path}')
    return lock


def audit():
    lock = verify_sources()
    sources = OUT / 'sources'
    old = read_csv(ROOT / 'data/model-metadata.csv')
    bridge = read_csv(ROOT / 'research/readiness-20261021/sources/Model.csv')
    broad = read_csv(sources / 'broad-model_metadata.csv')
    screens = read_csv(sources / 'broad-screen_metadata.csv')
    aliases = json.loads((sources / 'broad-aliases.json').read_text())
    sanger = json.loads((sources / 'sanger-availability.json').read_text())
    alias_map = unique_index(aliases, 'Model ID')
    unique_index(broad, 'ModelID')
    unique_index(screens, 'ScreenID')
    unique_index(sanger, 'sample_ID')
    for row in broad:
        if truth(row['IsNextGen']) and row['ModelID'] not in alias_map:
            raise ValueError('NextGen model without supplementary identity record')
        row.update(alias_map.get(row['ModelID'], {}))
    # 24Q4 is an identity bridge, not an exclusion cohort: no outcomes were examined.
    blocks = [('old', old), ('bridge24q4', bridge), ('broad', broad), ('sanger', sanger)]
    records = [dict(row, source=source) for source, rows in blocks for row in rows]
    groups, edges = connected(records)
    old_groups = {g for g, row in zip(groups, records) if row['source'] == 'old'}
    broad_groups = {g for g, row in zip(groups, records) if row['source'] == 'broad'}
    flag_groups = {g for g, row in zip(groups, records)
                   if row['source'] == 'sanger' and truth(row['overlap_Broad_DepMap'])}
    passed = collections.defaultdict(list)
    for screen in screens:
        if truth(screen['PassesQC']):
            passed[screen['ModelID']].append(screen)
    broad_rows, sanger_rows = [], []
    for group, row in zip(groups, records):
        if row['source'] == 'broad' and truth(row['IsNextGen']):
            model = row['ModelID']
            selected = [s for s in passed[model] if truth(s['IsNextGen'])]
            has_screen = bool(selected)
            if has_screen != truth(row['HasCRISPRData']):
                raise ValueError('Model/screen availability mismatch')
            broad_rows.append(dict(model_id=model, component=group, lineage=row['OncotreeLineage'],
                passing_screens=len(selected), expression_listed=truth(row['HasExprData']),
                cn_listed=truth(row['HasCNData']), old_identity_overlap=group in old_groups,
                annotation_eligible=row['OncotreePrimaryDisease'] not in ('', 'Non-Cancerous') and
                    row['OncotreeLineage'] not in ('', 'Normal', 'Fibroblast', 'Muscle', 'Hair', 'Other'),
                sanger_flagged_overlap=group in flag_groups,
                screen_types=sorted({s['ScreenType'] for s in selected}),
                libraries=sorted({s['Library'] for s in selected})))
        if row['source'] == 'sanger':
            sanger_rows.append(dict(sample_id=row['sample_ID'], component=group,
                individual_group=row['individual_group'], lineage=row['primary_tumour_type'],
                crispr_listed=truth(row['CRISPR_available']), expression_listed=truth(row['RNAseq_available']),
                old_identity_overlap=group in old_groups, broad_identity_overlap=group in broad_groups,
                broad_flagged_overlap=group in flag_groups))
    broad_screened = [r for r in broad_rows if r['passing_screens']]
    broad_candidates = [r for r in broad_screened if r['expression_listed'] and
                        r['annotation_eligible'] and not r['old_identity_overlap']]
    sanger_screened = [r for r in sanger_rows if r['crispr_listed']]
    sanger_candidates = [r for r in sanger_screened if r['expression_listed'] and not
                         (r['old_identity_overlap'] or r['broad_identity_overlap'] or r['broad_flagged_overlap'])]

    def summarize(rows):
        components = collections.defaultdict(list)
        for row in rows:
            components[row['component']].append(row)
        return {'models': len(rows), 'identity_components': len(components),
                'models_by_lineage': dict(sorted(collections.Counter(r['lineage'] for r in rows).items())),
                'component_representatives': sorted(min(r.get('model_id', r.get('sample_id')) for r in rs)
                                                    for rs in components.values())}

    old_ids = {r['ModelID'] for r in old}
    return {
        'schema': 'cancer-qualification-audit/v1', 'source_lock_sha256': digest(OUT / 'source-lock.json'),
        'scope': 'Metadata-only feasibility; no new feature or dependency outcomes loaded or scored.',
        'source_rows': {name: len(rows) for name, rows in blocks},
        'broad_screened_nextgen': summarize(broad_screened),
        'broad_screened_ids_absent_old': sum(r['model_id'] not in old_ids for r in broad_screened),
        'broad_provisional_reserve': summarize(broad_candidates),
        'sanger_screened': summarize(sanger_screened),
        'sanger_screened_broad_flagged_models': sum(r['broad_flagged_overlap'] for r in sanger_screened),
        'sanger_provisional_reserve': summarize(sanger_candidates),
        'broad_records': broad_rows, 'sanger_records': sanger_rows,
        'identity_nodes': [{'source': r['source'], 'id': r.get('ModelID', r.get('sample_ID'))} for r in records],
        'identity_edges': edges,
        'confirmation_ready': False,
        'limitations': [
            'Counts are provisional upper bounds on eligible independent units, not confirmation sample sizes.',
            'Broad supplementary aliases omit complete PatientID/RRID/SangerModelID mappings for new models.',
            'Names are normalized conservatively; collisions and unlisted aliases need independent review.',
            'Sanger related models are grouped through individual identifiers; unrecorded relationships can remain.',
            'Sanger reserve excludes whole components linked to any Broad metadata model or marked Broad overlap.',
            'Expression availability flags do not establish required gene coverage or compatible feature values.',
            'Target support, branch support, statistical power and source-processing independence are unresolved.',
            'NextGen Humagne and Sanger organoid assays require a new approved protocol; original Avana/2DS gate is unchanged.',
            'Published study results have been read; these public resources cannot be described as wholly unseen evidence.'
        ]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Write the deterministic metadata audit')
    args = parser.parse_args()
    result = audit()
    output = OUT / 'cohort-audit.json'
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        output.write_text(encoded)
    elif output.read_text() != encoded:
        raise ValueError('Audit differs from frozen evidence')
    for name in ('broad_screened_nextgen', 'broad_provisional_reserve', 'sanger_screened', 'sanger_provisional_reserve'):
        print(name, json.dumps({k: v for k, v in result[name].items() if k != 'component_representatives'}))
    print('PASS metadata audit; confirmation_ready=false')


if __name__ == '__main__':
    main()
