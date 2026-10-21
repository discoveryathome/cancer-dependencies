# Proposed cross-dataset study — review draft, not preregistered

Question: **Do compact predictors retain useful information about dependency
differences across models beyond lineage and stronger conventional predictors,
and which failures can we establish reproducibly?**

This is a new study proposal. The original Avana/2DS preregistration, historical
results and 24Q4 support gate remain unchanged. No new confirmatory fit or outcome
evaluation has occurred. Approval fields in `review.json` are deliberately empty.

## Proposed scope

Keep the existing 12 targets and development-only 773 identities as the starting
scope. An owner may approve a narrower biologically motivated question **before
opening new outcomes**, with the rationale and omitted targets recorded. Do not
select targets because a new cohort or published score makes them look promising.
Gene identifiers must be matched to an authoritative mapping; absence remains
absence rather than an invitation to choose a favorable substitute.

Prioritize Sanger as a candidate external-assay evaluation after the current
identity exclusions and processing review. Treat Broad as a separate resource
whose role must be declared in advance: development/domain-diagnostic data or a
reserved evaluation, not both. CNS and organoid populations have different
upstream processing roles; do not automatically pool them. Using one resource for
adaptation consumes its role as candidate-unseen confirmation. Related models in
the other resource must remain excluded.

## Freeze before outcomes

Record the exact dataset versions, identity component list, representative rule,
target list, model source/hyperparameters, feature contract, training artifacts,
seeds, comparator fitting, all eligibility checks, metrics and uncertainty plan.
Record literature and data exposures. A curator checks feature/target availability
and subgroup counts without revealing new response associations to developers.

Keep the existing >=30 external-unit floor and >=15 observations in each branch
for binary-rule claims. These do not establish adequate power. Before freezing,
the statistical reviewer must specify a useful effect size, required precision,
power/design justification and multiplicity treatment for the actual comparison.
Unsupported targets appear as unsupported, not silently excluded from a favorable
aggregate. Rules for any aggregate denominator must be fixed in advance.

## Comparators and metrics

Carry forward mean, lineage, self-expression, rule and nested-selected strong
linear comparators, all selected using development data only. The existing
strong baseline is strong **within the restricted 30-gene input panel**; beating
it would not establish superiority over genome-wide predictors. Review the newer
expression-model study and a broader conventional comparator before making a
competitive claim. Compactness can be a separate benefit if an owner defines a
useful complexity/accuracy tradeoff prospectively.

For review: use target-wise cross-model rank association as a candidate primary
transfer endpoint because assay score scales differ. The reviewer must decide
whether this endpoint answers a useful question and how to compare it to lineage
and strong linear predictions. Do not choose it after seeing it outperform MSE.
Absolute score error is a separate endpoint requiring a justified common scale;
calibration learned from new labels requires a distinct calibration partition.
Within-model gene ranking is a different question and cannot replace a failed
cross-model endpoint. Report ties and constant predictors explicitly.

Use identity-grouped uncertainty with the same resampled identities across targets
for aggregate contrasts. Report lineage composition, missingness, per-target
support and all failed comparisons. Small lineages can support descriptive
diagnostics without supporting claims about that lineage. A performance failure
does not identify its biological cause.

## Bounded contribution and evaluation process

Start with three independent contributors, each assigned one reviewed task from
TASKS.md. The number is an operational trial proposal, not a power calculation.
Record elapsed time, assistance, artifact, review time and whether the reviewer
would reuse the result. The author cannot serve as the independent newcomer.

At most one frozen candidate per contributor in the first reviewed evaluation
batch. Return all batch outcomes together. Further tuning uses development data;
after evaluation, that cohort is exposed for those candidates and cannot be reused
as fresh confirmation without acknowledging adaptation. A new batch needs an
explicit reuse policy or genuinely new evidence.

Pilot success means contributors can complete useful, checkable work and an owner
can review it at sustainable cost. Predictive gains, verified negative findings,
reproducibility repairs and identity corrections receive distinct labels. A
biological novelty claim requires additional evidence and independent review.

## Stop or narrow the scope if

- No scientific owner can name a use for accepted artifacts and commit capacity.
- Independent audit leaves inadequate target/branch support or incompatible inputs.
- Shared processing prevents the proposed independence claim and no narrower claim
  is scientifically useful.
- Independent contributors mostly produce benchmark tuning that the owner would
  not reuse, or review consumes more effort than the outputs justify.

In that case retain the reproducibility/metadata resource and defer broad traffic.
Do not lower the support gate or substitute a more favorable metric to force a launch.
