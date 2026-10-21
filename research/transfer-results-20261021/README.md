# Broad organoid transfer: completed exploratory trial

**The new data are imported locally and the frozen trial is complete. The compact
candidate did not demonstrate an aggregate advantage over the stronger baseline.**

Prepared from scaffold commit `d111d08db07fe8f9b97006a7345759a6047f6fd1` on
2026-10-21. The same agent performed and checked the trial; this is not independent
contributor or scientific acceptance. Intake remains closed and Sanger outcomes
remain reserved. No candidate was retuned on the new outcomes.

## Main result

All **77** prespecified Broad 3DO organoids had complete expression data for all
30 panel genes and responses for all **12** targets. There were no expression-row
exclusions or missing target outcomes. The pool still represents provisional
recorded identity components; incomplete donor/alias information is unresolved.

| Prespecified comparison | Result |
| --- | ---: |
| Mean target-wise Spearman, compact pair | 0.08373 |
| Mean target-wise Spearman, selected strong expression baseline | 0.12985 |
| Primary paired difference, compact minus strong | **−0.04613** |
| Conditional paired-identity bootstrap 95% interval | **[−0.10689, +0.01843]** |
| Bootstrap draws supporting all 12 contrasts | 2,000 / 2,000 |

The point estimate favors the stronger baseline, but the interval spans zero.
There is no demonstrated compact-model advantage, nor a conclusive inferiority
claim. The interval conditions on fitted models and provisional recorded identities;
it does not include training, dataset-selection or unknown-relatedness uncertainty.
Mean lineage and self-expression correlations were 0.03650 and 0.08028,
respectively, as descriptive comparisons with no added significance claims.

## All targets and support

Rho denotes Spearman correlation. All model families and MSE diagnostics are in
`../transfer-trial-20261021/run/results.json`. Five of twelve compact candidates
had a higher point estimate than the selected strong baseline; this does not
establish five discoveries. No target was selected or removed after evaluation.

| Target | n | Compact pair rho | Strong baseline rho | Difference | Rule branch counts |
| --- | ---: | ---: | ---: | ---: | --- |
| BRAF | 77 | -0.1742 | -0.0283 | -0.1459 | 70 / 7 |
| KRAS | 77 | 0.3455 | 0.5910 | -0.2454 | 8 / 69 |
| NRAS | 77 | 0.0569 | -0.0539 | +0.1109 | 2 / 75 |
| EGFR | 77 | 0.3492 | 0.4353 | -0.0861 | 0 / 77 |
| ERBB2 | 77 | -0.0072 | 0.0439 | -0.0512 | 37 / 40 |
| PIK3CA | 77 | -0.0998 | 0.2989 | -0.3987 | 74 / 3 |
| SMARCA2 | 77 | 0.0423 | 0.0213 | +0.0211 | 66 / 11 |
| SMARCA4 | 77 | 0.1806 | 0.1966 | -0.0160 | 31 / 46 |
| ARID1B | 77 | 0.1314 | 0.0842 | +0.0472 | 77 / 0 |
| STAG1 | 77 | -0.1649 | -0.2852 | +0.1204 | 77 / 0 |
| MDM2 | 77 | 0.1151 | 0.1790 | -0.0639 | 60 / 17 |
| PRMT5 | 77 | 0.2297 | 0.0755 | +0.1542 | 12 / 65 |

Only **3/12** expression rules had at least 15 response-bearing models in both
branches: ERBB2, MDM2 and SMARCA4. ARID1B, EGFR and STAG1 put all 77 models in one
branch, giving constant predictions and undefined rank correlations. Several
other rules had a small minority branch. The primary compact-versus-strong
comparison remained defined for all targets; inadequate rule support is separately
reported and must not be treated as a rule validation success.

The cohort contains Pancreas 19, Esophagus/Stomach 18, Bowel 16, Breast 9,
Prostate 7, and four lineages with two models each (Ampulla of Vater, Biliary
Tract, Ovary/Fallopian Tube, Uterus). Small lineage tables are descriptive only.
Transfer performance can reflect population and measurement differences; this
trial does not identify the cause of weak transfer or establish causal biology.

## What this changes for the project

We now have a working, fully covered external stress test and a concrete negative
aggregate result. The strongest near-term work is replication and robustness:
verify the measurements and identities, explain rule-support failures, and test
whether improvements survive stricter comparisons. The evidence does not support
presenting compact predictor search as a reliable route to new cancer targets.

The project can offer bounded, checkable research artifacts, including failures.
It still needs a scientific owner and an independent reviewer before supervised
intake. Cancer-model knockout responses do not establish drug response, normal-cell
sparing or clinical utility. This expression-only, restricted-panel experiment is
not a genome-wide benchmark or a direct replication of the recent transfer paper.

## Data and terms

Downloaded the exact `next_gen_expression.csv` (92,238,316 bytes),
`screen_gene_effect.csv` (557,107,782 bytes), and release `README.txt`
(26,165 bytes) from the [NextGen Model Manuscript 2026 release](https://depmap.org/portal/data_page/?tab=allData&releasename=NextGen+Model+Manuscript+2026).
SHA-256 hashes, input definitions and provenance are in [source-manifest.json](source-manifest.json).
The inspected UI did not expose publisher checksums; these are locally calculated
hashes, not an independent publisher-checksum verification. The input headers and
coverage match the intended stable-gene and model/screen identities.

The user explicitly authorized accepting the [DepMap terms](https://depmap.org/portal/terms/),
revised April 2, 2026. The reviewed terms permit internal research with AI/ML,
restrict commercial/clinical use, require attribution and privacy protections,
and impose requirements on rehosting. This local trial follows that limited
scope. Raw matrices and the publisher README remain in ignored
`data/raw/transfer-trial-20261021/`; no raw downloads were published. The prediction
artifact embeds the 77-model expression panel; review the data terms before any
external redistribution of it. No general CC BY permission is inferred for these
portal downloads from a different Figshare metadata release.

Attribution: Neiswender, Maffa, Brenan et al., *A dependency map enhanced with
next-generation 3D cancer models*, Nature (2026),
[doi:10.1038/s41586-026-10843-7](https://doi.org/10.1038/s41586-026-10843-7),
Broad Institute DepMap. Analysis and author checks performed with agent assistance.

**Correction to the preparation rationale:** the publisher README distinguishes
raw `next_gen_copy_number.csv` on a linear scale from derived analysis tables on
log2(relative-to-ploidy + 1). The earlier preparation text overgeneralized the
derived-table scale to the entire new copy-number resource. Direct compatibility
with old absolute PureCN values still needs checking. We kept the already frozen
expression-only protocol and did not download copy-number data or revise candidates
based on this clarification.

## Reproduce and next work

The one-time evaluation has already occurred; use `verify`, not `score` or a new
freeze. The outcome exposure record is retained. The earlier preparation manifests
remain immutable historical snapshots; this report supersedes their pending-data
status, not their model/protocol bindings.

```sh
python3 research/readiness-20261021/check_manifest.py
python3 research/qualification-20261021/check_manifest.py
python3 research/transfer-trial-20261021/check_manifest.py
python3 research/transfer-results-20261021/check_manifest.py --inputs data/raw/transfer-trial-20261021
.venv/bin/python src/transfer_trial.py verify --out research/transfer-trial-20261021/run --inputs data/raw/transfer-trial-20261021 --source-manifest research/transfer-results-20261021/source-manifest.json
.venv/bin/python research/transfer-results-20261021/audit_metrics.py --inputs data/raw/transfer-trial-20261021
```

The full frozen scorer replay passed, including all bootstrap results. A separate
SciPy implementation checked all 72 model/target correlations and MSEs, all
12 × 77 response coverage counts, and the primary contrast to 1e-12 tolerance.
All 12 development fits had already reproduced exactly before external scoring.
These checks establish computational consistency, not independent scientific review.

Useful next tasks are an identity crosswalk audit, a measurement/threshold-support
audit, and an independent replay of this exact failure. Any new Broad-driven model
work is exploratory now. Reserve Sanger for a separately reviewed, prospectively
frozen protocol, with adequate lineage and identity support established beforehand.
