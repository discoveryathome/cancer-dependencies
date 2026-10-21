# Matched-expression robustness attempt

**Release differences are measurable, and a simple offset improves matched-model
expression agreement. It does not rescue the organoid prediction result.** This
completed local sensitivity attempt is author-checked, exploratory work on the
already exposed Broad cohort. Sanger remains reserved; intake and scientific
acceptance remain pending.

## What was done

The manuscript companion `traditional_expression.csv` downloaded successfully via
the ordinary DepMap publisher UI on this attempt. No browser block appeared and
none was bypassed. The ignored local file is 500,469,516 bytes, SHA256
`a63be3d995298f8a718efe8652315060da0a135a227b16bd5552a8ec73e2f5e1`.
This is a locally calculated hash; no publisher checksum was exposed.

The protocol was recorded after download and before parsing its expression values.
All 30 original predictors and all 12 targets were retained. **770 of 773** old
development ModelIDs have complete matched expression in this file. The three
absent IDs are ACH-001422, ACH-001648 and ACH-001649. No historical final models
were used. Matching used ModelID and the frozen Entrez gene identifiers.

One proposed correction subtracts each gene's median paired (new minus old)
expression difference. Five identity folds, fixed by sorting SHA256(group) and
assigning round-robin, assess this correction on expression values not used to
estimate that fold's offsets. Neither organoid expression nor any dependency
outcome is used to estimate offsets or select the method. The comparison is
against leaving the new traditional-model measurements unchanged.

The mean across genes of held-out MAE divided by the original 773-model development
IQR fell **0.204657 → 0.107428**, a **47.51%** reduction. **27/30** genes improved;
EGFR, NKX2-1 and SOX10 had zero median offsets and unchanged errors. All 30 paired
Spearman correlations were above 0.95. This passes the prespecified heuristic
(10% reduction and at least 20 improved genes), not a significance test.

An initial implementation mistakenly used the matched-model IQR and imposed an
extra complete-overlap gate. It was corrected to the protocol's full-development
IQR before prediction locking or outcome access. The initial source/results and
`implementation-correction.json` remain in the package. No correction method or
threshold was changed in response to prediction scores.

## What the provenance establishes

All 770 matched models are annotated traditional 2D. All have an old default RNA
profile from Broad. However, **same ModelID is not same RNA sample**. The manuscript
model metadata does not expose RNA ProfileIDs or ModelConditions, so sample
continuity cannot be verified with the supplied files.

There is a further limitation: old default RNA profiles include 493 marked
unstranded and 277 marked stranded, whereas the historical expression matrix is
documented as unstranded. These default-profile records must not be presented as
an established sample map for that particular unstranded matrix. A reviewer needs
the actual matrix-to-RNA-profile mapping on both sides.

The decision to continue therefore authorized only a **conditional release-bridge
sensitivity**, assuming that matched traditional-model offsets also apply to
organoids. It did not certify a technical batch correction or identify the cause
of the differences. Sample changes, processing changes and other causes are not
separated by this analysis. The empirical validation is within traditional models;
transportability of their offsets to organoids is unverified.

## All-77-organoid sensitivity result

The offsets estimated from all 770 matched development models were frozen before
response parsing in this round and applied identically to every model family.
All 77 organoids and all 12 targets were scored. No retraining, threshold tuning,
clipping, scaling search, target removal or alternative correction was attempted.
Some corrected coordinates become negative; they are model coordinates, not
claims of physical negative log2(TPM+1). Their counts are retained in the lock.

**Compact minus strong mean Spearman remains −0.046125**, with the same conditional
95% identity-bootstrap interval **[−0.106894, +0.018432]** (all 2,000 draws valid).
Compact mean Spearman remains 0.083727 versus strong 0.129853.

This invariance was identified and recorded *before scoring*: with complete inputs,
a constant offset per gene changes only the intercept of a frozen linear model.
It cannot change its ranking. All 36 linear-family rankings (12 targets × compact,
strong and self-expression) were verified unchanged. The unchanged rank endpoint
is algebraic, not new evidence that every possible harmonization would fail.

Absolute-error diagnostics improve modestly: macro raw MSE is 0.219806 → 0.209590
for compact and 0.198326 → 0.191740 for strong. The compact model remains worse on
that summary too. These MSEs are uncalibrated cross-assay diagnostics, not the
primary endpoint or a claim of biological improvement. Per-target, all-family
and lineage results are preserved in `results.json`.

Only **3/12 rules** have at least 15 organoids on both sides, both before and after
correction. SMARCA2 gains support (66/11 → 51/26), while MDM2 loses it (60/17 →
65/12). ERBB2 and SMARCA4 retain support. ARID1B, EGFR and STAG1 remain constant
branches. The supported SMARCA2 rule still has only descriptive Spearman 0.0395.

| Dependency target | Original branches | Offset-adjusted branches | Adjusted support |
| --- | ---: | ---: | --- |
| BRAF | 70 / 7 | 70 / 7 | insufficient |
| KRAS | 8 / 69 | 12 / 65 | insufficient |
| NRAS | 2 / 75 | 2 / 75 | insufficient |
| EGFR | 0 / 77 | 0 / 77 | insufficient |
| ERBB2 | 37 / 40 | 37 / 40 | adequate |
| PIK3CA | 74 / 3 | 74 / 3 | insufficient |
| SMARCA2 | 66 / 11 | 51 / 26 | adequate |
| SMARCA4 | 31 / 46 | 48 / 29 | adequate |
| ARID1B | 77 / 0 | 77 / 0 | insufficient |
| STAG1 | 77 / 0 | 77 / 0 | insufficient |
| MDM2 | 60 / 17 | 65 / 12 | insufficient |
| PRMT5 | 12 / 65 | 12 / 65 | insufficient |

## Matched-model expression audit, all 30 genes

Offsets are new minus old on 770 paired development models; application subtracts
them. MAE columns below are unscaled expression errors from the held-out folds.
The aggregate gate above uses the original development IQR as each denominator.
No target or gene is selected for a favorable result.

| Gene | Median offset | Paired Spearman | OOF MAE before | OOF MAE after |
| --- | ---: | ---: | ---: | ---: |
| ARID1A | +0.1454 | 0.9734 | 0.2051 | 0.1712 |
| ARID1B | +0.0143 | 0.9583 | 0.1460 | 0.1455 |
| BRAF | +0.1615 | 0.9627 | 0.1875 | 0.1128 |
| CCND1 | +0.2472 | 0.9980 | 0.2469 | 0.0871 |
| CDK4 | +0.2751 | 0.9824 | 0.2839 | 0.0920 |
| CDK6 | +0.3712 | 0.9906 | 0.3864 | 0.1250 |
| CDKN2A | +0.0977 | 0.9939 | 0.2505 | 0.2304 |
| EGFR | +0.0000 | 0.9968 | 0.0815 | 0.0815 |
| EPCAM | +0.2408 | 0.9982 | 0.2465 | 0.1434 |
| ERBB2 | -0.0239 | 0.9955 | 0.0903 | 0.0881 |
| ESR1 | +0.0161 | 0.9944 | 0.0452 | 0.0403 |
| GATA3 | +0.0204 | 0.9958 | 0.1198 | 0.1169 |
| KRAS | +0.4924 | 0.9717 | 0.4962 | 0.1213 |
| MDM2 | +0.3071 | 0.9655 | 0.3337 | 0.2085 |
| MITF | +0.1229 | 0.9957 | 0.1554 | 0.1014 |
| MTAP | +0.3205 | 0.9795 | 0.3530 | 0.2045 |
| MYC | -0.1609 | 0.9623 | 0.2841 | 0.2586 |
| NKX2-1 | +0.0000 | 0.9904 | 0.0784 | 0.0784 |
| NRAS | +0.3767 | 0.9767 | 0.3938 | 0.1121 |
| PIK3CA | +0.1779 | 0.9614 | 0.2097 | 0.1163 |
| PRMT5 | +0.1099 | 0.9895 | 0.1203 | 0.0727 |
| PTEN | +0.3743 | 0.9709 | 0.3699 | 0.1255 |
| RB1 | +0.3563 | 0.9797 | 0.3685 | 0.1219 |
| SMARCA2 | +0.4010 | 0.9819 | 0.4066 | 0.1856 |
| SMARCA4 | -0.5462 | 0.9544 | 0.4963 | 0.1708 |
| SOX10 | +0.0000 | 0.9859 | 0.0334 | 0.0334 |
| STAG1 | +0.1140 | 0.9794 | 0.1427 | 0.1038 |
| STAG2 | +0.2928 | 0.9796 | 0.2886 | 0.1033 |
| TP53 | +0.0822 | 0.9887 | 0.1438 | 0.1224 |
| VIM | -0.1204 | 0.9972 | 0.1910 | 0.1712 |

## Assessment and next step

This strengthens the project as a bounded robustness/benchmarking workstream:
contributors can identify release compatibility problems and test falsifiable
explanations without claiming a new cancer target. It does **not** improve the
case for advertising robust organoid prediction or opening public donor intake.
Release shifts can matter for individual rule thresholds; this one empirically
supported offset does not restore broad rule support or predictive superiority.

The next high-value outside input is an assay-aware reviewer who can obtain or
verify the exact RNA-profile mapping, sample continuity, processing/annotation
versions and whether traditional-model shifts should transfer to organoids. A
scientific owner also needs to decide whether another correction or a revised
benchmark addresses a useful biological question. Neither role is appointed.

Do not spend the reserved Sanger evaluation on repeated normalization guesses.
Any later adaptive model/correction development needs its own outcome-free
selection design and eventual prospective confirmation. This analysis does not
show that nonlinear/scale changes cannot help, and does not prove biological
causes for the remaining differences. No outreach, push or public update occurred.

## Reproduction and checks

```sh
python3 research/robustness-20261021/check_manifest.py --raw
.venv/bin/python src/expression_bridge.py verify --inputs data/raw/robustness-20261021
.venv/bin/python src/bridge_sensitivity.py verify --inputs data/raw/transfer-trial-20261021
.venv/bin/python research/robustness-20261021/audit_metrics.py
.venv/bin/python -m pytest -q
```

Raw publisher inputs remain in ignored `data/raw/`. The source manifest records
acquisition and bytes; no new raw data is committed. `run`/`predict`/`score` use
exclusive creation, while `verify` performs replay. Four new controls cover offset
recovery, held-out-fold isolation, missingness/identity failures, correct full
reference IQR and real prediction-stage guards against response/Sanger access.
All **42 tests pass**. Full prediction/result replay passes. A separate SciPy
calculation checks all **144** corrected/uncorrected target-family rho/MSE pairs,
24 branch counts, full outcome coverage and invariant rankings. These are
arithmetic checks by the same author, not independent scientific review.

Sources and attribution: Broad Institute DepMap,
[DepMap Public 24Q2 v1](https://doi.org/10.25452/figshare.plus.25880521.v1),
[NextGen Model Manuscript 2026](https://depmap.org/portal/data_page/?releasename=NextGen+Model+Manuscript+2026&tab=allData),
and Neiswender, Maffa, Brenan et al.,
[Nature (2026)](https://doi.org/10.1038/s41586-026-10843-7).
Release descriptions and the locally pinned publisher READMEs document the
expression units. Data retain publisher terms; internal-research authorization is
not a blanket raw-data redistribution license.
