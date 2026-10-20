"""Post-freeze descriptive diagnostics only; never selects a new model."""
import json,pathlib
import numpy as np
import pandas as pd
from core import dumps,metrics,predict
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    f=pd.read_csv(ROOT/'data/panel/primary.csv'); final=f[f.partition=='final']; rows=[]
    for run,families in [('initial',['rule_all']),('contributor-trial',['biology_pair','blind_pair'])]:
        frozen=json.loads((ROOT/f'research/{run}/frozen.json').read_text())
        base=json.loads((ROOT/'research/initial/frozen.json').read_text())
        for target,models in frozen['models'].items():
            for family in families:
                model=models[family]; te=final[final['y:'+target].notna()].copy()
                features=model.get('features',[])
                for label,part in [('all',te),('complete_features',te.dropna(subset=features))]:
                    if len(part)<2: continue
                    rows.append({'target':target,'family':family,'subset':label,**metrics(part['y:'+target],predict(model,part),predict(base['models'][target]['lineage'],part))})
                for lineage,part in te.groupby('lineage'):
                    if len(part)<10: continue
                    rows.append({'target':target,'family':family,'subset':'within:'+lineage,**metrics(part['y:'+target],predict(model,part),predict(base['models'][target]['lineage'],part))})
    pd.DataFrame(rows).to_csv(ROOT/'reports/sensitivity.csv',index=False,float_format='%.12g')
    print('Wrote',len(rows),'descriptive sensitivity rows; no models retuned.')
if __name__=='__main__':main()
