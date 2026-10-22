# Frozen exploratory expression-transfer trial

The candidate models and evaluation pipeline are prepared. **The new expression
and response matrices have not been acquired or scored.** Data access is blocked
by the publisher portal's human-verification page. Metadata alone cannot establish
feature completeness or predictive performance.

This round follows the user's authorization to prepare and run a local exploratory
trial. It does not satisfy the scientific-owner acceptance proposed in the earlier
qualification round. No owner is appointed, public intake remains closed, and no
independent review, outreach or publication is claimed.

## Scope and measurement decision

The original development extract contains 773 identities. We fit six model families
for each of its original 12 dependency targets using only its 30 expression genes:
mean, lineage, self-expression, an expression rule, a selected strong expression
baseline, and the existing compact two-expression-feature ridge candidate. All
hyperparameter and feature choices use development data. The strong baseline is
selected by inner validation among self-expression and tuned ridge/elastic models.
It is a comparator within this 30-gene panel, not a genome-wide state-of-the-art claim.

The new manuscript describes expression as log2(TPM+1), matching the intended
expression contract. Its copy-number scale is log2(relative-to-ploidy + 1), whereas
the old panel uses absolute PureCN values. Reusing old thresholds across those
scales would be invalid. This trial therefore freezes an **expression-only**
protocol. It does not evaluate the original multimodal candidate unchanged.

The frozen metadata pool contains **77 provisional Broad dome-screened (3DO)
organoids**, one passing Humagne-CD screen and one representative per recorded
identity component. Culture formats are not pooled. Known historical overlap and
the non-cancerous annotation are excluded by the prior qualification audit.
Unresolved donor/alias and engineered-status information remains a limitation;
77 is an upper bound before checking complete expression and target coverage.

The primary endpoint is the unweighted mean, across all 12 targets, of the compact
pair's Spearman correlation minus the strong expression baseline's correlation.
Every target must have at least 30 responses and defined correlations. Unsupported
targets make the primary endpoint unavailable, rather than disappearing from it.
The 2,000 paired bootstrap draws reuse the same identity resamples across targets.
Intervals are conditional on these fitted models and provisional identity groups.
Per-lineage results, rule-branch counts and raw MSE are descriptive diagnostics.
See [the frozen protocol](protocol.json) for all thresholds and exclusions.

## Evidence separation

`freeze` reads historical development data and qualified metadata. `predict` reads
the new expression matrix and locks predictions without parsing new responses.
`score` binds both input checksums, replays predictions and records exposure before
parsing the new response matrix. It refuses a second scoring attempt; `verify`
replays the recorded result. Artifacts are created exclusively, never overwritten.

Broad becomes exposed exploratory evidence when scored. Sanger outcomes remain
reserved; no Sanger matrix is downloaded or opened by this pipeline. Published
study summaries were already known before fitting. The trial is not a replication
of the recent paper's full pipeline and cannot establish a novel biomarker, useful
treatment, independent confirmation or public-launch readiness.

## Validation and continuation

The tests use synthetic matrices, including outcome-read guards, missingness,
duplicate identifiers, changed source bytes, replay tampering and an independent
SciPy check of the rank metric. Synthetic scores are not biological results.
`verify-fit` independently reruns all 12 development fits and cohort selection.
See [validation evidence](validation.json) and [the continuation instructions](HANDOFF.md).

The first refit check found a tuple/list mismatch in serialized tuning diagnostics.
The numerical BRAF refit matched after JSON normalization. Diagnostics now use
JSON-stable lists; the original freeze and source are retained under `superseded/`.
The corrected freeze was created before any new outcomes were opened. Do not use
the superseded artifact for prediction or score replay.

## Sources and unresolved access

The [Broad manuscript](https://www.nature.com/articles/s41586-026-10843-7) and
[publisher analysis code](https://github.com/broadinstitute/DepMap-NextGen-Public)
identify the manuscript release inputs. The inspected upstream `src/data_utils.py`
maps expression to `next_gen_expression.csv`, indexed by model; upstream screen
processing uses `screen_gene_effect.csv`, indexed by screen. These are the intended
contracts, still to be confirmed against the actual downloaded files and release
definitions. The [manuscript download page](https://depmap.org/portal/data_page/?releasename=NextGen+Model+Manuscript+2026&tab=allData)
requires human verification in this session. Do not silently replace its files
with 26Q3, supplementary analytical summaries, or a different release.

Exact file checksums and source-specific local-use terms remain pending in
`source-manifest.template.json`. The template deliberately fails validation until
completed from actual verified inputs. Raw matrices belong in ignored `data/raw/`.
