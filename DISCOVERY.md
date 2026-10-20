# Research and contribution contract

The precise question is whether one to three molecular measurements can predict measured
CRISPR fitness effects in unseen cancer cell lines, with useful performance beyond lineage
and standard linear models. The pilot starts with one-feature rules on a fixed 12-target,
30-predictor panel. No biological result is accepted by a maintainer yet.

The literature frontier is summarized, with claim-by-claim sources, in
setup/RESEARCH_BRIEF.md. The current local computational frontier and its verification
scope live only in discover/frontier.json. No universal best algorithm is established by
these papers: datasets, target eligibility, splits and metrics differ. Do not compare
numbers across protocols as a leaderboard.

## Bottleneck and settled questions

Predictability is established for some dependencies. Known oncogene/paralog biomarkers
are positive controls. Increasing candidate count can increase apparent CV performance;
it does not establish generalization. Sanger data already included in an integrated
training release are not external replication. Same biological lines measured in two labs
are not twice as many independent samples. Copy-number correction and batch normalization
reduce artifacts but do not guarantee absence of them. Cancer-only screens cannot establish
normal-cell sparing, and genetic knockout effects need not match partial drug inhibition.

The hard work is independent validation and interpretation after controlling lineage,
measurement artifacts, public-data overlap, and adaptive search. A smaller reliable rule
can be more useful than a marginally better opaque predictor. A negative result that
exposes a failed assumption is also useful, but cannot be scored as a predictive gain.

## Evidence and evaluation

Follow the frozen preregistration. No target-panel selection or feature threshold fitting
on holdout outcomes. Identity components are grouped using public source IDs and aliases;
all target-eligible final models must be evaluated. All preprocessing learns within the
training fold. Record source checksums, exact input cohort, seed, full search space, all
failed candidates, complexity, runtime, validation and uncertainty. Release preprocessing
remains an upstream source of shared estimation, explicitly outside the fold-local fit.

Prediction certificate verification and source-rebuilding are separate checks. The fast
check recomputes all final predictions and metrics, not just reads a score. Full replay
checks fitted model and selection reproducibility. Neither is independent scientific
review. Literature novelty and mechanistic causality require further evidence.

The finite test family is 12 primary target/rule comparisons; descriptive secondary
comparisons have no unadjusted significance claims. Permutations repeat the complete
selection process. Final bootstrap intervals condition on the fitted model and resample
independent identities. Repeated-fold stability is not an independent-sample confidence
interval. Report effect size and supported cell counts before p-values.

## Work tracks

The machine-readable catalogue has four weighted tracks: replication, verifier hardening,
biological/novelty audits, and compact-model improvement. Pick using
`python3 setup/discover.pyz pick . --seed <32-hex-digit-seed>` if the hash-verified helper
is present. Otherwise use executed OS randomness and the protocol's weighted arithmetic.
Record the seed; never let the language model choose a supposedly random task.

An initial contributor trial is evaluated separately from setup. It must leave a concrete
patch, candidate, validation record, or falsified hypothesis. Record contributor minutes
and CPU/runtime separately. The primary agent is performing this trial; it is not an
independent newcomer or blinded reviewer.

## Review, credit, and publication

No appointed maintainer; no weekly capacity promised. All results are author-checked at
most. Intake is closed; there is no donor-launcher or hub consent. Before opening intake,
a person must explicitly accept responsibility and capacity, review the verifier and
frontier, and decide what acceptance means. The reference manifest schema requires a
nonempty maintainer array; this proposal deliberately leaves it empty rather than invent
a maintainer. Its schema exception must be resolved before publishing as a ready project.

Locally save contributions under research/<name>/ with their protocol, exact command,
outputs, hashes and a review note. Use the v0 message format for saved findings/handoffs.
One reviewer other than the author should replay results and inspect leakage and novelty;
an appointed maintainer decides whether to update the frontier. Passing code tests alone
does not accept a biological claim. Full public posting requires separate authorization.

Code is MIT; new documentation CC BY 4.0. Data retain publisher licensing. Contributor
credit follows the artifact/provenance record; list people only with their agreement.
Acknowledge agent assistance, source data authors, negative findings and independent
reproduction. Authorship is not promised automatically. Review capacity, not donated
compute, will determine how quickly meaningful contributions can be accepted.

## Limits of statistical and operational guarantees

The final test is separated by workflow and inspected once after freezing; its labels are
in public files, not protected by an access-control service. An adversarial contributor
can read them. Future adaptive work cannot use that same test for independent confirmation.
The verifier checks arithmetic and explicit provenance; an independent review must inspect
how a candidate was chosen. Re-fitting selected models is a stronger computational check
than merely reproducing their predictions, but still not a novelty or causality check.

The 12 primary development permutation p-values receive BH adjustment. Final target-level
bootstrap intervals are individual conditional intervals, not simultaneous familywise
coverage. The conjunction of pilot screening gates is not a new formal FDR guarantee.
Cross-lineage, batch and external tables are sensitivity evidence; small subgroup cells
are not independent discoveries. No significance claim is attached to secondary rankings.
The trial has one declared aggregate comparison; its two additional comparator rankings
are descriptive. Confidence intervals omit training-data and dataset-selection uncertainty.
