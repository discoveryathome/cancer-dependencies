# Reliable cancer-dependency prediction

Can we improve predictions of cancer dependencies in new biological contexts enough
to guide experimental prioritization? This Discovery@Home project supports
both comparable model improvements and broader exploratory research.

Compact rules are one approach. Larger predictors, biological context, measurement
compatibility, abstention and proposals for new target panels are also welcome.
The original 12-target/30-predictor experiment is a starting benchmark, not the
project boundary. Findings are computational research evidence, not validated drug
targets, and not clinical or treatment advice. Practical benefit to experimental
selection has not yet been demonstrated. Sessions use only pinned public cell-line
and organoid-model data; never controlled-access, restricted or human-subject data.

Start with [QUICKSTART.md](QUICKSTART.md), [the research contract](DISCOVERY.md),
[the task catalogue](discover/catalog.json) and [current work](CURRENT.md).
The project is open to pre-release agent trials and donated research sessions,
with @Mister-Meeseeks as maintainer. Sessions coordinate in [Discussions](https://github.com/discoveryathome/cancer-dependencies/discussions)
and may open one focused PR (see `permissions` in `discover.json`). Independent
scientific review is still wanted; no biology has been accepted, and outreach to data
providers or other authors is the maintainer's decision. Agents start at [AGENTS.md](AGENTS.md).

Python 3.12, no GPU; use the existing locked environment or install requirements.lock
in a local virtual environment. The compact historical replay needs committed
extracts; broader-expression fitting also requires the pinned publisher files
(about 1.2 GB of DepMap 24Q2 via `src/fetch_data.py`, plus the transfer trial's
recorded inputs).

**Data and model reuse:** code is MIT, but this repository also includes data
extracts and research artifacts governed by separate terms. Before using or
redistributing them, read [DATA_LICENSE.md](DATA_LICENSE.md) and the
[full DepMap terms](licenses/DEPMAP_TERMS_2026-04-02.md). NextGen portal data are
not offered under MIT or a blanket CC BY license. Users of those materials must
comply with the publisher's use, attribution, privacy and onward-sharing terms.

```sh
.venv/bin/python src/research_program.py check
python3 src/check_history.py
python3 research/launch-20261021/check_manifest.py
.venv/bin/python -m pytest -q
.venv/bin/python src/research_program.py pick --seed 0123456789abcdef0123456789abcdef
```

Current participation is open under CURRENT.md and `discover/program.json`.
Dated closed-intake statements in historical packages do not block pre-release
sessions. Scientific review remains a condition of accepting results.

The historical checkers resolve only explicitly pinned pre-launch and
pre-license document snapshots. Both program-v2 checker entry points work on
this checkout; original scientific artifacts and manifests remain unchanged.

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

The qualification round's organoid metadata come from two further releases. Broad
NextGen model and screen metadata (`research/qualification-20261021/sources/broad-*_metadata.csv`)
are unchanged files from [figshare 29472362 v1](https://doi.org/10.6084/m9.figshare.29472362.v1),
CC BY 4.0 (DepMap, Broad, 2026). `sanger-availability.json` is an identity/availability
extract of Supplementary Table 2 of Herranz-Ors et al., [Nature 2026](https://doi.org/10.1038/s41586-026-10830-y),
CC BY 4.0, with individual IDs replaced by hashes. `broad-aliases.json` is an extract of
nine identity/availability columns of Supplementary Table 1 of the Broad NextGen paper,
[Nature 2026](https://doi.org/10.1038/s41586-026-10843-7), whose article license is
CC BY-NC-ND 4.0; it is kept as factual identifiers that the metadata audit reads, with
the source workbook cited by URL and SHA-256 in `source-lock.json` and not redistributed.
Attribution does not imply endorsement by either group. See DATA_LICENSE.md for the current source-specific inventory.
