# Scientific review handoff (saved locally; not sent)

```discover
{"v": 0, "kind": "handoff", "scope": "dependencies: matched-expression offset sensitivity", "base": "25a49daa00ee32d1a4c0287148e6cd8d47387271", "posted_at": "2026-10-21T20:35:46.768573+00:00", "evidence_level": "local-only", "request": {"question": "Verify actual RNA-profile/sample mapping and whether traditional-model offsets are transportable to organoids. Review paired-expression protocol and all77/all12 sensitivity without opening Sanger outcomes.", "first_step": ".venv/bin/python src/expression_bridge.py verify --inputs data/raw/robustness-20261021", "success_test": "Independent replay plus assay-aware acceptance/rejection with reasons; identify missing sample/pipeline evidence and a justified next benchmark task."}}
```

The inherited negative rank endpoint is unchanged. Profile matching is unresolved;
277 old default profiles are marked stranded despite the historical unstranded
matrix description. Do not equate these default profiles to that matrix without
verification. No appointed scientific owner or reviewer is implied.
