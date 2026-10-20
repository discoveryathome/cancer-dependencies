# Initial benchmark results

All findings are computational research hypotheses. This report covers a predeclared 12-target panel, not a genome-wide search. No new drug target, causal interaction, normal-cell sparing, or independent biological validation is established.

The corrected primary cohort has 967 independent model groups: 773 development and 194 final. The disjoint Sanger transfer cohort has 49 groups. Models were frozen before final scoring. See config/PREREGISTRATION.md and the git record for eligibility corrections before final inspection.

| Target | Frozen rule feature | Final skill vs lineage | 95% paired CI | Development q | Positive outer folds | Positive lineage holdouts | Pilot gate |
|---|---|---:|---|---:|---:|---:|---|
| BRAF | hotspot:BRAF | 51.1% | [19.2%, 68.8%] | 0.006 | 100% | 82% of 17 | pass |
| KRAS | hotspot:KRAS | 38.0% | [18.2%, 53.5%] | 0.006 | 100% | 88% of 17 | pass |
| NRAS | hotspot:NRAS | 31.9% | [-44.1%, 68.3%] | 0.006 | 100% | 94% of 17 | fail |
| EGFR | expr:EPCAM | 6.5% | [-4.4%, 13.4%] | 0.006 | 13% | 76% of 17 | fail |
| ERBB2 | expr:ERBB2 | 1.0% | [-18.8%, 16.2%] | 0.0109 | 33% | 82% of 17 | fail |
| PIK3CA | hotspot:PIK3CA | 19.4% | [3.6%, 33.1%] | 0.006 | 60% | 76% of 17 | fail |
| SMARCA2 | damaging:SMARCA4 | 10.6% | [-7.7%, 29.8%] | 0.006 | 100% | 59% of 17 | fail |
| SMARCA4 | expr:SMARCA2 | 5.8% | [-4.3%, 14.9%] | 0.006 | 80% | 71% of 17 | fail |
| ARID1B | damaging:ARID1A | 22.7% | [9.1%, 31.6%] | 0.006 | 93% | 76% of 17 | pass |
| STAG1 | expr:ARID1A | -7.4% | [-18.0%, 2.4%] | 0.35 | 7% | 41% of 17 | fail |
| MDM2 | damaging:TP53 | 44.2% | [30.9%, 54.7%] | 0.006 | 93% | 88% of 17 | pass |
| PRMT5 | expr:MTAP | 1.7% | [-5.4%, 8.4%] | 0.006 | 80% | 76% of 17 | fail |

Skill = 1 − model MSE / lineage-baseline MSE. Negative values are worse than lineage. Intervals are conditional, per comparison, and not simultaneous. The development q-values use 199 within-lineage permutations with complete candidate reselection and BH across all 12 targets; p-value resolution is 0.005. Passing all screening gates does not establish novelty or a formal final-discovery FDR.

## Exact compact rules

Expression thresholds are in log2(TPM+1), CN is the provided absolute estimate, and mutation features are binary presence. Smaller predicted gene-effect values indicate greater dependency. Missing features use the saved development median; this can hide biologically important uncertainty.

| Target | Condition | Prediction when true | Otherwise | Final leaf counts |
|---|---|---:|---:|---|
| BRAF | hotspot:BRAF ≤ 0.5 | -0.2285 | -1.6019 | [176, 18] |
| KRAS | hotspot:KRAS ≤ 0.5 | -0.6046 | -1.9818 | [160, 34] |
| NRAS | hotspot:NRAS ≤ 0.5 | -0.1710 | -1.7520 | [187, 7] |
| EGFR | expr:EPCAM ≤ 5.95388 | -0.0664 | -0.3387 | [111, 83] |
| ERBB2 | expr:ERBB2 ≤ 5.50874 | -0.3244 | -0.6438 | [156, 38] |
| PIK3CA | hotspot:PIK3CA ≤ 0.5 | -0.4610 | -0.9722 | [178, 16] |
| SMARCA2 | damaging:SMARCA4 ≤ 0.5 | 0.0999 | -0.3636 | [189, 5] |
| SMARCA4 | expr:SMARCA2 ≤ 4.36947 | -0.5510 | -0.3487 | [81, 113] |
| ARID1B | damaging:ARID1A ≤ 0.5 | -0.1140 | -0.3858 | [167, 27] |
| STAG1 | expr:ARID1A ≤ 4.93271 | -0.1450 | -0.2260 | [123, 71] |
| MDM2 | damaging:TP53 ≤ 0.5 | -1.2928 | -0.4671 | [79, 115] |
| PRMT5 | expr:MTAP ≤ 1.695 | -1.5765 | -1.3267 | [37, 157] |

## Baselines

| Target | Lowest final MSE model (descriptive) | MSE | Molecular features |
|---|---|---:|---:|
| BRAF | elastic_all | 0.07188 | 47 |
| KRAS | ridge_all | 0.18705 | 103 |
| NRAS | ridge_all | 0.05368 | 103 |
| EGFR | elastic_expr | 0.14433 | 17 |
| ERBB2 | ridge_all | 0.09596 | 103 |
| PIK3CA | elastic_all | 0.09554 | 71 |
| SMARCA2 | rule_all | 0.03497 | 1 |
| SMARCA4 | elastic_expr | 0.13296 | 22 |
| ARID1B | ridge_all | 0.05377 | 103 |
| STAG1 | elastic_all | 0.04995 | 53 |
| MDM2 | elastic_all | 0.18897 | 76 |
| PRMT5 | elastic_all | 0.15450 | 3 |

This retrospective ranking is descriptive and must not select a new model for the same test. Every baseline, failure and complexity count appears in research/initial/final_metrics.csv. Candidate rule grids and linear alpha scores are in search.json; all outer predictions are retained.

## Prospective contributor trial

| Fixed comparison | Aggregate error reduction | Paired 95% CI |
|---|---:|---|
| biology_pair_vs_best_linear | -2.1% | [-6.3%, 2.0%] |
| biology_pair_vs_blind_pair | -4.2% | [-6.1%, -2.2%] |
| biology_pair_vs_rule_all | -0.6% | [-3.4%, 2.6%] |

Trial's predeclared gate: FAIL. Positive development outer comparisons: 87%. The primary comparison is biology_pair versus rule_all; other comparisons are descriptive.

Targets are normalized by development variance, and cells are jointly resampled across targets. The pairs encode known biological priors. Improvement is a computational model result, not evidence of a novel biological relationship or a general advantage of agent intelligence.

## Independent-identity assay transfer

| Target | Sanger n | Rule skill vs lineage | 95% CI | Rule leaf support | Adequate support |
|---|---:|---:|---|---|---|
| BRAF | 49 | -151.0% | [-338.2%, -10.7%] | [44, 5] | False |
| KRAS | 49 | 27.3% | [-23.0%, 56.8%] | [36, 13] | False |
| NRAS | 49 | 69.0% | [4.9%, 84.6%] | [47, 2] | False |
| EGFR | 49 | -13.8% | [-41.8%, 10.7%] | [20, 29] | True |
| ERBB2 | 49 | -3.2% | [-36.5%, 5.7%] | [26, 23] | True |
| PIK3CA | 49 | 32.7% | [14.2%, 49.1%] | [37, 12] | False |
| SMARCA2 | 49 | -11.4% | [-33.0%, 0.8%] | [48, 1] | False |
| SMARCA4 | 49 | -16.3% | [-54.9%, 7.0%] | [18, 31] | True |
| ARID1B | 49 | 11.9% | [-33.4%, 31.2%] | [41, 8] | False |
| STAG1 | 49 | -13.0% | [-25.9%, 0.6%] | [30, 19] | True |
| MDM2 | 49 | 15.4% | [-33.6%, 50.4%] | [11, 38] | False |
| PRMT5 | 49 | 14.9% | [7.5%, 21.5%] | [7, 42] | False |

These are different experimental measurements in non-overlapping model identities, processed in the same public release. They are a small cross-laboratory transfer test, not a fully independent end-to-end data-processing replication. Both leaves need at least 15 observations for the displayed adequate-support flag. No external model recalibration is performed.

## Remaining uncertainty

- Shared upstream screen processing is outside fold-local fitting. Genetic dependency need not predict response to partial pharmacological inhibition.
- Complete-feature and within-lineage diagnostics are in reports/sensitivity.csv; pDNA batch holdouts are in reports/batch_holdouts.csv.
- All RNA profiles in the primary cohort are labeled BROAD, so an RNA-provider batch comparison is unavailable. pDNA batch and residual screen-quality checks cannot exclude every technical artifact.
- The panel is selected from familiar biology. Rare alleles, biallelic state, genome-wide candidates and normal controls are not represented adequately.
- A public final-test set becomes development evidence after repeated community inspection. New claims need fresh evaluation data or curator-controlled validation.
- No independent reviewer or consenting maintainer has accepted the results. Fresh-process checks establish computational reproducibility only.
