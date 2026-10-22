# Pre-release incubated project handoff — 2026-10-21

> **Historical (2026-10-21).** The status below predates the launch: the checkpoint is
> merged to main, and the project has been open to donated sessions since 2026-10-21 with
> @Mister-Meeseeks as maintainer. The scientific position and resume sequence still stand.
> Current status is in `CURRENT.md`; run `research/launch-20261021/check_manifest.py` in
> place of `research/program-v2-20261021/check_manifest.py` on the current checkout.

**Status: parked, ready for supervised scientific/technical handoff.** Research
preparation is complete for this round. Public donor intake and scientific
acceptance remain pending. No scientific owner or independent reviewer is appointed.
This document is a current operational summary, not a new scientific acceptance.

The research checkpoint is `3aa53b0` on `trial-cancer-support-20261021` in
`discoveryathome/cancer-dependencies`. The latest work is local and has not been
pushed or sent to a reviewer. A recipient needs this branch/checkpoint and access
to the publisher inputs before a full replay; a clone of the existing remote main
alone does not contain this work.

## What is ready

The [research contract](../DISCOVERY.md), [quickstart](../QUICKSTART.md) and
[seven task cards](../discover/catalog.json) support both comparable improvements
and broader exploration. Compact models are optional; the original target panel
does not permanently limit the project. The latest trial has frozen protocols,
models, predictions, complete target accounting, source hashes, runtime records,
verification commands and a [review request](../research/wide-expression-20261021/HANDOFF.md).

At the research checkpoint, all 50 tests, the full model refit, prediction/result
replay and a separate arithmetic audit passed. These are author-performed checks,
not independent scientific review or a successful newcomer onboarding trial.
During handoff cleanup, all six historical evidence packages, the program package,
the latest trial package (including its three raw-input hashes), and the task
declarations were checked again and passed. No model or scientific artifact changed.

## Scientific position and next lead

The [broader-expression trial](../research/wide-expression-20261021/README.md)
improved development mean Spearman from 0.2948 to 0.3471. Broad organoid mean
Spearman was 0.1100 versus 0.1273 for the matched reference: no aggregate external
gain is established, and no superiority over published methods has been tested.

MDM2 is the priority follow-up lead: Broad correlation increased from 0.1790 for
the earlier strong reference (0.2160 for the matched reference) to 0.4083. BRAF
and PRMT5 are secondary leads. All three were identified after inspection and
remain exploratory. Preserve all 12 targets and failures; do not turn the favorable
subset into a retrospective success criterion. The original results, not the
priority ranking in this handoff, are the scientific record.

The [expression compatibility audit](../research/robustness-20261021/README.md)
also found a measurable cross-release discrepancy reduction, but did not establish
an improvement in model rankings or prove portability of the correction to
organoids. Practical experimental utility, novelty and treatment relevance remain
unestablished.

## Resume sequence and outside help

1. Appoint a cancer functional-genomics scientific owner and an independent
   statistical/methodological reviewer. They should assess assay and sample
   comparability, identity overlap, leakage, reference strength and interpretation.
2. Independently replay the existing package before changing it. Reproduce a
   relevant published reference under a clearly documented comparable protocol;
   our local references do not establish the state of the art.
3. Write a new prospective follow-up protocol prioritizing MDM2, with explicit
   treatment of BRAF/PRMT5 and multiple comparisons, eligibility/coverage criteria,
   comparators, metrics, budget and acceptance conditions. Keep broader exploration
   available as separately logged tasks.
4. Qualify a suitable independent evaluation before opening outcomes. Broad and
   the historical final test are exposed. Sanger outcomes remain reserved within
   this project, but independence and assay compatibility must be checked; public
   availability is not access-controlled blinding. If unsuitable, identify another
   evaluation rather than claiming repeated Broad scoring as confirmation.
5. Have a new contributor complete a bounded task and obtain reviewer acceptance
   before considering an invitation beta. Public intake needs a separate readiness
   decision with an accountable owner and review capacity.

## Reproduction and data handoff

Use Python 3.12 and [the locked environment](../requirements.lock). Raw publisher
matrices are ignored and are not included in Git. The recipient must obtain them
under the source terms and match the recorded hashes. Start with the
[original input lock](../data/source-lock.json),
[transfer source manifest](../research/transfer-results-20261021/source-manifest.json)
and [latest artifact/raw manifest](../research/wide-expression-20261021/manifest.json).
The robustness package records its additional traditional-expression input.
Local availability is verified; fresh-machine acquisition/onboarding is not.

From the repository root, inspect the scripts and run:

```sh
python3 src/check_history.py
python3 research/program-v2-20261021/check_manifest.py
python3 research/wide-expression-20261021/check_manifest.py --raw
.venv/bin/python src/research_program.py check
.venv/bin/python src/wide_expression.py check
.venv/bin/python src/wide_expression.py verify-fit
.venv/bin/python src/wide_expression.py verify
.venv/bin/python research/wide-expression-20261021/audit_metrics.py
.venv/bin/python -m pytest -q
```

The recorded full refit took about five minutes on the preparation machine; setup
and data acquisition are additional. Verification replays existing evidence;
new work belongs in a new contribution package.

Earlier handoffs and package READMEs are dated evidence. In particular, the initial
transfer preparation's access-blocked status was resolved in the transfer-results
package, and its copy-number scale description was subsequently corrected: the
new raw copy-number input is linear; it was not used in the expression-only trial.
Use CURRENT.md and this handoff for current operational status. Historical
documents and evidence manifests are preserved, including earlier limitations
and superseded recommendations.
