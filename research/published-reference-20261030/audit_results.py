"""Separate arithmetic audit of this package from committed files only; no fitting, no raw data.

Recomputes every reported Spearman/Pearson/MSE from development.csv outcomes and the saved
OOF predictions, checks complete single coverage of all 773 identities per target, outer-fold
identity separation against the saved wide300 folds, and that each chosen lambda is the
first minimum of its recorded inner MSE curve.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def main():
    load=lambda name:json.loads((HERE/name).read_text())
    res,adapted,exact,price=load('results.json'),load('adapted.json')['targets'],load('exact.json')['targets'],load('price.json')['targets']
    wide=json.loads((ROOT/'research/wide-expression-20261021/models.json').read_text())
    dev=pd.read_csv(ROOT/'research/readiness-20261021/development.csv')
    ids=dev.model_id.tolist();checked=0;worst=0.
    for t,row in res['targets'].items():
        y=dev['y:'+t].to_numpy(float);assert np.isfinite(y).all() and len(y)==773
        seen=[i for f in adapted[t]['folds'] for i in f['test_ids']]
        assert sorted(seen)==sorted(ids) and len(seen)==len(set(seen)),'coverage '+t
        saved=[f['test_ids'] for f in wide['targets'][t]['folds']]
        assert [f['test_ids'] for f in adapted[t]['folds']]==saved,'outer folds differ '+t
        for f in adapted[t]['folds']:
            curve=np.array(f['inner_mse']);assert f['lambda_index']==int(np.argmin(curve)),'lambda choice '+t
            assert f['nonzero']==len(f['coefficients'])
        preds={'elastic_net':np.array(adapted[t]['oof'])}
        preds.update({s:np.array(wide['targets'][t]['oof_predictions'][s]) for s in ['wide300','panel30','lineage']})
        for s,v in preds.items():
            got={'spearman':stats.spearmanr(y,v)[0],'pearson':stats.pearsonr(y,v)[0],'mse':float(np.mean((y-v)**2))}
            for k,value in got.items():
                worst=max(worst,abs(value-row[s][k]));checked+=1
        curve=np.array(price[t]['spearman_by_position'],dtype=float)
        assert abs(np.nanmax(curve)-row['stage1_ceiling_spearman'])==0
        assert exact[t]['lambda_index']==int(np.argmin(exact[t]['inner_mse']))
    means={s:float(np.mean([res['targets'][t][s]['spearman'] for t in res['targets']])) for s in ['elastic_net','wide300','panel30','lineage']}
    for s,v in means.items():worst=max(worst,abs(v-res['aggregate'][s]['spearman']))
    worst=max(worst,abs(means['elastic_net']-means['wide300']-res['primary_elastic_net_minus_wide300']))
    assert worst<1e-12,worst
    print('PASS',checked,'per-target metrics,',len(res['targets']),'targets x 773 identities, max abs difference',worst)
    print('mean Spearman',{k:round(v,6) for k,v in means.items()})


if __name__=='__main__':main()
