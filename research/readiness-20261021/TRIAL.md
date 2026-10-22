# Independent contributor trial protocol

This is a proposed small, supervised computational-methods trial. No independent
contributor has run it yet, and no scientific maintainer has accepted responsibility.

1. Read the preparation README and use the catalogue picker with an executed seed.
   Start with the exact positive control for the selected target or audit task.
2. Limit model changes to `src/compact_candidate.py`, <=3 molecular features, the
   fixed development identities and folds. Use a bounded 30–45 minute session and
   record every attempted hypothesis, seed, fit and failed run. Keep original source
   and comparator inputs immutable.
3. Run `readiness.py propose --target TARGET --output research/UNIQUE/candidate.json`.
   It passes only training rows to the hook, refuses overwrite, computes all five
   folds, compares to fixed strong baselines, and verifies/refits the result.
4. Save the hook source, commit/hash, commands, resource use and all outcomes. Run
   `readiness.py verify --candidate PATH --refit` in the matching checkout. A reviewer
   must inspect the source for outcome leakage; arbitrary Python cannot be made
   trustworthy by an artifact checker alone.
5. Report skill versus the strong linear baseline, lineage and one-rule controls,
   feature complexity and per-lineage support. Repeated adaptive development scores
   are not independent validation. Explain failed hypotheses as well as gains.

The current two-feature control is already supplied for every target. Reproducing
it is an onboarding control, not a new biological finding. Useful contributions
include a real leakage/identity defect, a stronger evaluation, independent replay,
a well-supported negative result or a compact-method proposal awaiting confirmation.

Measure setup time, first valid artifact, total compute, source-review burden and
reproducibility. Do not count author-run preparation checks as newcomer success.
Stop and assess a few reviewed sessions before inviting wider traffic. Confirmation
remains gated by EVALUATION.md; old final and external outcomes are not a tuning set.
