# Source attribution and permitted reuse

DepMap, Broad (2024). **DepMap 24Q2 Public**, version 1.
https://doi.org/10.25452/figshare.plus.25880521.v1
Publisher: Figshare+. License: CC BY 4.0.
https://creativecommons.org/licenses/by/4.0/

The publisher's license declaration is preserved in
setup/sources/depmap-24q2-v1.json and data/source-lock.json. This is release-specific;
it says nothing about the rights to any other release, CCLE dataset, or third-party
annotation downloaded separately. No independently fetched restricted annotation database
is used. Hotspot and damaging annotations here are those distributed in this release.

`data/panel/*.csv` are modified extracts: selected genes, binary mutation presence with
missingness preserved, eligible 2D passing screens, same-library median outcomes,
identity de-duplication and fixed sample partitions. `data/gene-map.json` preserves
original gene labels. The processing script is src/prepare.py. Raw publisher files remain
excluded from git and can be re-fetched by pinned URL and verified hashes.

Screen gene effects are inferred from experimentally measured CRISPR depletion screens;
they are processed estimates, not direct probabilities of death. Attribution does not
imply endorsement by the Broad Institute, Sanger Institute, or original investigators.

Setup instructions and schemas fetched from Discovery@Home are preserved solely as
provenance and retain their original authorship/terms; they are not pilot-authored prose.
