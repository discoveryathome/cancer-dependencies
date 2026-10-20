"""Fetch only version-pinned, CC-BY data; verify publisher MD5 and record SHA256."""
import concurrent.futures, hashlib, json, pathlib, urllib.request, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
NAMES = ['ScreenGeneEffect.csv','OmicsExpressionProteinCodingGenesTPMLogp1.csv',
         'OmicsAbsoluteCNGene.csv','OmicsSomaticMutationsMatrixDamaging.csv',
         'OmicsSomaticMutationsMatrixHotspot.csv','Model.csv','AchillesScreenQCReport.csv',
         'OmicsDefaultModelProfiles.csv','OmicsProfiles.csv','CRISPRScreenMap.csv',
         'ScreenSequenceMap.csv','AchillesSequenceQCReport.csv']
def digest(path, kind):
    h=hashlib.new(kind)
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def main():
    meta=json.loads((ROOT/'setup/sources/depmap-24q2-v1.json').read_text())
    assert meta['license']['name']=='CC BY 4.0' and meta['version']==1
    files=[f for f in meta['files'] if f['name'] in NAMES]
    assert len(files)==len(NAMES)
    assert sum(f['size'] for f in files)<1_300_000_000
    def get(f):
        p=ROOT/'data/raw'/f['name']; p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            tmp=p.with_suffix('.part')
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(f['download_url'], timeout=120) as r, tmp.open('wb') as out:
                        while b:=r.read(1024*1024): out.write(b)
                    break
                except Exception:
                    if attempt==2: raise
                    time.sleep(2)
            assert tmp.stat().st_size==f['size'], f['name']
            assert digest(tmp,'md5')==f['computed_md5'], f['name']
            tmp.rename(p)
        assert p.stat().st_size==f['size'] and digest(p,'md5')==f['computed_md5']
        print('Verified', f['name'],p.stat().st_size,flush=True)
        return {'name':f['name'],'bytes':f['size'],'md5':f['computed_md5'],
                'sha256':digest(p,'sha256'),'url':f['download_url']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        got=list(pool.map(get,files))
    (ROOT/'data/source-lock.json').write_text(json.dumps({'doi':meta['doi'],'license':meta['license'],
        'article_version':1,'files':sorted(got,key=lambda f:f['name'])},indent=2)+'\n')
if __name__=='__main__': main()
