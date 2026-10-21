# Cancer-cell dependencies: preparation for scoped trials

Local preparation authorized on 2026-10-21. Results are author-checked; scientific
review and public intake remain pending. No external messages or publication occurred.

## Start

From the repository root in its documented environment:

```sh
.venv/bin/python src/readiness.py verify --candidate research/readiness-20261021/candidates/SMARCA2.json
```

## Prepared work

The new contributor surface exports only the **773 historical development identities**.
It contains none of the 194 historical final identities or separate Sanger outcomes.
`src/prepare_development.py` verifies the source lock and preserves the original
CSV cell strings exactly. An initial floating-point re-export was replaced before
freezing this package to avoid unnecessary numerical perturbations.
The old final/transfer files remain in the repository for reproduction; this is an
explicit workflow boundary, not a hostile-user access-control system.

There are 12 positive-control task packages, each with five fixed outer folds.
Every fold has mean, lineage, one-rule and strong linear comparators. Ridge/elastic
hyperparameters and the strong baseline family are selected inside that fold's
training data; self-expression is included. No outer-test choice selects the comparator.
The starter is the existing data-selected two-feature ridge model, not a new method.
All per-target wins and losses appear in `portfolio.json`; these are exposed-data
comparisons and no fresh predictive discovery is claimed.

The editable hook is `src/compact_candidate.py`. It receives one training fold.
A concrete propose → verify → refit workflow is available:

```sh
.venv/bin/python src/readiness.py propose --target SMARCA2 --output research/my-task/candidate.json
.venv/bin/python src/readiness.py verify --candidate research/my-task/candidate.json --refit
```

The checker enforces exact five-fold coverage, identity separation, <=3 molecular
features, finite well-shaped models and all reported metrics. It rejects missing
folds, substituted identities, outcome features, zero scales and fabricated scores.
`--refit` binds the candidate hook and re-fits each training fold. A consistent but
non-refittable forged model is a tested negative control. Source review is still
necessary to assess whether selection was honest. The original scientific checker,
cohort and historical frontier are unchanged.

The proposed future-data audit found **135 metadata-only new identity components**
in DepMap 24Q4 after excluding every component linked to the entire old release.
Only **17** have passing releasable 2D screens, **12** of those with Avana. Feature
and target availability and branch support are not yet established. This is below
the existing 30-model external-support requirement, before stricter exclusions.
The reserve is therefore **insufficient for confirmation**. No new response or
molecular-feature matrices were downloaded or evaluated. See [EVALUATION.md](EVALUATION.md).

The 24Q4 v1 publisher metadata explicitly states CC BY 4.0. Only four metadata files
were fetched, with publisher MD5 and local SHA-256 checks. This release-specific
record does not authorize arbitrary newer releases. Attribution: DepMap, Broad
(2024), https://doi.org/10.25452/figshare.plus.27993248.v1. Metadata are unchanged;
`cohort-reserve.json` is our derived identity/availability audit.

`pytest.ini` now confines collection to the project's tests and supplies `src` on
the import path. This fixes the documented pytest command attempting to collect
tests from the local dependency cache. No global environment was changed.

## Review and trials

Read [REVIEW.md](REVIEW.md), [EVALUATION.md](EVALUATION.md), and [TRIAL.md](TRIAL.md).
The unfilled `review.json` is intentional. A reviewer must identify the exact commit
and artifact hashes. Independent human review is not inferred from multiple checkers.

Remaining gates:

- Appoint a responsible maintainer and scientific reviewer with capacity.
- Approve a sufficiently large new cohort with identity and processing audits.
- Independent source/refit and newcomer review.
- Review claims, source-specific terms and benchmark acceptance before public intake.
