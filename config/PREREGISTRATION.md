# Preregistration, pilot v1

Frozen before response associations or model performance are inspected. The configuration
fixes 12 response genes, 30 molecular predictor genes, and 3 seeds × 5 development outer
folds. This is a restricted feasibility panel, not a genome-wide discovery survey.

Targets cover oncogene addictions and known paralog dependencies. Broad classes are
supported by the sources in setup/RESEARCH_BRIEF.md; pairs such as SMARCA4–SMARCA2
are positive controls, not novelty. The candidate universe is all available panel gene ×
modality pairs, including unrelated and cross-lineage pairs as exploratory hypotheses.
Absolute CN is the provided PureCN estimate, expression is log2(TPM+1), and damaging and
hotspot mutation calls are binary presence (>0), keeping missing calls missing. No claim
that any gene-level mutation means a specific activating allele or biallelic loss is made.

Eligibility: release-authorized passing 2DS screens; Avana primary; remove annotated
engineered models, normal/non-cancer lineage categories, and models whose primary disease
is Non-Cancerous or missing; require an expression row. The disease-label filter corrects
an eligibility implementation omission detected before final-test inspection (see SESSION.md).
Unknown engineered status is not evidence of absence. Identity union and one deterministic
representative per identity/component prevent related models from crossing partitions.
Use a seeded 20% group test partition; all discovery and null permutations use development
only. All eligible nonmissing target outcomes in a partition must be reported.

Primary candidate: one molecular threshold rule, selected by threefold inner validation
across the finite set of expression/CN quantiles (0.2,0.4,0.6,0.8) and mutation threshold
0.5. Thresholds and leaf predictions fit only training data; minimum 15 training samples
per leaf. Invalid candidates fall back to the training mean and cannot win ties over a
valid equally good candidate. Evaluate ablations for expression, copy number, and mutations.
A rule has one molecular feature, one threshold and two leaf predictions. No interactions
are searched in this initial pass; extension to 2–3 features is future work.

Baselines: training mean; lineage mean shrunk by 10 observations toward the global mean
(unseen lineage falls back to global); self-expression linear regression; expression and
multi-omics ridge and elastic net. Training-only median imputation and standardization.
Alpha grids and l1 ratio are fixed in benchmark.json. Hyperparameters use the same inner
folds as the rules. No batch or outcome quality variable is a predictor.

Primary comparison is per-target rule_all MSE skill relative to lineage baseline. A candidate
passes the pilot gate only if final skill >=0.05, paired group-bootstrap 95% CI lower bound
>0, development selection-aware within-lineage permutation BH q<=0.05 (12 targets),
>=80% of the 15 development outer folds improve on lineage, and >=50% of eligible
leave-one-lineage-out development tests improve on a training global mean. Report exact
support and rule-selection stability. These are screening gates, not evidence of a drug target.
Secondary model comparisons and modality ablations are descriptive, with no significance claims.

Permutation test: 199 permutations within development lineage groups; one representative
per identity makes this an independent-unit shuffle. Rerun the complete rule_all candidate
selection in the fixed inner CV for each permutation. Statistic is best inner OOF MSE
improvement over lineage OOF MSE. Compare to observed same statistic using (b+1)/(B+1).
This tests additional predictive signal within lineage conditional on these permutations;
no claim that it adjusts unknown batch covariates. All 12 target p-values enter BH.
Limited p-value resolution is disclosed. Bootstrap final samples by identity (2,000 draws)
conditional on the fitted models; it does not capture training-set variability. The outer
folds measure stability but are correlated, not 15 independent experiments.

Freeze a development-selected rule for every target before opening the final outcomes.
Keep final results for all targets; no post-test retuning. Cross-lineage testing is performed
on development only (lineage >=25 observations and remaining train >=200). Sanger transfer
uses identities absent from the entire Avana cohort; no cross-assay recalibration. Assess
same-line remeasurement separately, never count it as independent validation. External
claims require >=30 eligible models and adequate observed rule support in both leaves.

Runtime bound: finite 12-target panel, 15 outer folds, 3 inner folds, 199 permutations.
A fast replay verifies frozen models, all predictions and metrics; full replay reruns search.
No global genome-wide expansions, raw guide downloads, experimental design, publishing,
or donor intake are authorized by the local pilot.
