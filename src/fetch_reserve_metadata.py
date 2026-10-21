"""Optional reconstruction of four pinned metadata files; no outcome downloads."""
import hashlib,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021/sources'
ALLOW=('Model.csv','CRISPRScreenMap.csv','AchillesScreenQCReport.csv','OmicsDefaultModelProfiles.csv')
def main():
    article=json.loads((OUT/'depmap-24q4-v1.json').read_text())
    if article['doi']!='10.25452/figshare.plus.27993248.v1' or article['license']['name']!='CC BY 4.0':raise ValueError('Unexpected release/license')
    for name in ALLOW:
        f=next(f for f in article['files'] if f['name']==name);path=OUT/name
        raw=path.read_bytes() if path.exists() else urllib.request.urlopen(f['download_url'],timeout=60).read()
        if len(raw)!=f['size'] or hashlib.md5(raw).hexdigest()!=f['computed_md5']:raise ValueError('Publisher checksum mismatch: '+name)
        if not path.exists():path.write_bytes(raw)
        print('PASS',name,len(raw))
if __name__=='__main__':main()
