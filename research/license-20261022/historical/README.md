# Reliable cancer-dependency prediction

Can we improve predictions of cancer dependencies in new biological contexts enough
to guide experimental prioritization? This private Discovery@Home pilot supports
both comparable model improvements and broader exploratory research.

Compact rules are one approach. Larger predictors, biological context, measurement
compatibility, abstention and proposals for new target panels are also welcome.
The original 12-target/30-predictor experiment is a starting benchmark, not the
project boundary. Findings are computational research evidence, not validated drug
targets. Practical benefit to experimental selection has not yet been demonstrated.

Start with [QUICKSTART.md](QUICKSTART.md), [the research contract](DISCOVERY.md),
[the task catalogue](discover/catalog.json) and [current work](CURRENT.md).
There is no appointed scientific owner; intake remains closed. Nothing in this
update authorizes public launch, outreach or a claim of accepted biology.

Python 3.12, no GPU; use the existing locked environment or install requirements.lock
in a local virtual environment. The compact historical replay needs committed
extracts; broader-expression fitting also requires the pinned local publisher files.

```sh
.venv/bin/python src/research_program.py check
python3 src/check_history.py
.venv/bin/python -m pytest -q
```

Existing literature already studies dependency prediction and organoid transfer.
Our expanded reference is not a reproduction of a published model or a claim to
beat it. See [the updated research context](research/program-v2-20261021/CONTEXT.md).

Historical evidence remains available in research/initial/, research/contributor-trial/,
research/readiness-20261021/, research/transfer-results-20261021/ and later diagnostic
packages linked from CURRENT.md. Original setup/replay instructions and root docs
are preserved in [the entry snapshot](research/program-v2-20261021/historical-entry/README.md).
Its relative links describe the original repository layout; use the migration's
base commit for the complete old workflow. [DATA_LICENSE.md](DATA_LICENSE.md)
and source manifests retain data attribution and licensing distinctions.
