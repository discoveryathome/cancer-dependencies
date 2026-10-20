"""Uncertainty/support for untouched Sanger identities; descriptive, not retuning."""
import json,pathlib
import numpy as np
import pandas as pd
from core import bootstrap,dumps,metrics,predict,assert_disjoint
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    cfg=json.loads((ROOT/'config/benchmark.json').read_text()); primary=pd.read_csv(ROOT/'data/panel/primary.csv')
    external=pd.read_csv(ROOT/'data/panel/sanger.csv'); external=external[external.partition=='external']; assert_disjoint(primary,external)
    base=json.loads((ROOT/'research/initial/frozen.json').read_text());trial=json.loads((ROOT/'research/contributor-trial/frozen.json').read_text())
    rows=[]
    for i,target in enumerate(cfg['targets']):
        te=external[external['y:'+target].notna()];y=te['y:'+target].to_numpy()
        for name,model in [('rule_all',base['models'][target]['rule_all']),('biology_pair',trial['models'][target]['biology_pair']),('blind_pair',trial['models'][target]['blind_pair'])]:
            ref=predict(base['models'][target]['lineage'],te); pred=predict(model,te)
            ci=bootstrap(y,pred,ref,te.group,10101+i,2000)
            features=model.get('features',[]);support=None
            if model['kind']=='rule':
                x=te[features[0]].fillna(model['medians'][0]); left=int((x<=model['threshold']).sum());support=[left,len(te)-left]
            rows.append({'target':target,'model':name,**metrics(y,pred,ref),'skill_ci95':ci,'rule_support':support,
                'complete_feature_rows':int(te[features].notna().all(axis=1).sum()),
                'rule_support_adequate':bool(support is not None and min(support)>=cfg['min_leaf'] and len(te)>=cfg['min_external_n'])})
    (ROOT/'reports/external_uncertainty.json').write_text(dumps(rows));print('Wrote',len(rows),'external uncertainty/support records.')
if __name__=='__main__':main()
