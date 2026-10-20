"""Compare scientific outputs of full replay, ignoring runtime/platform metadata."""
import argparse,json,pathlib
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('original');p.add_argument('replay');a=p.parse_args()
old=ROOT/a.original;new=ROOT/a.replay
files=['outer_metrics.csv','outer_predictions.csv','lineage_metrics.csv','final_metrics.csv','external_metrics.csv']
for name in files:
    x=pd.read_csv(old/name);y=pd.read_csv(new/name)
    pd.testing.assert_frame_equal(x,y,check_exact=False,rtol=1e-7,atol=1e-8)
for name in ['permutations.json','decisions.json','summary.json']:
    if not (old/name).exists(): continue
    def compare(x,y):
        if isinstance(x,dict):
            assert x.keys()==y.keys()
            for k in x: compare(x[k],y[k])
        elif isinstance(x,list):
            assert len(x)==len(y)
            for i,j in zip(x,y): compare(i,j)
        elif isinstance(x,(int,float)) and not isinstance(x,bool): np.testing.assert_allclose(x,y,rtol=1e-7,atol=1e-8)
        else: assert x==y,(x,y)
    compare(json.loads((old/name).read_text()),json.loads((new/name).read_text()))
print('PASS: full replay scientific outputs agree; timing/platform excluded.')
