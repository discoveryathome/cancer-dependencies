# Research and contribution contract — program v2

Pre-release contribution policy: **start a bounded task when your person has
requested a trial or donated session.** Scientific review is required to accept
results, not to begin research, reproduce a result or prepare a contribution.
`discover/program.json` and CURRENT.md define current intake. Closed-intake or
missing-owner statements in dated research packages, archived entry documents,
`discover/readiness.json`, `discover/qualification.json`, `discover/*-trial.json`
and `discover/transfer-result.json` describe earlier stages; they do not block
current participation. Preserve their scientific evidence and exposure records.

Can we improve predictions of cancer dependencies in new biological contexts enough
to guide experimental prioritization? This is the current mission. A practical
result would help researchers choose informative target–model combinations; good
benchmark correlation alone does not demonstrate that benefit.

## Search space and bottleneck

Methods may use compact or broader molecular predictors, biological context,
measurement harmonization or explicit abstention. Three measurements are an
optional compact-model objective, not a project-wide limit. The original 12-target,
30-predictor panel is an inherited benchmark, not a permanent boundary of the
science. Alternative targets, representations and data sources are welcome as
separately specified exploratory tasks with provenance, budget and evaluation.

The present bottleneck is reliable transfer and credible reference methods, not
more optimization of the original small panel. See CURRENT.md for the latest
work; discover/frontier.json remains the historical pilot evidence record, not a
claim that a new method is scientifically accepted. Current program status lives
in discover/program.json. No state-of-the-art or experimental utility is established.

## Two connected contribution tracks

**Comparable improvements:** work on a named task with frozen cohort, target set,
metrics, comparators and compute budget. Compare methods on the same data and
splits. Report accuracy, coverage, complexity and measurement requirements rather
than hiding tradeoffs in one universal score. Compact models remain welcome.

**Exploration and new tasks:** investigate broader models, biological contexts,
new targets, alternative representations, data compatibility or failure causes.
Register a bounded proposal before new outcome analysis. A useful deliverable is
a reproduced reference, candidate, falsified explanation, verified defect or
well-supported proposal for a new benchmark. A negative result is not a predictive
gain. Promising exploratory work becomes a comparison task only with an explicit
protocol and review; no forced mapping into the original compact-rule interface.

Use discover/catalog.json and QUICKSTART.md. Default track weights are balanced
for exploration and comparison; they are routing choices, not estimated scientific
value. A user-directed priority task need not be randomly selected; record why.

## Evaluation and promotion

Development-only outer validation is the optimization workspace. Feature screening,
imputation, normalization, hyperparameter selection and any abstention rule learn
inside training folds. Biological identity groups must not cross splits. Keep all
declared eligible targets and samples; report missingness and unsupported cases.
A coverage criterion must be set without evaluation outcomes. No favorable-subset
selection after scoring, and no claim that grouped random folds establish transfer
to unseen lineages, labs or culture conditions.

Broad organoid outcomes and historical final-test outcomes are already exposed.
Any further work using them is exploratory. Sanger organoid outcomes remain
reserved in this project; public availability does not make them an access-protected
holdout. Promotion to a confirmed result needs an appropriate untouched evaluation,
identity/assay review, a frozen analysis and independent reproduction. Do not claim
new confirmation from repeated use of a public evaluation set.

Changing targets, metrics or methods after inspection is allowed as new exploratory
work, but must be logged and cannot rewrite an earlier success criterion. Preserve
all attempted candidates and failures. A new task specifies its scientific question,
intended decision, data/cohort, baseline, metrics, search budget, exposure status,
prospective evaluation plan and acceptance/rejection conditions. Acceptance of
arithmetic, scientific interpretation and practical utility are distinct decisions.

## Scientific interpretation and review

Known biomarker rediscoveries are controls, not novelty. CRISPR knockout dependence
is not drug sensitivity. Cancer-only models cannot establish normal-cell sparing.
Same-model remeasurement is not an independent biological sample. Metadata lineage
adjustment cannot prove removal of all confounding; upstream assay preprocessing
is not automatically fold-local. No patient-level inference, restricted data,
wet-lab designs or claims of validated treatments are in scope.

Results are computational hypotheses about dependencies in cancer cell lines and
organoid models, not clinical or treatment advice. Sessions use only the pinned
public data and never fetch controlled-access, restricted or human-subject data.

Maintainer: @Mister-Meeseeks, from 2026-10-21. Review capacity: `surge`. The project
is open to pre-release agent trials and donated research sessions. Within their person's grant, sessions post claims, findings
and handoffs in the [Handoffs thread](https://github.com/discoveryathome/cancer-dependencies/discussions/3),
proposals in [Proposals](https://github.com/discoveryathome/cancer-dependencies/discussions/4)
and retrospectives in [Feedback](https://github.com/discoveryathome/cancer-dependencies/discussions/5),
and may open one focused PR. Changing the frontier, scientific acceptance, external
submission and merging stay with the maintainer; never contact data providers or other
authors on the project's behalf. Existing evidence is author-checked at most. An
independent reviewer, ideally a cancer functional-genomics scientist, should still
inspect leakage, assay/sample comparability and novelty before any result is accepted.

Save protocol, code, exact commands, input hashes, outputs, runtime, failures,
coverage and a v0 review handoff under research/<attempt>/. Distinguish preparation
from the contributor session and author-performed work from independent onboarding.
Code is MIT, new prose CC BY 4.0, and source data retain publisher terms. Preserve
attribution and agent provenance; name contributors only with their agreement.

## Historical protocols

config/PREREGISTRATION.md and config/benchmark.json remain the original pilot's
frozen protocol, not limits on new authorized v2 tasks. Existing compact-model
verifiers remain specific to their old task. Original entry documents are archived
byte-for-byte in research/program-v2-20261021/historical-entry/. Run
`python3 src/check_history.py` to verify old manifests against those snapshots and
unchanged current scientific artifacts. The old readiness manifest command expects
the old root documents and should be run at the pre-migration commit for its exact
original workflow. No historical scores or manifests were rewritten.
