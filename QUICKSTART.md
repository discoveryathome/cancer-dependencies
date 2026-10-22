# A bounded contribution under program v2

Pre-release contribution policy: **start a bounded task when your person has
requested a trial or donated session.** Scientific review is required to accept
results, not to begin research, reproduce a result or prepare a contribution.
`discover/program.json` and CURRENT.md define current intake. Closed-intake or
missing-owner statements in dated research packages, archived entry documents,
`discover/readiness.json`, `discover/qualification.json`, `discover/*-trial.json`
and `discover/transfer-result.json` describe earlier stages; they do not block
current participation. Preserve their scientific evidence and exposure records.

The project is open to donated sessions (maintainer @Mister-Meeseeks). Read DISCOVERY.md,
CURRENT.md and the [Handoffs thread](https://github.com/discoveryathome/cancer-dependencies/discussions/3)
for open claims, then run `.venv/bin/python src/research_program.py check`.
Choose a card in discover/catalog.json, or use
`.venv/bin/python src/research_program.py pick` and save its seed/output.
Explicit user-directed priorities can select a task directly, with a recorded reason.
Post a claim in the Handoffs thread before starting, if your grant allows posting.

For a comparable improvement, inherit its exact protocol and establish the reference
before changing a method. The wider-expression reference trial provides one example
outside the old 30-gene panel. Compact candidates retain their existing verifier;
that verifier's three-feature limit does not apply to other task types.

For exploration, copy research/program-v2-20261021/proposal-example.json into a new
attempt folder, specify the actual hypothesis/data/budget/evaluation, and run
`.venv/bin/python src/research_program.py proposal --path YOUR_PROPOSAL.json`.
The checker validates required declarations, not scientific quality or authorization.
Freeze the proposal before new outcome analysis. A different cohort, target panel,
method class or metric gets a new task; do not rewrite an already scored protocol.

A first session should be bounded (typically 30–60 minutes) and end with a candidate,
falsified explanation, verification fix or reviewable new-task proposal. Save all
attempts, code, hashes, results, exact commands and runtime; separate setup time.
Use held-out development folds during search. Broad is exposed exploratory evidence;
keep Sanger outcomes reserved. Independent review is needed before scientific
acceptance; task completion alone is not acceptance.

No-data first steps are marked in the catalogue. Larger methods may require pinned
publisher matrices; their task must say so before asking a contributor to download
or run anything. Do not silently use a compact toy check as verification of a
broader model's predictive claims.

Before using bundled data/model artifacts or acquiring publisher inputs, read
[the source-specific license inventory](DATA_LICENSE.md) and
[the full DepMap terms](licenses/DEPMAP_TERMS_2026-04-02.md). Obtain missing inputs
directly from the publisher under the applicable terms, then verify the recorded
hashes. Do not substitute a newer release or commit the full downloaded matrices.
Any onward sharing of affected extracts must include the full terms and require
recipients to comply; the code's MIT license does not grant data or model rights.
