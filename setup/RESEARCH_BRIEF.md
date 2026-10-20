# Cancer-dependency pilot: pre-build research brief

Status: proposed LOCAL pilot; awaiting the setup playbook's pre-build confirmation.
Research date: 2026-10-20. No benchmark has been run and no biological result is claimed.

## Exact question and scope

Can a rule using at most three molecular features predict measured CRISPR gene-effect scores in previously unseen cancer cell lines, improve on a training-only mean and lineage baseline, and retain useful performance when entire cancer lineages are held out? Compare against regularized linear models and established biomarker controls. Evaluate mutation, expression, and copy-number features separately and together.

This addresses context-selective dependencies within cancer models. Without suitable normal-cell controls, this pilot cannot establish cancer-versus-normal selectivity, a therapeutic window, or a validated drug target. All candidate findings are computational research hypotheses. No new biological experiments or constructs are in scope.

## What is already known; claim audit

1. **Confirmed: molecular features can predict some cancer dependencies.** Shi et al., Nature Cancer (2024), https://doi.org/10.1038/s43018-024-00789-y, report 2,045 multi-omics elastic-net models meeting their tenfold cross-validation criteria among 7,260 attempted genes (Pearson r > 0.2; FDR < 0.001). Median selected feature count was 98. Most successful models performed comparably with expression alone. These are literature results under that paper's protocol, not scores reproduced here, and not a directly comparable benchmark leaderboard.
2. **Confirmed: independent CRISPR screens can agree, with material technical differences.** Dempster et al. (2019), https://doi.org/10.1038/s41467-019-13805-y, compare independent Broad/Sanger screens including 147 common cell lines. Pacini et al. (2021), https://doi.org/10.1038/s41467-021-21898-7, study cross-study integration, copy-number artifacts, and batch effects. Batch correction is not evidence that a prediction generalizes.
3. **Confirmed: an openly licensed, versioned starting dataset exists.** DepMap, Broad (2024), DepMap 24Q2 Public, https://doi.org/10.25452/figshare.plus.25880521.v1. The publisher's API records CC BY 4.0: https://api.figshare.com/v2/articles/25880521/versions/1. The original metadata and release README are saved alongside this brief. Licenses must be checked separately for each additional source; this is not a blanket claim about all DepMap or CCLE data.
4. **Confirmed: integrated gene effects already include Sanger.** The 24Q2 README explicitly says CRISPRGeneEffect combines the screening libraries with joint Chronos fitting. It also supplies ScreenGeneEffect processed per library/screen type. Consequently Sanger cannot be labeled independent validation of models trained on the combined matrix. Use an Avana-only primary cohort from screen-level scores, with Sanger KY treated as a secondary assay transfer check only after provenance and overlap audits.
5. **Confirmed: processed screen scores are estimates, not raw survival probabilities.** Dempster et al., Chronos (2021), https://doi.org/10.1186/s13059-021-02540-7. The release describes correction and scaling. Dependency probabilities also use expression-derived nulls; prefer continuous gene effects as the response to reduce direct circularity when expression is a predictor.
6. **Confirmed: familiar paralog associations are prior knowledge.** For example SMARCA4 loss/SMARCA2 dependency predates this pilot: Helming et al. (2014), https://pmc.ncbi.nlm.nih.gov/articles/PMC3958034/. Rediscovery is a positive control, not novelty.
7. **Unverified/open: agents can find a compact, previously unreported rule that adds held-out predictive value beyond these baselines.** Neither existing literature nor a successful code run establishes this. Novelty requires a candidate-specific literature audit and independent review.

The broad existence question is already answered affirmatively for some genes. The user's requested emphasis on compactness and reproducibility supplies the meaningful remaining question; this pilot does not claim a new general capability to predict dependency.

## Proposed preregistered benchmark

- Freeze a literature-motivated pilot panel of targets and predictor genes before examining their response associations. Include documented positive controls and exploratory pairs; disclose the restricted search space and count every candidate evaluated.
- Pin release, source files, byte counts, hashes, feature encodings, gene identifiers, missingness rules, cohort filters, software, and random seeds. Mutation-matrix missing values stay missing; no mutation-call row must not silently become wild type.
- Use screen metadata to isolate Avana primary outcomes, aggregate eligible replicate screens consistently, and group related models by source identity/PatientID. Audit aliases and duplicates across all splits. Do not feed dependencies of other genes or post-screen quality metrics into biomarker models.
- Reserve a locked final test cohort before model selection. Within development data, use repeated grouped outer folds and inner-fold selection. Separately evaluate whole-lineage holdouts. Fit imputation, scaling, feature filtering, thresholds, and tuning only within the relevant training fold. Holdout labels must not determine the gene panel or missingness filters.
- Baselines: training mean, shrinkage lineage mean, self-expression linear predictor, ridge and elastic net (expression-only and multi-omics). Candidates: one-feature threshold rules and shallow trees with a strict feature/leaf budget; record exact rules, thresholds, support, leaves, and number of fitted parameters.
- Primary score: held-out mean squared error improvement over the lineage baseline, alongside mean-baseline skill, R-squared, MAE, and correlation. Report per-target and per-lineage scores, not only pooled correlations. Final comparisons use a prespecified minimum practical effect and uncertainty criterion, fixed before unsealing the test.
- Quantify paired uncertainty by resampling independent biological groups. Repeated folds are dependent: do not treat fold scores as independent observations. Use lineage-preserving label permutations that rerun candidate selection on development data; correct the complete tested family for multiplicity. Report all failed and null candidates.
- Audit lineage confounding with within-lineage baselines/permutations and lineage holdouts; batch effects with library/screen metadata and residual diagnostics. Any fitted harmonization uses training data only. Disclose upstream public-release joint preprocessing as a limitation, even when model fitting is leakage controlled.
- Sanger validation, if feasible: exclude every training/development biological identity and alias, retain only truly untouched models, freeze all rule parameters, and report sample/support limitations. Re-measurements of the same held-out line are assay reproducibility, not additional independent cell lines. If there are too few disjoint lines, report this limitation and use lineage validation without an external-replication claim.
- Computational reproducibility: a verifier recomputes predictions and scores from pinned small extracts and rejects an intentionally wrong result. A separate end-to-end command rebuilds extracts from licensed source files. Fresh-process replay establishes reproducibility, not independent scientific confirmation.

## Feasibility and governance

Use the older pinned CC BY release deliberately, rather than an unpinned latest release. Publisher file sizes for ScreenGeneEffect, expression, absolute copy number, damaging/hotspot mutations, and metadata total approximately 1.24 GB. With a local Python environment and compact extracted panel, expected session storage is below 2 GB (estimate); avoid raw guide/readcount downloads. Free disk checked: approximately 31 GiB. Large searches and repeated permutation counts must have explicit bounded runtime and report their actual budget.

This is analysis of existing public cell-line data, not recruitment, identifiable patient research, wet-lab work, or clinical decision-making. No restricted inputs are planned.

No maintainer has agreed to serve. Build as a local proposal with donor intake closed, no hub consent, no publishing, and no invented maintainer identity. Proposed license: MIT for new code, CC BY 4.0 for new prose; source data retain their own terms and attribution. Credit named contributors only with their agreement; preserve candidate provenance, agent contributions, negative results, and independent verification records.

## Confirmation required by the requested playbook

The user-requested https://discoveryathome.org/v0/start.md, step 3, says: "Get their confirmation before building." It also requires agreement before running project code without a sandbox. This session has unrestricted filesystem permissions and no execution sandbox. Confirm the above local scope and local execution before implementation. This does not authorize publishing, contacting anyone, hub enrollment, or wet-lab work.

After confirmation: build the verifier first, then the evaluation pipeline and worked example; establish baselines and run the bounded candidate search; write the protocol manifest/frontier/catalogue and reports; validate every first-step command and replay in a fresh checkout. Leave review ownership unresolved until somebody explicitly agrees.
