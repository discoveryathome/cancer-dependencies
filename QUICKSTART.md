# A first 30–60 minute contribution

This is a local proposal, not an open donor call. After a maintainer opens intake, a
first contributor should use the compact committed panel, not download the raw release.

1. Read AGENTS.md, the frontier, and the chosen catalogue card (5–10 minutes).
2. Create a local Python 3.12 environment and install requirements.lock with hashes;
   run `.venv/bin/python src/doctor.py` and `.venv/bin/python src/verify.py`.
3. Run one bounded development-only task:

   ```sh
   .venv/bin/python src/contribute.py run --target SMARCA2 --artifact research/my-attempt/RESULT.json
   .venv/bin/python src/contribute.py verify --artifact research/my-attempt/RESULT.json
   ```

4. Inspect the rule, support and five held-out-fold scores. Audit a biological assumption,
   propose a small model change, or find an evaluation bug. Keep a complete attempt log.
5. Save the patch, protocol, outputs, runtime and limitations in a result package. Do not
   optimize against research/initial final scores or call a known paralog result novel.

The starter compares a one-feature threshold rule, a two-feature biological prior, and a
blind two-feature model. Its score is exploratory development evidence. Improvement on
this repeatedly inspected set needs confirmation on a new, curator-sealed cohort.
A negative result or a verified leakage fix is useful progress; it is not a new biomarker.

What counts as a concrete contribution: a reproducible score/complexity improvement on
specified development splits, an independently reproduced result, a scientifically relevant
verifier rejection test, or a sourced correction to a biological/assay assumption. A longer
GPU run, an unverified correlation, or another rendering of a known biomarker does not count.
