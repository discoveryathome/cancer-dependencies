# Reproducibility record — 2026-10-20

**Author-checked computational reproduction passed. Independent review has not occurred.**
The source snapshot used for the fresh checkout was
`1ae3bfcb95f23785521c6773974a2b26b2cbc3ce`. It was replayed in `setup/replay/`
using the same pinned Python 3.12 environment on the same computer. This checks a fresh
checkout and fresh processes, not another operating system, independently installed
environment, independent person, or independent implementation. Final package verification
records identify the later packaged commit and the precise checked scope.

## Checks completed

- Full baseline replay: repeated outer/inner fitting, lineage holdouts, selection-aware
  null permutations, final and external evaluation. Scientific outputs match within the
  declared numerical tolerances; runtime/platform fields are excluded.
- Full contributor-trial replay: repeated feature selection, tuning, outer/lineage fits,
  final/external scoring and the aggregate comparison. Scientific outputs match.
- Frozen prediction certificates: all 132 baseline and 24 contributor model/target
  results recomputed, with input hashes, identity separation and complete cohort checks.
- Development re-selection/refitting: all 156 final models reproduced in 44.13 seconds.
- Statistical audit: outer metrics and primary rule predictions, paired bootstrap
  intervals, selection-null p-values, BH corrections and every internal decision gate
  recomputed. The standalone final statistical check reused saved null selections;
  the full baseline replay above reran those selections.
- Seventeen tests passed, including meaningful altered-input/output and leakage checks.
- All fifteen catalogue first-step commands executed successfully.
- Reference schemas pass except the disclosed empty maintainer prerequisite. The local
  validator reports that exception explicitly. This is not a donor-ready project.

Evidence is retained in `setup/logs/`: `baseline-replay-comparison.log`,
`trial-replay-comparison.log`, `fresh-full-replay.log`, `fresh-trial-replay.log`,
`prediction-verification.log`, `refit-verification.log`,
`statistical-verification-final.log`, `tests-final.log`, `catalog-check.log`,
`catalog-first-steps.json`, and `local-validation.log`.

The full fresh baseline replay took 451.23 seconds wall time and 163.77 CPU seconds,
with 383,844,352 bytes peak resident memory. The fresh trial replay took 180.77 seconds
wall time and 64.95 CPU seconds, with 243,990,528 bytes peak resident memory. Host
contention affects wall time; these are measured runs, not performance guarantees.

## Reproduce independently

Follow [README.md](../README.md) to create a new environment from the hashed dependency
lock and run the tests and certificate checks. Then replay into new output directories:

```sh
.venv/bin/python src/benchmark.py develop --out research/replay
.venv/bin/python src/benchmark.py finalize --out research/replay
.venv/bin/python src/trial.py develop --out research/trial-replay
.venv/bin/python src/trial.py finalize --out research/trial-replay
.venv/bin/python src/compare_replay.py research/initial research/replay
.venv/bin/python src/compare_replay.py research/contributor-trial research/trial-replay
.venv/bin/python src/verify_statistics.py
.venv/bin/python src/replay_fit.py
```

The compact committed extracts suffice. Rebuilding extracts also requires the public
raw data download; publisher metadata, licensing, checksums and commands are recorded
in the source lock and data-license document. The source data were downloaded and
checksummed during setup; the fresh-checkout replay started from compact extracts.

## What this does not establish

These checks do not establish biological novelty, causality, cancer-versus-normal
selectivity, drug response, unbiased future adaptive search, robustness to another
DepMap release, or generalization beyond the reported cohorts. They do not independently
validate upstream normalization or the extraction logic. Baselines are restricted to
this fixed predictor panel; published genome-wide systems were not reproduced. The
independent-identity Sanger results are reported even when unfavorable or underpowered.
The final labels are now inspected and cannot serve as fresh confirmation for future
adaptive contributors. No scientific acceptance or independent-verifier credit is claimed.
