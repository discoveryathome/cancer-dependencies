"""Metadata-only feasibility audit of a later release; never load gene effects."""
import argparse,json,pathlib
import pandas as pd
from core import dumps,sha256
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'
IDENTIFIERS=('ModelID','PatientID','RRID','StrippedCellLineName','SangerModelID','COSMICID')
def components(records):
    parent=list(range(len(records)));seen={}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,row in enumerate(records):
        for col in IDENTIFIERS:
            value=str(row.get(col,'')).strip()
            if not value or value.lower() in ('nan','none','null'):continue
            if col=='COSMICID' and value.endswith('.0'):value=value[:-2]
            key=(col,value)
            if key in seen:parent[find(i)]=find(seen[key])
            else:seen[key]=i
    return [find(i) for i in range(len(records))]
def main():
    source=OUT/'sources';old=pd.read_csv(ROOT/'data/model-metadata.csv',dtype=str).fillna('');new=pd.read_csv(source/'Model.csv',dtype=str).fillna('')
    required=set(IDENTIFIERS)|{'OncotreeLineage','OncotreePrimaryDisease','EngineeredModel'}
    if not required<=set(new):raise ValueError('Changed metadata schema')
    records=old.to_dict('records')+new.to_dict('records');groups=components(records);prior=set(groups[:len(old)])
    qc=pd.read_csv(source/'AchillesScreenQCReport.csv',dtype=str).fillna('')
    screens=qc[(qc.ScreenPermissionToRelease=='True')&(qc.PassesQC=='True')&(qc.CanInclude=='True')&(qc.ScreenType=='2DS')]
    avana=set(screens.loc[screens.Library=='Avana','ModelID']);all_screened=set(screens.ModelID)
    omics=pd.read_csv(source/'OmicsDefaultModelProfiles.csv',dtype=str).fillna('')
    if not {'ProfileType','ModelID'}<=set(omics):raise ValueError('Changed omics profile schema')
    expression=set(omics.loc[omics.ProfileType=='rna','ModelID'])
    rows=[];excluded={};used=set()
    for offset,row in enumerate(new.to_dict('records')):
        group=groups[len(old)+offset];reason=None
        if group in prior:reason='identity connected to any 24Q2 metadata model'
        elif row['EngineeredModel'] or row['OncotreeLineage'] in ('','Normal','Fibroblast','Muscle','Hair','Other') or row['OncotreePrimaryDisease'] in ('','Non-Cancerous'):reason='cohort annotation exclusion'
        elif group in used:reason='same new identity component'
        if reason:excluded[reason]=excluded.get(reason,0)+1;continue
        used.add(group)
        rows.append(dict(model_id=row['ModelID'],lineage=row['OncotreeLineage'],passing_releasable_2ds=row['ModelID'] in all_screened,passing_avana_2ds=row['ModelID'] in avana,
          expression_profile_listed=row['ModelID'] in expression))
    files=['data/model-metadata.csv']+[str(p.relative_to(ROOT)) for p in sorted(source.iterdir()) if p.is_file()]
    result=dict(source='10.25452/figshare.plus.27993248.v1',license=json.loads((source/'depmap-24q4-v1.json').read_text())['license'],
      files={f:sha256(ROOT/f) for f in files},old_metadata_models=len(old),new_release_metadata_models=len(new),candidate_identities=len(rows),
      passing_avana=sum(r['passing_avana_2ds'] for r in rows),passing_any_2ds=sum(r['passing_releasable_2ds'] for r in rows),excluded=excluded,candidates=rows,
      passing_any_with_expression_profile=sum(r['passing_releasable_2ds'] and r['expression_profile_listed'] for r in rows),
      passing_avana_with_expression_profile=sum(r['passing_avana_2ds'] and r['expression_profile_listed'] for r in rows),
      status='Metadata-only proposed reserve; no outcome or molecular-feature matrices downloaded or evaluated.',
      limitations=['Not yet an eligible confirmation cohort: feature/target availability and rule-branch support remain unknown.','Same-program release transfer is not independent-laboratory validation.','All known identifiers from the entire old release are excluded, including historical final and external cases. Unknown identity relationships can remain.','Independent curator approval, algorithm freeze and source-processing compatibility review required before loading outcomes.'])
    (OUT/'cohort-reserve.json').write_text(dumps(result));print(dumps({k:v for k,v in result.items() if k not in ('files','candidates')}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        d=json.loads((OUT/'cohort-reserve.json').read_text())
        for name,h in d['files'].items():
            if sha256(ROOT/name)!=h:raise ValueError('Metadata binding changed')
        print('PASS metadata bindings;',d['passing_any_2ds'],'passing new screened identities; confirmation pending')
    else:main()
