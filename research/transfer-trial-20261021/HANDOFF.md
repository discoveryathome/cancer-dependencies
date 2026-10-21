# Continue the local exploratory trial

Run commands from the repository root using its existing locked Python environment.
The current branch is `trial-cancer-transfer-20261021`; the starting commit was
`845bb4ce7af990bb92541106ed083f90ebc05495`.

## Before external scoring

1. Complete the human verification in the Chrome session “🧬 Dependency trial”.
   Obtain the exact **NextGen Model Manuscript 2026** release files
   `next_gen_expression.csv` and `screen_gene_effect.csv`. Keep the downloaded
   bytes in `data/raw/transfer-trial-20261021/`. Do not open Sanger outcomes.
2. Check the actual publisher release definitions, header identity units and
   applicable local-research terms. Expression must be model-indexed log2(TPM+1),
   and response must be screen-indexed Chronos gene effect, with stable Entrez
   identifiers in `SYMBOL (ID)` columns. If incompatible, stop and document a
   protocol revision before inspecting response values. Do not transform scales
   or substitute files opportunistically.
3. Copy `source-manifest.template.json` to the raw directory as `source-manifest.json`.
   Record SHA-256 hashes of the exact input bytes, publisher URL and terms URL.
   Set `terms_status` to `reviewed-for-local-research` only after actual review.
   Hashing bytes does not require examining outcome values. Retain any publisher
   checksum and its verification evidence as additional provenance.
4. Run the integrity/refit checks below. The frozen candidates are already present;
   do not rerun `freeze` into the existing run directory. Read the protocol before
   opening outcomes. No changes may be selected using new response values.

```sh
python3 research/readiness-20261021/check_manifest.py
python3 research/qualification-20261021/check_manifest.py
python3 research/transfer-trial-20261021/check_manifest.py
.venv/bin/python src/transfer_trial.py verify-fit --out research/transfer-trial-20261021/run
.venv/bin/python -m pytest -q
```

## Predict, score once, replay

After the exact inputs and completed source manifest are available:

```sh
.venv/bin/python src/transfer_trial.py predict \
  --out research/transfer-trial-20261021/run \
  --inputs data/raw/transfer-trial-20261021 \
  --source-manifest data/raw/transfer-trial-20261021/source-manifest.json
.venv/bin/python src/transfer_trial.py score \
  --out research/transfer-trial-20261021/run \
  --inputs data/raw/transfer-trial-20261021 \
  --source-manifest data/raw/transfer-trial-20261021/source-manifest.json
.venv/bin/python src/transfer_trial.py verify \
  --out research/transfer-trial-20261021/run \
  --inputs data/raw/transfer-trial-20261021 \
  --source-manifest data/raw/transfer-trial-20261021/source-manifest.json
```

`predictions.json` records complete and excluded expression rows. `exposure.json`
marks outcome access, even if subsequent scoring fails. `results.json` records all
12 targets, comparator scores, missing outcomes, branch/lineage support and the
primary endpoint. If scoring fails after exposure, retain that record and report
the failure before any repair; do not delete it to claim a new unopened trial.

Report losses and unsupported targets alongside gains. Any further tuning on Broad
requires an explicitly exploratory follow-up. Compare the results with the stated
transfer question and prior work; do not infer clinical usefulness or causal effects.
Scientific owner recruitment, identity/assay review and independent contributor
validation still remain outside this local trial. Do not change intake or publish
raw matrices or embedded expression rows without checking their redistribution terms.

The preparation manifest covers the frozen scaffold only. After scoring, retain
the original manifest and create a separate result manifest binding the completed
source manifest, predictions, exposure record and results.
