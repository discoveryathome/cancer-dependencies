"""Export development rows without parsing/reformatting any numeric cells."""
import argparse,csv,io,json,pathlib
from core import dumps,sha256
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'
def main(write=False):
    source=ROOT/'data/panel/primary.csv';pins=json.loads((ROOT/'data/panel-lock.json').read_text())
    if sha256(source)!=pins['data/panel/primary.csv']:raise ValueError('Original panel changed')
    with source.open(newline='') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    dev=[r for r in rows if r['partition']=='development'];final=[r for r in rows if r['partition']=='final']
    if set(r['group'] for r in dev)&set(r['group'] for r in final):raise ValueError('Identity overlap')
    buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(dev)
    path=OUT/'development.csv';raw=buffer.getvalue().encode()
    if write:path.write_bytes(raw)
    elif path.read_bytes()!=raw:raise ValueError('Development extract differs from original cell strings')
    files=['research/readiness-20261021/development.csv','config/benchmark.json','src/models.py','src/core.py','src/trial.py','research/contributor-trial/protocol.json']
    lock=dict(files={p:sha256(ROOT/p) for p in files},source_panel_sha256=sha256(source),development_groups=sorted(r['group'] for r in dev),excluded_final_groups=sorted(r['group'] for r in final),scope='Only historical development rows, with original CSV cell strings preserved; final and Sanger outcomes excluded. Exposed development data, not a fresh holdout.')
    if write:(OUT/'development-lock.json').write_text(dumps(lock))
    elif json.loads((OUT/'development-lock.json').read_text())!=lock:raise ValueError('Development lock changed')
    print('PASS',len(dev),'development identities; original numeric cell strings preserved')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();main(a.write)
