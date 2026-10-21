# Broader-expression contributor trial

**A new broader-feature reference improves development performance but does not
improve aggregate organoid transfer.** This is a completed new model contribution
under program v2, not a replay presented as a new trial. Same primary author, prior
repo/result context; no independent newcomer or scientific review is claimed.

## Question and method

Does removing the original 30-gene feature restriction improve dependency prediction?
The user authorized an expanded program and another trial. This was a deliberate
priority task, with rationale recorded rather than a fabricated random task draw.

The candidate uses ridge regression on 300 genes selected by absolute training
Pearson association with each target. It searches **18,953 unambiguous shared
EntrezIDs** from the old and manuscript expression headers. Feature screening,
90% observed-value eligibility, median imputation, scaling and ridge-penalty
selection are repeated within every inner-training fold. No external expression
values or outcomes enter fitting or feature selection. Header availability is
used to define a measurable cross-release feature universe; it is not a claim of
identical assay/sample provenance.

The matched reference uses the original 30 expression genes with the same ridge
penalty grid [1,10,100,1000], preprocessing, folds and selection objective. The
comparison therefore isolates expanding the feature search within this method.
It is not a reproduction of a published Elastic Net method and does not establish
state-of-the-art performance. The previous frozen strong expression and compact
models are retained as additional external references.

All 773 development identities and all 12 targets were eligible. We used five
identity-grouped outer folds (seed 1701), three inner folds (seed 817), pooled inner
MSE selection and larger-alpha tie breaking. Each development row has exactly one
outer-test prediction per target. The primary metric is the all 12-target mean
Spearman difference, wider minus panel30. Random grouped folds do not establish
transfer to an unseen lineage or laboratory.

Input checks found 17 duplicated EntrezIDs in the old full matrix. The amendment
excludes ambiguous IDs from either release before fitting; no alias was selected
using values or outcomes. No original panel gene was excluded. One test fixture
also had an incorrect feature-count expectation; that was corrected before fitting.
Both preflight failures are recorded. No candidate was dropped after scoring.

## Results

| Evaluation | Broader300-gene ridge | Matched30-gene ridge | Wider minus panel30 |
| --- | ---: | ---: | ---: |
| Development OOF mean target-wise Spearman | 0.347068 | 0.294791 | +0.052276 |
| Broad 77 mean target-wise Spearman | 0.110030 | 0.127294 | −0.017263 |

Development lineage baseline mean Spearman is 0.212886. Wider expression improves
11/12 development target point estimates; STAG1 is slightly worse. These are
exploratory development estimates, not independent significance tests.

On the already exposed Broad organoids, wider minus panel30 has a conditional 95%
identity-bootstrap interval **[−0.089770,+0.048644]**. Against the earlier frozen
strong baseline (mean Spearman 0.129853), the difference is **−0.019822**, interval
**[−0.090422,+0.046161]**. All 2000 shared-identity draws are valid for both
comparisons. Point estimates favor the references, but these intervals do not
establish that the broader method is worse. Training/model-selection uncertainty
and unknown donor relationships are not captured by these conditional intervals.

All 77 organoids and all 12 targets were retained. There were **zero missing selected
expression entries** across the candidate/reference models; no imputation was
needed on their external selected features. No release correction, threshold
rebalancing, new target selection or alternative model search was added after
these results. The Sanger outcome files were not opened.

| Target | Development panel30 | Development wide300 | Broad panel30 | Broad wide300 | Broad old strong |
| --- | ---: | ---: | ---: | ---: | ---: |
| BRAF | 0.1711 | 0.2743 | -0.0193 | 0.2055 | -0.0283 |
| KRAS | 0.3536 | 0.3707 | 0.5910 | 0.5539 | 0.5910 |
| NRAS | 0.0603 | 0.1514 | -0.1009 | -0.1876 | -0.0539 |
| EGFR | 0.4770 | 0.5496 | 0.4419 | 0.2068 | 0.4353 |
| ERBB2 | 0.3892 | 0.3900 | 0.0450 | -0.1559 | 0.0439 |
| PIK3CA | 0.3385 | 0.4751 | 0.3125 | 0.2839 | 0.2989 |
| SMARCA2 | 0.1497 | 0.1994 | 0.0428 | -0.0008 | 0.0213 |
| SMARCA4 | 0.4223 | 0.4278 | 0.1700 | 0.0157 | 0.1966 |
| ARID1B | 0.1723 | 0.1762 | 0.0613 | -0.0911 | 0.0842 |
| STAG1 | 0.1935 | 0.1927 | -0.3280 | -0.2039 | -0.2852 |
| MDM2 | 0.5282 | 0.6389 | 0.2160 | 0.4083 | 0.1790 |
| PRMT5 | 0.2818 | 0.3187 | 0.0953 | 0.2856 | 0.0755 |

Full results include raw MSE diagnostics and descriptive lineage tables. Tiny
lineage cells are not separate discoveries. The predictions were locked before
this round's response access, but Broad was already exposed in previous work;
this is not a fresh blinded test.

## What the new contribution changes

The original panel restricted development performance, but expanding the expression
search alone did not repair organoid transfer. This supports studying context and
measurement compatibility rather than assuming more predictors automatically solve
the problem. It does not prove that broader models generally fail, nor identify
whether biology, measurement shift, overfitting or another cause drives attenuation.

Do not discard the full family solely because its aggregate result is negative.
BRAF, MDM2 and PRMT5 have higher positive organoid point correlations than both
references; STAG1 improves but stays negative. These are **post hoc exploratory
leads**, not accepted target-specific wins. All 12 rows are retained in leads.json.
No favorable subset or target-wise hybrid was substituted for the declared primary
comparison. A follow-up needs its own selection/confirmation plan.

The delivered reference removes a concrete limitation of the old workflow: it can
screen beyond30 genes, retain300-feature models, audit fold-local selection and
score all inherited external targets. Compact models remain a separate option.
There is still no demonstrated practical experimental-selection benefit, validated
biomarker, scientific owner or basis for opening public intake.

## Verification and reproduction

The existing Python 3.12 locked environment and local pinned publisher matrices are
required for fitting/replay. No downloads or installations were added this round.

```sh
.venv/bin/python src/research_program.py check
python3 src/check_history.py
.venv/bin/python src/wide_expression.py check
.venv/bin/python src/wide_expression.py verify-fit
.venv/bin/python src/wide_expression.py verify
.venv/bin/python research/wide-expression-20261021/audit_metrics.py
.venv/bin/python -m pytest -q
```

The train/predict/score phases refuse to overwrite saved evidence; use verify-fit
and verify to reproduce this completed reference. A new model or altered protocol
belongs in a new contribution package with its own source and bindings, not an
edit of the scored reference. The task protocol limits fitting to 15 minutes and
records all model/penalty selections. Timing files report actual execution.

All 50 tests pass, including six new controls for signal outside the original
panel, training-only preprocessing, ambiguous/duplicate identities, inner-fold
selection isolation, real-input outcome access guards and program declarations.
Separate SciPy arithmetic checks cover 96 target-family rho/MSE pairs, complete
outer coverage, inner/outer identity separation and all 77×12 external outcomes.
The full model refit passes (refit.log), as does prediction/result replay
(verify.log). The two added history-migration controls also pass. These checks are by the same author and do not establish independent
scientific acceptance.

Historical entry documents were archived before changing the current mission and
catalogue. Original numerical artifacts and manifests remain unchanged. The new
history checker resolves only explicitly archived entry documents; it does not
substitute snapshots for changed scientific code/data. See the program migration.

Source data: [DepMap 24Q2](https://doi.org/10.25452/figshare.plus.25880521.v1), Broad
Institute DepMap; [NextGen Model Manuscript 2026](https://depmap.org/portal/data_page/?releasename=NextGen+Model+Manuscript+2026&tab=allData),
Neiswender, Maffa, Brenan et al., [Nature 2026](https://doi.org/10.1038/s41586-026-10843-7).
Raw matrices remain ignored and are not redistributed. Data retain publisher
terms. Models and provenance are local research artifacts; no push, publication,
message or hub update occurred.
