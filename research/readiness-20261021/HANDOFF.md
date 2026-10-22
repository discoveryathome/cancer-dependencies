# Local preparation handoff

Read [README.md](README.md), [REVIEW.md](REVIEW.md) and [EVALUATION.md](EVALUATION.md).
The preparation is author-checked and committed locally. Scientific review,
confirmation and public intake remain pending; no external message was sent.

The manifest verifies the preparation base before starting a contribution.
Intentional candidate-code edits belong in a new commit with their own source
bindings; do not rewrite the base manifest to hide an intended or accidental change.

```discover
{"v":0,"kind":"handoff","scope":"dependencies: preparation for scoped computational contributor trials; versioned inherited controls, validation and outside-review package","base":"703781fa998c421d063f76ae1c997a4de827fd1e","posted_at":"2026-10-21T16:16:46.054943+00:00","evidence_level":"local-only","request":{"question":"Review scientific assumptions, future evaluation design and intake prerequisites in REVIEW.md and EVALUATION.md.","first_step":".venv/bin/python src/readiness.py verify --candidate research/readiness-20261021/candidates/SMARCA2.json","success_test":"Return exact commit/hashes, checks, limitations, review capacity and a scoped decision. No independent review is assumed."}}
```
