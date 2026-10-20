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
    targets=list(trial['scales']); labels=['Average only','Cancer type only','One molecular clue','Two biology-chosen clues','Two data-chosen clues','Linear-model baseline']
    names=['mean','lineage','rule_all','biology_pair','blind_pair','best_linear']; scores=[]; loss_matrices=[]
    for name in names:
        ls=[]; matrix=[]
        for t in targets:
            m=trial['models'][t][name] if name in ['biology_pair','blind_pair'] else base['models'][t][trial['best_linear'][t] if name=='best_linear' else name]
            te=test[test['y:'+t].notna()]; losses=(te['y:'+t]-predict(m,te))**2/trial['scales'][t]; ls.append(float(np.mean(losses))); matrix.append(pd.Series(losses.to_numpy(),index=te.model_id))
        scores.append(np.mean(ls)); loss_matrices.append(pd.concat(matrix,axis=1).mean(axis=1).reindex(test.model_id).to_numpy())
    scores=np.array(scores)/scores[0]*100
    loss_matrices=np.asarray(loss_matrices); rng=np.random.default_rng(20261022); ix=rng.integers(0,len(test),size=(10000,len(test)))
    base_boot=loss_matrices[0][ix].mean(axis=1)
    intervals=np.array([np.quantile(v[ix].mean(axis=1)/base_boot*100,[.025,.975]) for v in loss_matrices])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,5.2),layout='constrained')
    colors=['#aeb9c5','#889bac','#4477aa','#008877','#d49624','#65718c']
    bars=ax.barh(labels[::-1],scores[::-1],color=colors[::-1],height=.65)
    ax.errorbar(scores[::-1],np.arange(len(scores)),xerr=np.array([scores-intervals[:,0],intervals[:,1]-scores])[:,::-1],fmt='none',ecolor='#263746',capsize=4,lw=1)
    ax.axvline(100,color='#718096',ls=':',lw=1);ax.set_xlim(0,max(108,scores.max()+12))
    for bar,v in zip(bars,scores[::-1]):ax.text(max(v,intervals[len(scores)-1-list(bars).index(bar),1])+1,bar.get_y()+bar.get_height()/2,f'{v:.1f}',va='center',fontsize=11)
    ax.set_xlabel('Held-out prediction error (average-only baseline = 100; lower is better)')
    ax.set_title('Can a few molecular clues predict cancer-cell dependencies?',loc='left',fontsize=16,pad=18)
    fig.text(.01,-.045,'12 prespecified genes • 194 held-out model groups • Whiskers: 95% cell-line bootstrap intervals\nCross-laboratory transfer remains unresolved. Computational predictions; no new drug target established.',fontsize=10,color='#445566')
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
    (out/'figure-values.json').write_text(json.dumps({'public_demo_labels':labels,'relative_error':scores.tolist(),'ci95':intervals.tolist(),
        'normalization':'Target MSE divided by development target variance; macro mean, then scaled to training-mean baseline 100.',
        'not_a_learning_curve':'All methods were frozen before the same final evaluation. The figure is not a sequence of adaptive test-set improvements.'},indent=2)+'\n')
    external=json.loads((ROOT/'reports/external_uncertainty.json').read_text())
    e=next(d for d in external if d['target']=='BRAF' and d['model']=='rule_all')
    b=bm[(bm.target=='BRAF')&(bm.model=='rule_all')].iloc[0]
    values=np.array([b.skill,e['skill']])*100;low=np.array([b.skill_ci_low,e['skill_ci95'][0]])*100;high=np.array([b.skill_ci_high,e['skill_ci95'][1]])*100
    fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
    ax.barh(['Held-out Avana cells\n194 model groups','Disjoint Sanger cells\n49 model groups'],values,color=['#4477aa','#ba5b49'])
    ax.errorbar(values,[0,1],xerr=[values-low,high-values],fmt='none',color='#263746',capsize=5)
    ax.axvline(0,color='black',lw=.8);ax.set_xlabel('BRAF-rule error reduction vs cancer-type baseline (%)')
    ax.set_title('A rule can succeed in one cohort and fail to transfer',loc='left',fontsize=15)
    fig.text(.01,-.055,'Same frozen hotspot rule; no recalibration. Only 5 Sanger models carry a BRAF hotspot.\nA variant-class or assay explanation is a follow-up hypothesis, not an established cause.',fontsize=10,color='#445566')
    fig.savefig(out/'transfer-check.png',dpi=170,bbox_inches='tight');plt.close(fig)
    print('Wrote static PNG/SVG public demo, all-target comparison and transfer check.')
if __name__=='__main__': main()
