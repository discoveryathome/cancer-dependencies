# Source attribution and permitted reuse

## License boundaries and requirements for users

Project-authored source code is MIT; new project prose is additionally CC BY 4.0.
Third-party data, source documents and rights in trained models are not relicensed
by those grants. This inventory applies to the repository's current files and
the corresponding artifacts in its Git history. Historical handoffs describe
the permissions reviewed at that time; this notice supplies the current
source-specific reuse guidance.

**Anyone using or redistributing the NextGen portal data or affected artifacts
listed below must comply with the [full DepMap terms](licenses/DEPMAP_TERMS_2026-04-02.md).**
We require downstream users to follow those terms, including their use limits,
attribution, confidentiality, and continuity requirements. If you rehost affected
data, you must reproduce the terms in full and require your own recipients to
adhere to them. If you cannot comply, do not use or redistribute those materials.
These obligations do not restrict independent reuse of the MIT source code.

## DepMap 24Q2 Public

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

## Preparation metadata from a later release

DepMap, Broad (2024). **DepMap 24Q4 Public**, version 1.
https://doi.org/10.25452/figshare.plus.27993248.v1 — CC BY 4.0, as declared in
`research/readiness-20261021/sources/depmap-24q4-v1.json`.

Only Model.csv, CRISPRScreenMap.csv, AchillesScreenQCReport.csv and
OmicsDefaultModelProfiles.csv were fetched for a metadata-only eligibility audit.
They are unchanged publisher files. `cohort-reserve.json` is our derived identity
and availability analysis. Source checksums and retrieval URLs are retained; no new
gene-effect or molecular-feature matrices were downloaded. This permission record
applies to this pinned release and does not establish terms for newer releases.

The preceding section records the metadata-only preparation step. The later
NextGen matrix acquisitions described below are a separate source and permission
record; the earlier statement about matrices does not describe the whole project.

## Broad and Sanger qualification metadata

The following source records declare CC BY 4.0 for their pinned Figshare deposits:

- Neiswender, Maffa, Brenan and colleagues, Broad NextGen analytical deposit,
  [article 29472362 v1](https://doi.org/10.6084/m9.figshare.29472362.v1).
  License declaration: `research/qualification-20261021/sources/broad-figshare.json`.
  Bundled `broad-model_metadata.csv` and `broad-screen_metadata.csv` retain source
  metadata; `broad-aliases.json` is an extracted alias mapping from the associated
  article supplement.
- Herranz-Ors and colleagues, Sanger organoid deposit,
  [article 28339340 v1](https://doi.org/10.6084/m9.figshare.28339340.v1).
  License declaration: `research/qualification-20261021/sources/sanger-figshare.json`.
  `sanger-availability.json` extracts availability and identity metadata from the
  associated article supplement; it is not a redistributed Sanger outcome matrix.

The associated open-access article supplements are identified in
`research/qualification-20261021/source-lock.json` and `DATASETS.md` in that
directory: [Broad article](https://doi.org/10.1038/s41586-026-10843-7) and
[Sanger article](https://doi.org/10.1038/s41586-026-10830-y). The Sanger article/supplement is recorded under CC BY 4.0, subject to separately
marked third-party exceptions. The Broad article instead carries
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), as confirmed
on its publisher rights-and-permissions page on 2026-10-22. That article license
does not authorize sharing adaptations. `broad-aliases.json` records factual
identity/availability fields extracted from its Supplementary Table 1; the source
workbook is not redistributed. This project does not claim a CC BY grant for
that extract or resolve any copyright/database rights in it. Further reuse must
respect applicable rights; the metadata deposit's different license must not be
used to infer permission. Derived identity and availability audits preserve source
attribution and transformations without implying endorsement or verified identity.
Permission for these deposits does not establish permission for portal matrices.

## NextGen Model Manuscript 2026 portal inputs and artifacts

Source: Neiswender, Maffa, Brenan et al., *A dependency map enhanced with
next-generation 3D cancer models*, Nature (2026),
[doi:10.1038/s41586-026-10843-7](https://doi.org/10.1038/s41586-026-10843-7).
We acknowledge the Broad Institute DepMap and the original investigators for
the data used in these analyses, without implying endorsement.

The exact release is [NextGen Model Manuscript 2026](https://depmap.org/portal/data_page/?releasename=NextGen+Model+Manuscript+2026&tab=allData).
The applicable portal [terms](https://depmap.org/portal/terms/) state
“Last Revised: April 2nd, 2026”; a full reproduction, inspected in the publisher's
browser page on 2026-10-22 UTC, is in
[`licenses/DEPMAP_TERMS_2026-04-02.md`](licenses/DEPMAP_TERMS_2026-04-02.md).
No CC BY permission for these portal inputs is inferred from the separate
Figshare metadata deposit.

| Input or artifact | Contents and treatment |
| --- | --- |
| `data/raw/transfer-trial-20261021/next_gen_expression.csv`, `screen_gene_effect.csv`, `traditional_expression.csv` and release README | Publisher inputs remain ignored and absent from Git history. Acquire directly from the publisher; verify the hashes in the transfer-results and robustness source manifests and wide-expression manifest. |
| `research/transfer-trial-20261021/run/predictions.json` | Includes a 77-model, 30-gene expression extract, identifiers and predictions. This is rehosted portal data despite its filename; the full DepMap terms apply. |
| `research/robustness-20261021/predictions.json` | Includes the same source expression rows, model identifiers, offsets and derived predictions. The data and derived research artifacts retain the source-use obligations. |
| `research/transfer-trial-20261021/run/frozen.json` and `superseded/frozen-initial.json` | Frozen model/protocol artifacts; provenance distinguishes the older CC BY training panel from later portal evaluation inputs. These do not grant a new license to portal data. |
| `research/wide-expression-20261021/models.json` and `predictions.json` | Trained research models, feature-selection/provenance records and predictions; the prediction rows contain identifiers rather than the full expression matrix. They are supplied for nonprofit research under applicable source terms, not as unrestricted MIT model weights. |
| Transfer-results, contributor-support, robustness and wide-expression reports, diagnostics, figures, metrics and logs | Project-generated analyses using the identified sources. Original prose/code licensing does not override source rights in included data, models or derived content. Preserve source attribution and the applicable terms when sharing those components. |

The portal terms permit use of ML/AI models with the data for internal use or
sharing for nonprofit research. They do not authorize commercial use of the data
and identify clinical use as outside the intended purpose. They also require
attribution, protection of subject confidentiality, and continuity of terms when
rehosting data. The full publisher wording governs; this summary does not expand
those permissions or resolve independent third-party rights. Do not use these
research artifacts as clinical recommendations or represent them as unrestricted
commercial datasets/models. Commercial use may require a separate license from
Broad or its contributors.

Reproduction workflow: read the terms before using the bundled extracts; obtain
missing full matrices directly from the publisher, review the source terms there,
and verify exact file hashes before running the frozen analysis. Keep downloaded
matrices in ignored `data/raw/`. Share code independently under MIT; accompany
affected data/model packages with this inventory, the full terms, source citations
and transformation/provenance records. Require recipients to comply with the
same terms and pass those requirements on when rehosting data.

## Evidence preservation

This notice updates licensing documentation, not scientific evidence or publisher
permissions. The previous notice and affected entry/checker documents are preserved
byte-for-byte under `research/license-20261022/historical/`; historical manifests
remain unchanged and are checked against their exact original document versions.
No expression rows, models, predictions, protocols or scientific results were
changed as part of this licensing update.
