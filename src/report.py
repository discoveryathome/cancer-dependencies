"""Generate transparent result tables; qualitative interpretation is separately reviewed."""
import json,pathlib
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    decisions=json.loads((ROOT/'research/initial/decisions.json').read_text())
    trial=json.loads((ROOT/'research/contributor-trial/summary.json').read_text())
    base=pd.read_csv(ROOT/'research/initial/final_metrics.csv')
    ext=json.loads((ROOT/'reports/external_uncertainty.json').read_text())
    cohort=json.loads((ROOT/'reports/data_audit.json').read_text())
    rows=['# Initial benchmark results','',
      'All findings are computational research hypotheses. This report covers a predeclared 12-target panel, not a genome-wide search. No new drug target, causal interaction, normal-cell sparing, or independent biological validation is established.','',
      f"The corrected primary cohort has {cohort['Avana']['independent_groups']} independent model groups: {cohort['split_counts']['development']} development and {cohort['split_counts']['final']} final. The disjoint Sanger transfer cohort has {cohort['distinct_sanger_groups']} groups. Models were frozen before final scoring. See config/PREREGISTRATION.md and the git record for eligibility corrections before final inspection.",'',
      '| Target | Frozen rule feature | Final skill vs lineage | 95% paired CI | Development q | Positive outer folds | Positive lineage holdouts | Pilot gate |',
      '|---|---|---:|---|---:|---:|---:|---|']
    for d in decisions:
        rule=d['rule'];feature=', '.join(rule.get('features',[])) or 'constant'
        rows.append(f"| {d['target']} | {feature} | {d['final_skill']:.1%} | [{d['final_ci'][0]:.1%}, {d['final_ci'][1]:.1%}] | {d['permutation_q']:.3g} | {d['outer_positive_fraction']:.0%} | {d['lineage_positive_fraction']:.0%} of {d['eligible_lineages']} | {'pass' if d['passes_pilot_gate'] else 'fail'} |")
    rows+=['','Skill = 1 − model MSE / lineage-baseline MSE. Negative values are worse than lineage. Intervals are conditional, per comparison, and not simultaneous. The development q-values use 199 within-lineage permutations with complete candidate reselection and BH across all 12 targets; p-value resolution is 0.005. Passing all screening gates does not establish novelty or a formal final-discovery FDR.','',
      '## Exact compact rules','',
      'Expression thresholds are in log2(TPM+1), CN is the provided absolute estimate, and mutation features are binary presence. Smaller predicted gene-effect values indicate greater dependency. Missing features use the saved development median; this can hide biologically important uncertainty.','',
      '| Target | Condition | Prediction when true | Otherwise | Final leaf counts |',
      '|---|---|---:|---:|---|']
    for d in decisions:
        r=d['rule']
        if r['kind']=='rule': rows.append(f"| {d['target']} | {r['features'][0]} ≤ {r['threshold']:.6g} | {r['left']:.4f} | {r['right']:.4f} | {d['final_support']} |")
    rows+=['','## Baselines','', '| Target | Lowest final MSE model (descriptive) | MSE | Molecular features |', '|---|---|---:|---:|']
    for target,group in base.groupby('target',sort=False):
        r=group.loc[group.mse.idxmin()]
        rows.append(f'| {target} | {r.model} | {r.mse:.5f} | {r.molecular_features} |')
    rows+=['','This retrospective ranking is descriptive and must not select a new model for the same test. Every baseline, failure and complexity count appears in research/initial/final_metrics.csv. Candidate rule grids and linear alpha scores are in search.json; all outer predictions are retained.','',
      '## Prospective contributor trial','',
      '| Fixed comparison | Aggregate error reduction | Paired 95% CI |', '|---|---:|---|']
    for key,v in trial['comparisons'].items():
        if key.startswith('biology_pair_'):
            rows.append(f"| {key} | {v['normalized_mse_skill']:.1%} | [{v['ci95'][0]:.1%}, {v['ci95'][1]:.1%}] |")
    rows+=[f"\nTrial's predeclared gate: {'PASS' if trial['passes_trial_gate'] else 'FAIL'}. Positive development outer comparisons: {trial['outer_positive_fraction']['biology_pair']:.0%}. The primary comparison is biology_pair versus rule_all; other comparisons are descriptive.",
      '', 'Targets are normalized by development variance, and cells are jointly resampled across targets. The pairs encode known biological priors. Improvement is a computational model result, not evidence of a novel biological relationship or a general advantage of agent intelligence.','',
      '## Independent-identity assay transfer','',
      '| Target | Sanger n | Rule skill vs lineage | 95% CI | Rule leaf support | Adequate support |',
      '|---|---:|---:|---|---|---|']
    for d in ext:
        if d['model']=='rule_all':
            rows.append(f"| {d['target']} | {d['n']} | {d['skill']:.1%} | [{d['skill_ci95'][0]:.1%}, {d['skill_ci95'][1]:.1%}] | {d['rule_support']} | {d['rule_support_adequate']} |")
    rows+=['','These are different experimental measurements in non-overlapping model identities, processed in the same public release. They are a small cross-laboratory transfer test, not a fully independent end-to-end data-processing replication. Both leaves need at least 15 observations for the displayed adequate-support flag. No external model recalibration is performed.','',
      '## Remaining uncertainty','',
      '- Shared upstream screen processing is outside fold-local fitting. Genetic dependency need not predict response to partial pharmacological inhibition.',
      '- Complete-feature and within-lineage diagnostics are in reports/sensitivity.csv; pDNA batch holdouts are in reports/batch_holdouts.csv.',
      '- All RNA profiles in the primary cohort are labeled BROAD, so an RNA-provider batch comparison is unavailable. pDNA batch and residual screen-quality checks cannot exclude every technical artifact.',
      '- The panel is selected from familiar biology. Rare alleles, biallelic state, genome-wide candidates and normal controls are not represented adequately.',
      '- A public final-test set becomes development evidence after repeated community inspection. New claims need fresh evaluation data or curator-controlled validation.',
      '- No independent reviewer or consenting maintainer has accepted the results. Fresh-process checks establish computational reproducibility only.','']
    (ROOT/'reports/RESULTS.md').write_text('\n'.join(rows))
    print('Wrote reports/RESULTS.md')
if __name__=='__main__':main()
