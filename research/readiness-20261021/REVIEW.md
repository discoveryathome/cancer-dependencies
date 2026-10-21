# Review package: Cancer-cell dependencies

Prepared locally; not sent. Base commit: `703781fa998c421d063f76ae1c997a4de827fd1e`.
Review the final preparation commit and artifact manifest, then run the commands
in README.md and the negative controls in the project tests.

1. Review nested baseline selection, the compact-model contract, complete-fold enforcement and the limitations of source/refit validation.
2. Audit identity union across ModelID, PatientID, RRID, stripped names, SangerModelID and COSMICID; inspect unknown/changed identifiers.
3. The 24Q4 metadata reserve is too small. Identify an adequately supported fresh cohort and review upstream processing, assay comparability and feature availability before outcomes are opened.
4. Choose scientifically useful replication/falsification tasks and appoint a maintainer with review capacity. No clinical or novel-mechanistic claim is established.

Return the reviewed commit, artifact hashes, commands, findings, conflicts/prior
involvement, proposed fixes, decision (revise / approve scoped trial / defer), and
review capacity. Fill review.json only after actual review.
