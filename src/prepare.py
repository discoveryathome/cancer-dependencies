"""Deterministic, outcome-association-blind cohort and panel extraction."""
import json, pathlib
import numpy as np
import pandas as pd
from core import dumps,sha256
ROOT=pathlib.Path(__file__).resolve().parents[1]

def read_genes(name, genes, prefix, mapping):
    path=ROOT/'data/raw'/name
    header=pd.read_csv(path,nrows=0).columns.tolist()
    cols=[c for c in header[1:] if c.split(' (')[0] in genes]
    symbols=[c.split(' (')[0] for c in cols]
    assert len(symbols)==len(set(symbols)), 'Ambiguous gene symbol'
    mapping[prefix]={s:c for s,c in zip(symbols,cols)}
    f=pd.read_csv(path,usecols=[header[0]]+cols).set_index(header[0])
    assert not f.index.duplicated().any(),name
    f.columns=[prefix+':'+c.split(' (')[0] for c in f.columns]
    return f

def identity_groups(m):
    parent={x:x for x in m.ModelID}
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for col in ['PatientID','RRID','StrippedCellLineName','SangerModelID','COSMICID']:
        for _,part in m[m[col].notna()].groupby(col):
            ids=part.ModelID.tolist()
            for x in ids[1:]:
                a,b=find(ids[0]),find(x); parent[max(a,b)]=min(a,b)
    return m.ModelID.map(lambda x:find(x))

def main():
    cfg=json.loads((ROOT/'config/benchmark.json').read_text()); mapping={}
    source=json.loads((ROOT/'data/source-lock.json').read_text())
    for row in source['files']:
        if sha256(ROOT/'data/raw'/row['name'])!=row['sha256']: raise ValueError('Source changed')
    m=pd.read_csv(ROOT/'data/raw/Model.csv'); m['group']=identity_groups(m)
    eligible=m.EngineeredModel.isna() & m.OncotreeLineage.notna() & ~m.OncotreeLineage.isin(['Normal','Fibroblast','Muscle','Hair','Other'])
    meta=m.loc[eligible,['ModelID','group','OncotreeLineage']].rename(columns={'ModelID':'model_id','OncotreeLineage':'lineage'}).set_index('model_id')
    blocks=[]
    for name,prefix in [('OmicsExpressionProteinCodingGenesTPMLogp1.csv','expr'),('OmicsAbsoluteCNGene.csv','cn'),
                         ('OmicsSomaticMutationsMatrixDamaging.csv','damaging'),('OmicsSomaticMutationsMatrixHotspot.csv','hotspot')]:
        f=read_genes(name,cfg['predictors'],prefix,mapping)
        if prefix in ['damaging','hotspot']:
            assert set(np.unique(f.to_numpy()[~np.isnan(f.to_numpy())]))<=set([0,1,2])
            f=f.where(f.isna(),(f>0).astype(float))
        blocks.append(f)
    features=pd.concat(blocks,axis=1)
    # Availability filter is specified before outcome inspection, never based on a target.
    expr_ids=blocks[0].index
    meta=meta.loc[meta.index.intersection(expr_ids)].join(features)
    profiles=pd.read_csv(ROOT/'data/raw/OmicsProfiles.csv')
    defaults=pd.read_csv(ROOT/'data/raw/OmicsDefaultModelProfiles.csv')
    rna=defaults[defaults.ProfileType=='rna'].merge(profiles[['ProfileID','Source']],on='ProfileID',validate='many_to_one')
    assert not rna.ModelID.duplicated().any()
    meta['expression_source']=meta.index.map(rna.set_index('ModelID').Source).fillna('unknown')
    screens=read_genes('ScreenGeneEffect.csv',cfg['targets'],'y',mapping)
    qc=pd.read_csv(ROOT/'data/raw/AchillesScreenQCReport.csv').set_index('ScreenID')
    assert not qc.index.duplicated().any()
    joined=screens.join(qc[['ModelID','Library','ScreenType','PassesQC','CanInclude','ScreenNNMD']],how='inner')
    joined=joined[(joined.PassesQC==True)&(joined.CanInclude==True)&(joined.ScreenType=='2DS')]
    outcomes=[c for c in joined if c.startswith('y:')]
    output={}; audit={}
    for library in ['Avana','KY']:
        s=joined[joined.Library==library]
        agg=s.groupby('ModelID')[outcomes+['ScreenNNMD']].median().rename(columns={'ScreenNNMD':'audit_screen_nnmd'})
        f=meta.join(agg,how='inner').rename_axis('model_id').reset_index().sort_values('model_id')
        before=len(f); f=f.drop_duplicates('group',keep='first').copy()
        f['library']=library
        output[library]=f
        audit[library]={'eligible_screens':len(s),'models_before_identity_dedup':before,'independent_groups':len(f)}
    primary=output['Avana']; external=output['KY']
    rng=np.random.default_rng(cfg['split_seed']); groups=sorted(primary.group)
    final=set(rng.permutation(groups)[:int(np.ceil(len(groups)*cfg['final_test_fraction']))])
    primary['partition']=np.where(primary.group.isin(final),'final','development')
    external['partition']=np.where(external.group.isin(set(primary.group)),'overlapping_assay','external')
    for name,f in [('primary',primary),('sanger',external)]:
        f.to_csv(ROOT/f'data/panel/{name}.csv',index=False,float_format='%.12g')
    audit.update({'distinct_sanger_groups':int((external.partition=='external').sum()),
        'overlapping_sanger_groups':int((external.partition!='external').sum()),
        'split_counts':primary.partition.value_counts().to_dict(),
        'lineage_counts':primary.groupby(['partition','lineage']).size().to_dict() if False else
            primary.groupby(['partition','lineage']).size().reset_index(name='n').to_dict('records'),
        'feature_count':len(features.columns),'missing_genes':{p:sorted(set(cfg['predictors'])-set(v)) for p,v in mapping.items() if p!='y'},
        'missingness':primary.filter(regex='^(expr|cn|damaging|hotspot):').isna().mean().to_dict(),
        'identity_policy':'Union PatientID, RRID, stripped name, SangerModelID, COSMICID; first ModelID per component per library',
        'screen_policy':'PassesQC and CanInclude; 2DS; median of eligible same-library screen gene effects',
        'caveat':'Upstream Chronos screen preprocessing is not refit within model folds; this is prediction from released processed assays.'})
    (ROOT/'reports/data_audit.json').write_text(dumps(audit))
    (ROOT/'data/gene-map.json').write_text(dumps(mapping))
    (ROOT/'data/panel-lock.json').write_text(dumps({str(p.relative_to(ROOT)):sha256(p) for p in sorted((ROOT/'data/panel').glob('*.csv'))}))
    print(dumps({k:v for k,v in audit.items() if k in ['Avana','KY','distinct_sanger_groups','split_counts','feature_count']}))
if __name__=='__main__': main()
