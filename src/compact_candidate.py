"""Editable contributor hook; receives one training fold and its outcomes.

Initially the existing blind two-feature ridge control. Keep at most three
molecular features. Source review is required: this API is not a sandbox.
"""
from trial import fit_pair
def fit(train,y,target,cfg):
    return fit_pair(train,y,target,'blind_pair',cfg,{'ridge_alphas':[1,10,100]})
