# Reproducible cancer-cell dependency rules

Can a compact molecular rule predict which previously unseen cancer cell lines depend
on a gene? This LOCAL Discovery@Home pilot compares interpretable rules with standard
predictive baselines using existing DepMap CRISPR results. Findings are **computational
research hypotheses**, not validated drug targets. Cancer-versus-normal selectivity is
not measured.

The broad prediction problem already has successful examples: [Shi et al. (2024)](https://doi.org/10.1038/s43018-024-00789-y)
reported 2,045 multi-omics elastic-net models passing their cross-validation criteria.
That literature result is not this pilot's baseline score. Our opportunity is compact,
auditable rules that retain value under held-out and cross-lineage testing.

## Run locally

Python 3.12, no GPU. From this directory:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pytest -q
.venv/bin/python src/verify.py
```

The verifier uses committed, attributed compact extracts; it does not require a 1.24 GB
download. It checks input hashes, identity separation, completeness of final cohorts,
frozen-model predictions and reported scores. It does not independently prove that a
model was selected honestly; full replay checks the implemented fitting procedure.

Full search replay from compact inputs (use a new output directory):

```sh
.venv/bin/python src/benchmark.py develop --out research/replay
.venv/bin/python src/benchmark.py finalize --out research/replay
.venv/bin/python src/verify.py research/replay/VERIFY.json
```

To rebuild the compact extracts from the publisher's files:

```sh
.venv/bin/python src/fetch_data.py
.venv/bin/python src/prepare.py
```

The source release is [DepMap 24Q2 Public v1](https://doi.org/10.25452/figshare.plus.25880521.v1),
CC BY 4.0, attributed to DepMap, Broad (2024). `data/source-lock.json` pins publisher
URLs, MD5 checks and SHA256 hashes; `data/gene-map.json` retains original gene IDs.
`data/panel-lock.json` pins the exact extracts. Read [DATA_LICENSE.md](DATA_LICENSE.md).

## Read the evidence

- [Protocol and review rules](DISCOVERY.md), [agent entry](AGENTS.md).
- [Preregistration](config/PREREGISTRATION.md) and [research brief](setup/RESEARCH_BRIEF.md).
- `research/initial/`: search ledger, outer and lineage evaluations, null permutations,
  frozen models, final evaluation and verification certificate.
- `reports/`: data and scientific audits, contributor-trial assessment.
- [Authoritative frontier](discover/frontier.json): accepted scope and open obligations.

This is an unlisted local proposal. No maintainer has agreed to serve; donor intake is
closed, no hub consent exists, and no GitHub repository or posts have been created.
