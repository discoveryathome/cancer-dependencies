# Cancer dependencies: qualification round

**Decision: continue toward a small, scientifically supervised replication and
robustness pilot. Broad traffic and predictive-discovery claims remain premature.**

Prepared on 2026-10-21 from commit `8cb3c6b959845e5fbfe0c2f3443700d39c938084`.
This is a local, author-checked package. No scientific owner has agreed to participate;
the user confirmed that no candidate is currently in mind. No outreach, push, hub
submission or intake change occurred.

## What changed

The earlier reserve audit concerned DepMap 24Q4 and found only 17 passing new 2D
screened identities. That remains correct for that release. The newer published
organoid resources offer substantially larger pools worth qualifying:

| Metadata pool | Screened models | Provisional reserve models | Recorded identity components in reserve |
| --- | ---: | ---: | ---: |
| Broad NextGen | 147 | 129 | 129 |
| Sanger organoids | 162 | 148 | 144 |

These are **upper bounds on potentially eligible independent units**, not approved
confirmation sample sizes. The reserve requires RNA availability and excludes
known historical overlap. Sanger additionally excludes components connected to any
Broad metadata model or flagged as Broad overlap. Broad's new-model donor/alias
coverage is incomplete. Per-target feature completeness, subgroup support,
engineered status, assay compatibility and statistical power are unresolved.

The 129 Broad reserve models include 77 dome-screened organoids, 14 coat-screened
organoids, and 38 CNS models across two formats. Pooling these populations would
need scientific justification. The Sanger pool is predominantly colorectal and
oesophageal: 81 and 49 models, respectively. Gastric (3), ovarian (11) and
pancreatic (4) strata are small; these counts are models, before donor grouping.

The current pilot's Avana/2DS protocol does not admit these assays. This round
proposes a separate protocol rather than treating the counts as a pass under the
old rules. See [the dataset audit](DATASETS.md) and [proposed study](PROTOCOL.md).

## Best contribution opportunity

Test the reliability and limitations of compact dependency predictors across
datasets. Produce reusable identity mappings, measurement contracts, comparator
checks, independent reproductions and falsified assumptions. Credit each artifact
according to what it establishes. A new treatment or biological mechanism is not
required for a useful computational contribution.

A directly relevant October 2026 paper already examined 2D-to-organoid prediction
using these resources. Its reported external advantage over lineage prediction was
uncertain. The general transfer question therefore needs a novelty/replication
review, not a first-study claim. We have read its published summary, not reproduced
its results. [Fırat and Kılıçaslan](https://doi.org/10.3390/biology15191782).

## Reproduce this round

From the repository root:

```sh
python3 src/qualification.py
.venv/bin/python -m pytest -q
python3 research/readiness-20261021/check_manifest.py
python3 research/qualification-20261021/check_manifest.py
```

The first command recomputes the graph and counts from hash-bound metadata and
compares the entire result with `cohort-audit.json`. The test suite includes
transitive alias matching, missing/duplicate rejection, source tampering and a
guard that forbids reading response or molecular-feature matrices during the audit.
The older 82-file preparation manifest remains intact.

Optional source replay needs Python with openpyxl and curl:

```sh
python research/qualification-20261021/fetch_metadata.py
python research/qualification-20261021/extract_metadata.py
```

Only allowlisted metadata are retrieved. The Sanger supplementary ZIP is read by
locked byte ranges; dependency tables are not downloaded or decompressed. Workbook
replay reads only identity/availability columns from named metadata sheets. Raw
workbooks stay in ignored `data/raw/`, and may contain other published metadata.
Committed extracts omit clinical attributes and culture recipes. Grouping hashes
are reproducible identifiers, not a claim of anonymization or security.

## Work and decisions remaining

- [Five bounded tasks](TASKS.md), with machine-readable first steps in `tasks.json`.
- [Scientific-owner brief and relevant groups](OWNER_BRIEF.md), prepared but unsent.
- [Independent review and decision gates](REVIEW.md). Outcomes remain unopened by
  this project; published summaries are already known and must be disclosed.

We can run the metadata and development-only tasks now. A scientific owner must
approve the research question, assay contract and evaluation plan before the new
outcome evaluation. An unrelated contributor must complete a trial before we can
claim an independent onboarding success. Securing those people remains outside
what this local preparation establishes.
