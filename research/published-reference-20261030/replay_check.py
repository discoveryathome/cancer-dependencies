"""Replay chosen targets from the raw expression matrix and compare with the saved stage outputs.

usage: replay_check.py STAGE TARGET...   (STAGE: price, adapted or exact)
Needs the pinned 24Q2 matrix and `shi_elastic_net.py extract`; adapted also needs the stage 1 path cache.
"""
import json
import sys

import numpy as np

import shi_elastic_net as s


def main():
    stage,targets=sys.argv[1],sys.argv[2:]
    saved=json.loads((s.HERE/f'{stage}.json').read_text())['targets']
    func={'price':s.price_target,'adapted':s.adapted_target,'exact':s.exact_target}[stage]
    for target in targets:
        _,got=func(target);want=saved[target]
        if stage=='price':
            path=np.load(s.PATHS)[target];diff=float(np.max(np.abs(got['path_oof']-path)))
            same=got['spearman_by_position']==want['spearman_by_position'] and got['best_position']==want['best_position']
        elif stage=='adapted':
            diff=float(np.max(np.abs(np.array(got['oof'])-np.array(want['oof']))))
            same=[f['lambda_index'] for f in got['folds']]==[f['lambda_index'] for f in want['folds']]
        else:
            diff=abs(got['resubstitution_pearson']-want['resubstitution_pearson'])
            same=got['lambda_index']==want['lambda_index'] and got['nonzero']==want['nonzero']
        print('REPLAY',stage,target,'max_abs_difference',diff,'selection_identical',same,flush=True)
        if diff>1e-10 or not same:raise SystemExit('FAIL replay '+stage+' '+target)
    print('PASS replay',stage,targets)


if __name__=='__main__':main()
