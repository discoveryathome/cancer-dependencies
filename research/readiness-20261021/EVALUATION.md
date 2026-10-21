# Future confirmation plan — data gate not met

The original final test and Sanger transfer results are exposed historical evidence.
A new partition of those inspected labels is not fresh confirmation. All preparation
model work is restricted to the development-only extract, and all comparisons are
exploratory. Independent contributor replication remains useful on that scope.

## Completed metadata-only audit

Source: DepMap 24Q4 Public v1, DOI 10.25452/figshare.plus.27993248.v1, CC BY 4.0 in
its pinned publisher record. `sources/` holds the publisher metadata and four small
model/screen/profile metadata files. No gene-effect or molecular-feature matrix was
fetched. Run `python src/fetch_reserve_metadata.py` to verify/re-fetch only this
allowlist, and `python src/reserve_cohort.py` to regenerate the audit.

Identity union uses ModelID plus every original identity key across both releases,
including transitive matches and numeric COSMIC-ID normalization. It excludes any
component connected to any model in the old release metadata, not merely training
rows. Annotated engineered/non-cancer models are excluded; unknown engineered or
identity status remains a limitation. Use one representative per new component.

The result is 135 new annotated cancer-model identities, of which only 17 have
passing/releasable 2DS screens and 12 have passing Avana screens. RNA-profile listing
is reported separately; it does not establish usable values for the required genes.
The existing >=30-model external gate is not satisfied, even before per-target
missingness or rule-branch checks. Do not relax it or merge overlapping identities
to manufacture a viable cohort. No confirmation experiment is ready to execute.

## Required steps before opening new outcomes

An independent curator must identify a sufficiently supported public cohort and
approve release-specific terms, identity exclusions, assay/library compatibility,
normalization and upstream processing. A later release within the same program is
release transfer, not independent-laboratory confirmation. Version changes in gene
effect processing can create dependencies between datasets despite identity separation.

Freeze candidate source, model family, feature map, tuning grid, all target genes,
training artifacts, seeds, comparator selection, eligibility rules, missingness
handling, support thresholds and reporting plan before outcome access. Do not tune
against the proposed cohort's labels. Preserve the 12-target scope or preregister
any smaller panel before seeing its results. A curator should check available
support without feeding outcome-dependent selections back to the developer.

Report all targets, sample/identity counts, rule-branch support, error and uncertainty,
lineage/assay sensitivity, complexity and every failed/unsupported comparison. Keep
known-biomarker recovery explicitly labeled as a control. The old >=30 threshold is
a minimum support gate, not a guarantee of statistical power; a reviewer must judge
power and multiple-comparison handling for the actual proposed claim. No public
claim of biological improvement follows from a better development score.
