# Five bounded contributor tasks

These are local qualification cards, not live donor traffic. Their first commands
are recorded in `tasks.json`. Time boxes are proposed contributor budgets, not
measured newcomer completion times. Save each submission with source URLs/versions,
artifact hashes, exact commands, limitations and a review request. Do not download
new response matrices as part of these cards.

## Q1 — independently check one identity exclusion (30–45 minutes)

Start: `python3 src/qualification.py`.

Choose one edge/component from `cohort-audit.json`. Trace its model names, aliases,
historical linkage and any related Sanger model to the pinned metadata. Report
whether the exclusion is supported and whether the whole component was handled
correctly. For unresolved Broad donor links, record the missing crosswalk rather
than treating a distinct ModelID as an independent donor.

Deliverable: a short evidence record, a proposed mapping correction if justified,
and the resulting count change or explicit no-change finding. A second person must
be able to follow every mapping. Accepted as identity audit, never predictive gain.

## Q2 — complete one part of the assay contract (45 minutes)

Start: `python3 -m json.tool research/qualification-20261021/measurement-contract.json`.

Choose expression transformation, mutation semantics, copy-number semantics,
gene identifiers, or response processing. Use primary documentation and published
source code to specify the old/new definitions and compatibility limits. Code
inspection only: do not run the upstream pipelines or load outcomes. Distinguish
library/culture differences from processing artifacts and avoid causal attribution
from an observational contrast.

Deliverable: a source-cited contract patch with exact file/version locations,
allowed transformations and unresolved fields. Scientific review is necessary to
approve equivalence; a precise incompatibility is a valid completion.

## Q3 — reproduce a compact candidate and its stronger controls (30 minutes)

Start: `.venv/bin/python src/readiness.py verify --candidate research/readiness-20261021/starter.json --refit`.

Review the development-only fold boundaries, training-selected strong baseline,
candidate source/refit binding and complete reporting. Identify the candidate's
required input features and document which external feature definitions would need
to match. Do not read new cohort values or tune on historical final/Sanger results.

Deliverable: independent replay log, feature contract and any actionable defect or
clear reproduction result. Known-control recovery and source verification receive
replication credit, not biological novelty credit.

## Q4 — specify an independent reproduction of the recent transfer study (45 minutes)

Start: `python3 -m json.tool research/qualification-20261021/prior-work.json`.

Obtain the primary methods/code documentation, then compare its target panel,
feature universe, identity exclusions, freezing history, metrics and comparators
with our proposal. Identify one narrow result that can be independently reproduced
and why a researcher would use that reproduction. Our round read the abstract and
metadata; it did not reproduce that study. Reading further outcomes consumes
blinding for the relevant question and must be recorded.

Deliverable: a reproduction specification and exposure declaration, with pinned
code/data references or explicit missing inputs. No execution of the new outcome
evaluation until the owner approves its replication scope. Matching their cohort
count alone does not verify their findings.

## Q5 — review support and precision before evaluation (45–60 minutes)

Start: `python3 src/qualification.py`.

Use the reserve lineage counts, old protocol and proposed endpoints to state which
claims cannot be supported by the current metadata alone. Draft a power/precision
plan using development data or explicitly synthetic assumptions. Preserve grouped
identities and distinguish total sample size from each biomarker branch. Do not
estimate a desired effect by inspecting the proposed evaluation outcomes.

Deliverable: a statistical-review note listing the effect/precision assumptions,
missing eligibility counts, grouping and multiplicity rules. A qualified reviewer
must approve the design; a simulated pass does not establish external support.

## Trial acceptance

For each independent contributor record assignment, prior familiarity, start/end
time, assistance, output, reproducibility and reviewer minutes. Ask the owner
whether the artifact is useful and what they would do with it. The first three
contributors should cover different tasks. The author running entry commands is
only a workflow check, not an independent newcomer trial.
