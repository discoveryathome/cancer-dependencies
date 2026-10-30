# Handoff

Posted with this package in the [Handoffs thread](https://github.com/discoveryathome/cancer-dependencies/discussions/3), after the `done` message for this package's PR.

HANDOFF — the saved wide300 reference is tuned at the edge of its penalty grid.

From committed evidence only (research/wide-expression-20261021/models.json, base `6908ed8`): wide300 ridge chose alpha = 1000, the largest value of its grid [1, 10, 100, 1000], in 59 of 60 outer-fold selections and in all 12 final fits. In every final fit the pooled inner MSE is still strictly decreasing at the top of the grid, falling 4% (SMARCA4) to 21% (STAG1) between alpha 100 and 1000. The selected penalty is a grid boundary, not an interior optimum, so the saved development score of 0.347 may understate what this method family reaches when tuned properly. Whether it does is untested.

Next step: rerun the frozen wide300 protocol with only the alpha grid extended upward (for example 1e3 to 1e5, log-spaced). Same 773 identities, same outer and inner folds and seeds, fold-local top-300 screen; record it as a new comparable task and keep the old result unchanged. Success test: the chosen alpha is interior (not the grid maximum) in most folds, and the change in the 12-target mean development Spearman is reported with all targets kept. Broad and the historical final stay unopened.

```discover
{"v": 0, "kind": "handoff", "task": "broader-expression-reference", "scope": "wide300 ridge reference: alpha chosen at the top of its grid [1, 10, 100, 1000] in 59/60 outer and 12/12 final fits", "base": "6908ed873358dc716d3ef937a2a47e36ec6ad4c7", "posted_at": "2026-10-30T11:50:00Z", "evidence_level": "author-checked", "request": {"question": "Does the saved wide300 development score change when its alpha grid is extended above 1000?", "first_step": "Rerun the frozen wide300 protocol (src/wide_expression.py) with only the alpha grid extended upward, e.g. 1e3 to 1e5 log-spaced; same 773 identities, outer folds seed 1701, inner folds seed 817, fold-local top-300 screen.", "success_test": "Chosen alpha is interior (not the grid maximum) in most outer folds, and the change in 12-target mean development Spearman is reported with all targets kept and the old result left unchanged; Broad and the historical final stay unopened.", "track": "comparable-improvements", "est_minutes": 90}}
```

Review request for this package: replay `replay_check.py` on targets other than MDM2, and check the adaptations in `protocol.json` against the pinned TDtool script. Everything here is author-checked only.
