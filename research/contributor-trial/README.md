# contributor-trial: result package

Test early contributor progress, biological priors, home-PC feasibility and featured-pilot suitability.

Evidence level: author-checked only. Read ../../reports/RESULTS.md for every target,
negative result, complexity and uncertainty, and ../../reports/FEATURED_PILOT_ASSESSMENT.md
for the contributor assessment. Known biological priors are not novel findings.

## Reproduce

From the repository root:

```sh
.venv/bin/python src/verify.py research/contributor-trial/VERIFY.json
.venv/bin/python src/replay_fit.py
```

The first command checks frozen models, complete final cohorts, hashes, predictions and
scores. The second reselects and refits all final baseline and trial models from development.
See ../../README.md for full outer/lineage/null replay commands and limitations.
VERIFY.json records argv commands, input hashes, pins and timeouts; SOURCES.json records
live source hashes and Git blobs. No executable model pickle is loaded.

## Open next questions

See TASK.json. Independent reproduction and fresh-cohort confirmation remain open.
An appointed maintainer must review the evidence before accepting a frontier change or
opening donor intake. The local proposal deliberately has no invented maintainer.

Credit: Codex agent implemented and tested this package. DepMap, Broad (2024),
https://doi.org/10.25452/figshare.plus.25880521.v1 supplied the CC BY 4.0 data.
