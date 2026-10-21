"""Optional pinned metadata replay using curl; never fetch dependency matrices.

Run with Python plus openpyxl to re-extract the two metadata worksheets. The
standard audit has no network dependency and uses the committed extracts.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/qualification-20261021'


def fetch(url, path, sha=None, size=None, byte_range=None, md5=None):
    if not path.exists():
        command = ['curl', '--fail', '--location', '--silent', '--show-error', '--max-time', '45']
        if byte_range:
            command += ['--range', byte_range]
        temporary = path.with_suffix(path.suffix + '.part')
        command += [url, '--output', str(temporary)]
        subprocess.run(command, check=True)
        data = temporary.read_bytes()
    else:
        temporary = None
        data = path.read_bytes()
    if size is not None and len(data) != size:
        raise ValueError(f'Changed size or range ignored: {path.name}')
    if sha and hashlib.sha256(data).hexdigest() != sha:
        raise ValueError(f'Changed SHA-256: {path.name}')
    if md5 and hashlib.md5(data).hexdigest() != md5:
        raise ValueError(f'Publisher MD5 mismatch: {path.name}')
    if temporary:
        temporary.replace(path)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    lock = json.loads((HERE / 'source-lock.json').read_text())
    metadata = json.loads((HERE / 'sources/broad-figshare.json').read_text())
    allowed = {'model_metadata.csv', 'screen_metadata.csv'}
    for record in metadata['files']:
        if record['name'] in allowed:
            local = 'broad-' + record['name']
            sha = lock['audit_inputs'][str((HERE / 'sources' / local).relative_to(ROOT))]
            fetch(record['download_url'], RAW / local, sha=sha, size=record['size'], md5=record['computed_md5'])
    info = lock['raw_metadata_files']['broad-supplementary-table1.xlsx']
    fetch(lock['sources']['broad_supplement'], RAW / 'broad-supplementary-table1.xlsx',
          sha=info['sha256'], size=info['bytes'])
    for name, byte_range in lock['sanger_zip']['ranges'].items():
        info = lock['raw_metadata_files'][name]
        fetch(lock['sources']['sanger_supplement'], RAW / name, sha=info['sha256'],
              size=info['bytes'], byte_range=byte_range)
    # Sparse local archive contains only the locked metadata ranges. Dependency
    # members are not downloaded, decompressed, or made available by this script.
    sparse = RAW / 'sanger-metadata-replay.zip'
    with sparse.open('wb') as handle:
        tail = (RAW / 'sanger-zip-tail.bin').read_bytes()
        handle.seek(lock['sanger_zip']['bytes'] - len(tail))
        handle.write(tail)
        for name, start in [('sanger-zip-metadata.bin', 0), ('sanger-zip-table2.bin', 116710)]:
            handle.seek(start)
            handle.write((RAW / name).read_bytes())
    with zipfile.ZipFile(sparse) as archive:
        for name in ('supplementary_table_2_revision.xlsx', 'supplementary_table_10_revision.xlsx'):
            data = archive.read(name)  # ZIP CRC checked by zipfile.
            if hashlib.sha256(data).hexdigest() != lock['raw_metadata_files'][name]['sha256']:
                raise ValueError(f'Changed extracted workbook: {name}')
            (RAW / name).write_bytes(data)
    print('PASS pinned metadata retrieval; dependency tables not fetched')


if __name__ == '__main__':
    main()
