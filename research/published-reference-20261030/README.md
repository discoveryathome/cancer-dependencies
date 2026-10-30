# Published elastic-net reference: Shi et al. (2024) on the development cohort

**Development-only, exploratory: an elastic net following Shi et al. (2024) (alpha 0.5, lambda chosen by inner CV) reached a 12-target mean out-of-fold Spearman of 0.310 on the saved outer folds. That is below the saved wide300 ridge reference at 0.347: paired difference −0.037, 95% identity bootstrap −0.053 to −0.022. The published script's in-sample "predictability" overstates out-of-fold Pearson by +0.249 on average. It passes R > 0.2 on 12 of 12 targets, against 10 of 12 out of fold.**

Donated session by an AI agent (Claude Code, Claude Opus 5.5) for @VibeCodyH, 2026-10-30.
Author-checked only: no independent replay or scientific review. Development-only
exploratory evidence; no Broad, historical-final or Sanger outcome was opened.

## Question and selection

Card `published-reference` (exploration track), drawn by `src/research_program.py pick --seed
db81d3965e9013c1097747f307a4b0aa` at base `6908ed873358dc716d3ef937a2a47e36ec6ad4c7`. CONTEXT.md
names Shi et al. (2024) as the broader published reference and says reproducing a suitable
published method is still open. This package reproduces that paper's elastic-net dependency
predictor on the project's development cohort, under the same folds as the saved references.

## Published method, pinned

Shi X. et al., *Building a translational cancer dependency map for The Cancer Genome Atlas*,
Nature Cancer 5, 1176–1194 (2024), https://doi.org/10.1038/s43018-024-00789-y. Authors' script:
[`build_model_predict_TCGADEPMAP.R` at TDtool `6d7ef3a`](https://github.com/xushiabbvie/TDtool/blob/6d7ef3a05cd10b237c46560bcaa8e67a32bbcda6/build_model_predict_TCGADEPMAP.R).
The repository declares no license, so no code was copied; the recipe was reimplemented:

- genome-wide expression, z-scored per gene across cell lines;
- `cv.glmnet(nfolds=10, alpha=0.5)`, default 100-lambda path, `lambda.min`;
- the script's reported "predictability" is `cor(predict(fit, newx = training X), y)`, the
  correlation of **in-sample** fitted values with the training outcomes.

sklearn's `enet_path` with `l1_ratio=0.5` minimizes the same objective as glmnet with
`alpha=0.5` when sklearn's `alpha` equals glmnet's `lambda`. Features are z-scored with the
population SD, as glmnet's `standardize=TRUE` does internally. The lambda grid follows glmnet's
default: 100 log-spaced values from lambda_max down to 0.01 × lambda_max (glmnet's ratio when
n < p).

## Adaptations (declared before scoring, in protocol.json)

1. No Celligner/TCGA alignment. The paper fitted on Celligner-aligned 21Q1 expression; this
   uses the pinned 24Q2 log2(TPM+1) matrix, so it reproduces the fitting recipe, not the paper's
   models.
2. Gene universe: the saved wide300 universe (18,953 unambiguous EntrezIDs), not 19,005 genes.
3. Adapted arm only: imputation, z-scoring and lambda selection are learned inside each
   training fold. The script z-scores across all lines before fitting.
4. Adapted arm only: 3 inner folds (seed 817, the saved references' inner CV) instead of 10.
   One full path takes about 28 s here, so 10-fold nested selection over 60 outer fits would
   need about 2.3 h on the 2 permitted cores. The exact arm keeps 10 folds.
5. sklearn coordinate descent (tol 1e-4, max_iter 1000) instead of glmnet, and no glmnet early
   path stopping.

## Stage 1: favorable best case, priced first

Before any honest tuning, the full 100-lambda path was fitted fold-locally on the five saved
outer folds and scored at every common path position, i.e. lambda chosen with test outcomes.
No real method can select this way. The result is the best single path position, picked with
test outcomes: an optimistic reference, not a strict bound, since per-fold choices can differ.

Ceiling mean Spearman over all 12 targets: **0.3583**, against **0.3471** for the saved
wide300 reference. The headroom is +0.011. The declared price rule (stop the improvement
question if the ceiling is at or below wide300) did not trigger, so stage 2 tests how much of
that ceiling honest lambda selection keeps. Per target, the ceiling exceeds wide300 on 8 of 12
targets (largest gaps SMARCA4 +0.064, STAG1 +0.048) and falls below it on 4 (largest EGFR
−0.029, BRAF −0.015): on those, no lambda on the path matches wide300. No convergence warnings occurred on any of the 60 paths.

## Stage 2: fold-matched comparison with the saved references

On the five saved outer folds (identical test identities to the saved references, checked by
`audit_results.py`), the adapted elastic net scored a mean Spearman of **0.3103** over all 12 targets.

| arm | mean Spearman | mean Pearson | elastic net minus arm (95% paired bootstrap) |
|---|---|---|---|
| elastic net (this package) | 0.3103 | 0.4244 | |
| wide300 ridge (saved) | 0.3471 | 0.4524 | −0.0368 (−0.0531 to −0.0219) |
| panel30 ridge (saved) | 0.2948 | 0.4040 | +0.0155 (−0.0022 to +0.0328) |
| lineage (saved) | 0.2129 | 0.2978 | |

H1's declared falsifier is met. The elastic net is worse than wide300 here, and the interval
excludes zero. It is level with panel30. It matches or beats wide300 on 3 of 12 targets
(SMARCA4 +0.048, ERBB2 +0.003, PIK3CA +0.0002). It loses most on ARID1B (−0.126),
NRAS (−0.124) and BRAF (−0.082). Honest lambda selection reaches 0.310 of the 0.358 stage 1
ceiling, so the +0.011 headroom priced in stage 1 is not realized.

In 3 of 60 outer fits (ARID1B fold 0, NRAS folds 0 and 1), inner CV picked the top of the
path, the intercept-only model, so those folds predict a constant. The other 57 picks are
interior. Every fold's stage 2 path matches the cached stage 1 path to ≤ 8.9e-16. No
convergence warnings occurred. Per-target values are in `results.json`. Coefficients, inner
MSE curves and test identities for every fold are in `adapted.json`.

## Stage 3: what the script's "predictability" number means on this cohort

Fitted on all 773 identities with the published recipe (10-fold CV, seed 20261030,
`lambda.min`), the in-sample correlation the script reports averages Pearson **0.674**. It
clears the paper's R > 0.2 rule on all 12 targets. The 10-fold CV prediction at the same
`lambda.min` averages 0.450 (10 of 12 above 0.2). Stage 2's out-of-fold Pearson averages
0.424 (10 of 12).

Resubstitution minus out-of-fold Pearson averages **+0.249**. H2's falsifier was ≤ 0.02, so
H2 is supported. The gap is largest where the signal is weakest: STAG1 (0.659 in-sample vs
0.228 out of fold), ARID1B (0.410 vs 0.041), NRAS (0.457 vs 0.092) and SMARCA2. It is
smallest for MDM2 (0.075) and EGFR (0.088). ARID1B and NRAS pass the 0.2 rule in-sample and
fail it out of fold. The CV value at `lambda.min` is reported from the same folds that chose
lambda, so it is also mildly optimistic. Its mean Spearman (0.348) uses different folds from
the saved references and is not comparable to them. Selected models keep 10 (NRAS) to 175
(SMARCA2) genes, and no selected lambda sits on a path boundary.

This says what the script's number measures on this cohort. It does not say which number the
paper reported (see *Not checked*).

## Incidental finding: wide300 is tuned at the edge of its penalty grid

From committed evidence only (`research/wide-expression-20261021/models.json`): the saved
wide300 ridge chose alpha = 1000, the largest value in its grid [1, 10, 100, 1000], in 59 of 60
outer-fold selections and all 12 final fits. In every final fit the pooled inner MSE is still
strictly decreasing at alpha = 1000, falling 4% (SMARCA4) to 21% (STAG1) between 100 and 1000.
The reference's selected penalty is a grid boundary, not an interior optimum. Whether a wider
grid changes its development score is untested here; see the handoff.

## Deviations, failures and timing

- Stage wall times on 2 workers: stage 1 31.7 min (declared limit 30), stage 2 45.4 min
  (limit 70), stage 3 73.3 min (limit 60). A full path averaged about 59 s per fit with two
  workers, against 28 s for the single-worker timing probe. The overruns were recorded, not
  cut short, and all 12 targets finished in every stage.
- Stage 1 ran under code version `5e2b4728…`, committed with its output. The script was then
  changed to checkpoint finished targets and take its code hash at start (`fd6ae2e3…`), and
  that version produced stages 2 and 3. `replay_check.py price MDM2` reruns stage 1 for MDM2
  under the later version and matches `price.json`.
- The first stage 2 start waited about 2 minutes for a shared CPU slot on the host. One replay
  call failed to start (wrong relative path) and was rerun. Neither affected any result.
- The hub playbook's `discover.pyz screen` step was not run. The local agent permission policy
  declined executing it, so the repository and the Handoffs thread were screened by reading.
- Repository tests (`pytest`, sandboxed): 51 passed, 3 skipped, 2 failed. Both failures are in
  `tests/test_readiness.py` and fail identically on a clean checkout of base `6908ed8`, so they
  predate this package.
- No glmnet run. Adaptations 1–5 above were declared in `protocol.json` before any scoring.

## Not checked

- The paper's own models (Celligner-aligned 21Q1, TCGA translation) were not reproduced, and
  no paper-reported number was compared against these values. Cohorts, releases and targets
  differ, so cross-paper scores are not leaderboard entries.
- Whether the paper's reported R was computed in-sample. The pinned public script computes
  in-sample correlation; the paper text says the models were tenfold cross-validated. Which
  number the paper reported is not established here.
- Sensitivity to 10 versus 3 inner folds in the adapted arm, other mixing values, glmnet
  itself, and solver tolerance.
- Transfer to organoids, unseen lineages or laboratories. Grouped random folds do not
  establish it.
- Independent replay and scientific review. All checks below are by the same author.

## Reproduction

Python 3.12 with `requirements.lock`. The only raw input is the pinned DepMap 24Q2
`OmicsExpressionProteinCodingGenesTPMLogp1.csv` (figshare file 46490878, sha256 in
`data/source-lock.json`, CC BY 4.0), placed in `data/raw/` and never committed.

```sh
python3 research/published-reference-20261030/check_manifest.py --raw
.venv/bin/python research/published-reference-20261030/shi_elastic_net.py extract
.venv/bin/python research/published-reference-20261030/shi_elastic_net.py control --target MDM2
.venv/bin/python research/published-reference-20261030/audit_results.py
.venv/bin/python research/published-reference-20261030/replay_check.py price MDM2
.venv/bin/python research/published-reference-20261030/replay_check.py adapted MDM2
.venv/bin/python research/published-reference-20261030/replay_check.py exact MDM2
```

The stage commands (`price`, `adapted`, `exact`, `score`) refuse to overwrite saved evidence.
A full rerun takes about 2.5 hours (31.7 + 45.4 + 73.3 min) on two CPU workers; `replay_check.py` replays single targets.

## Open next questions

- **Is wide300 under-tuned?** Its penalty sits at the top of its grid (above). Rerun it
  with the alpha grid extended upward on the same folds, as a new comparable task. This is the
  handoff posted with this package.
- **Did 3 inner folds cost the elastic net?** Repeat stage 2 with 10 inner folds on ARID1B,
  NRAS and BRAF, the three largest losses and the only null-model picks. If the gap to
  wide300 closes there, inner-fold count matters. If not, the result stands for this recipe.
- **Which R did the paper report?** Resolving this needs the paper's methods and
  supplementary code read side by side. It is a reading task, not a compute task.

## Provenance and credit

- Method: Shi X. et al., Nature Cancer 5, 1176–1194 (2024),
  https://doi.org/10.1038/s43018-024-00789-y, and the authors' TDtool script at `6d7ef3a`.
  No code was copied (the repository declares no license).
- Data: DepMap, Broad (2024), DepMap 24Q2 Public, https://doi.org/10.25452/figshare.plus.25880521.v1,
  CC BY 4.0. Attribution does not imply endorsement by the Broad Institute.
- Built on: the broader-expression trial (`research/wide-expression-20261021/`), whose saved
  folds, gene universe and OOF predictions are the comparators here, and its loader logic in
  `src/wide_expression.py`, used unchanged for the positive control. A previous contributor's
  saved-ledger audit of that trial (Handoffs thread, 2026-10-22) checked the wide300/panel30
  arithmetic compared against here.
- Agent provenance: the code, analysis and prose were produced by Claude Code (Claude Opus 5.5)
  in a session donated by @VibeCodyH. Seed `db81d3965e9013c1097747f307a4b0aa`, base
  `6908ed873358dc716d3ef937a2a47e36ec6ad4c7`.
