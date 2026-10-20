"""Static, exportable public explanation derived only from frozen results."""
import os
os.environ['MPLCONFIGDIR']=str(__import__('pathlib').Path(__file__).resolve().parents[1]/'setup/matplotlib-cache')
import json,pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core import predict
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'reports'; f=pd.read_csv(ROOT/'data/panel/primary.csv'); test=f[f.partition=='final']
    base=json.loads((ROOT/'research/initial/frozen.json').read_text())
    trial=json.loads((ROOT/'research/contributor-trial/frozen.json').read_text())
    summary=json.loads((ROOT/'research/contributor-trial/summary.json').read_text())
    targets=list(trial['scales']); labels=['Training mean','Cancer lineage','One-feature rule','Biology pair','Blind pair','Best linear baseline']
    names=['mean','lineage','rule_all','biology_pair','blind_pair','best_linear']; scores=[]
    for name in names:
        ls=[]
        for t in targets:
            m=trial['models'][t][name] if name in ['biology_pair','blind_pair'] else base['models'][t][trial['best_linear'][t] if name=='best_linear' else name]
            te=test[test['y:'+t].notna()]; ls.append(float(np.mean((te['y:'+t]-predict(m,te))**2)/trial['scales'][t]))
        scores.append(np.mean(ls))
    scores=np.array(scores)/scores[0]*100
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,5.2),layout='constrained')
    colors=['#aeb9c5','#889bac','#4477aa','#008877','#d49624','#65718c']
    bars=ax.barh(labels[::-1],scores[::-1],color=colors[::-1],height=.65)
    ax.axvline(100,color='#718096',ls=':',lw=1);ax.set_xlim(0,max(108,scores.max()+12))
    for bar,v in zip(bars,scores[::-1]):ax.text(v+1,bar.get_y()+bar.get_height()/2,f'{v:.1f}',va='center',fontsize=11)
    ax.set_xlabel('Held-out prediction error (training-mean baseline = 100; lower is better)')
    ax.set_title('Can a few molecular clues predict cancer-cell dependencies?',loc='left',fontsize=16,pad=18)
    fig.text(.01,-.045,'12 prespecified genes • 194 held-out model groups • DepMap 24Q2 Avana\nKnown biological priors; computational prediction only. No new drug target is established.',fontsize=10,color='#445566')
    fig.savefig(out/'public-demo.png',dpi=170,bbox_inches='tight');fig.savefig(out/'public-demo.svg',bbox_inches='tight');plt.close(fig)
    # All target-level comparisons remain visible; no cherry-picked leaderboard.
    bm=pd.read_csv(ROOT/'research/initial/final_metrics.csv');tm=pd.read_csv(ROOT/'research/contributor-trial/final_metrics.csv')
    records=[]
    for t in targets:
        b=bm[(bm.target==t)&(bm.model=='rule_all')].iloc[0]
        p=tm[(tm.target==t)&(tm.model=='biology_pair')].iloc[0]
        records.append((t,b.skill,1-p.mse/bm[(bm.target==t)&(bm.model=='lineage')].iloc[0].mse))
    fig,ax=plt.subplots(figsize=(10,6),layout='constrained');pos=np.arange(len(records))
    ax.barh(pos-.18,[r[1]*100 for r in records],height=.34,label='One-feature rule',color='#4477aa')
    ax.barh(pos+.18,[r[2]*100 for r in records],height=.34,label='Biology pair',color='#008877')
    ax.set_yticks(pos,[r[0] for r in records]);ax.axvline(0,color='black',lw=.8)
    ax.set_xlabel('Held-out MSE improvement over cancer-lineage baseline (%)')
    ax.set_title('Improvements and failures across all 12 targets',loc='left',fontsize=16)
    ax.legend(frameon=False);fig.savefig(out/'all-targets.png',dpi=170);plt.close(fig)
    (out/'figure-values.json').write_text(json.dumps({'public_demo_labels':labels,'relative_error':scores.tolist(),
        'normalization':'Target MSE divided by development target variance; macro mean, then scaled to training-mean baseline 100.',
        'not_a_learning_curve':'All methods were frozen before the same final evaluation. The figure is not a sequence of adaptive test-set improvements.'},indent=2)+'\n')
    print('Wrote static PNG/SVG public demo and all-target comparison.')
if __name__=='__main__': main()
