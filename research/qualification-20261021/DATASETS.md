# Dataset feasibility and source provenance

## Sources and access

| Resource | Pinned evidence | Reuse/access finding | Remaining gap |
| --- | --- | --- | --- |
| Broad NextGen metadata | Figshare article 29472362 v1; model and screen metadata, plus Nature Supplementary Table 1 aliases | Figshare metadata record states CC BY 4.0; publisher supplement is linked from the open-access article | Complete donor crosswalk; required input matrices and their exact terms/checksums |
| Sanger organoid metadata | Nature supplementary ZIP, Table 2 `data_availability`; Figshare article 28339340 v1 inventory | Figshare record states CC BY 4.0; article/supplement licensing states CC BY 4.0 subject to marked exceptions | Gene-level availability, branch support, processing contract and independent identity review |
| DepMap 24Q2 and 24Q4 | Existing locked model metadata | Already audited source-specific terms | Missing aliases or related identities can survive recorded matches |

The pinned publisher metadata are in `sources/`; byte hashes, URLs and ZIP ranges
are in `source-lock.json`. Attribution belongs to Neiswender, Maffa, Brenan and
colleagues (Broad) and Herranz-Ors and colleagues (Sanger). Extracted JSON and the
identity graph are our derived metadata products. Code licensing does not confer
data rights; these records do not establish the terms of future portal releases.

Sources: [Broad data v1](https://doi.org/10.6084/m9.figshare.29472362.v1),
[Sanger data v1](https://doi.org/10.6084/m9.figshare.28339340.v1),
[Broad article](https://doi.org/10.1038/s41586-026-10843-7),
[Sanger article](https://doi.org/10.1038/s41586-026-10830-y).

The Broad manuscript directs input-matrix users to the portal's “NextGen Model
Manuscript 2026” files. Our unauthenticated request returned a verification page.
We did not retrieve those input matrices or infer that the Figshare analytical
outputs are substitutes. The portal team also states that NextGen screens are now
in the harmonized 26Q3 release and that the temporary Data Explorer dataset was
removed. This is a **version/processing distinction**, not evidence that the
manuscript download files disappeared. A curator must select and pin the intended
resource. [Portal team explanation, October 14](https://forum.depmap.org/t/organoid-dependency-data/4671/7).

Controlled raw human sequencing routes mentioned by the articles are outside this
project. No restricted data or patient-level inference is needed for the proposed
public model-data audit.

## Identity method and count reconciliation

`src/qualification.py` builds one transitive graph across all 1,959 old-release
models, 2,105 24Q4 metadata rows, 1,999 Broad manuscript model rows and 256 Sanger
organoid rows. The 24Q4 rows enrich identity links but are not themselves an
exclusion cohort: this project has not inspected their dependency outcomes.

Exact namespaced IDs include ModelID, PatientID, RRID, SangerModelID and normalized
COSMIC IDs where supplied. Names/aliases are matched after removing punctuation
and uppercasing. Missing placeholders never generate a key. Sanger individual IDs
group related organoids within their own namespace. Matching is transitive across
all records, so an unscreened related model can still reveal exclusion evidence.
Every union edge and its source-node indices are preserved in `cohort-audit.json`.

Broad has 147 passing NextGen screens/models in the metadata. Sixteen screened
models connect to the old-release identity graph. One additional model lacks an
expression-availability flag, and one is annotated non-cancerous, leaving 129 models/components. The initial ModelID
check alone yielded 131 IDs absent from the old release. The final 129 is an
availability-and-identity count, not a newly verified donor count. Broad provides
no complete new-model PatientID mapping in these manuscript tables.

Sanger's 162 screened models represent 157 recorded identity components. Thirteen
screened rows directly say Broad overlap. Excluding whole related components
removes 14 screened models, leaving 148 models/144 components. The reserve has
listed RNA availability for all models. Use one deterministic eligible
representative per component, or a preregistered within-component aggregation;
never count related organoids as independent observations.

Names can collide, aliases can be missing, and equal HCMI prefixes alone are not
proof of a shared donor. We do not invent prefix-based donor grouping. The next
review must reconcile Broad donors, publisher overlap flags, Sanger identities,
engineered status and any newer model registry against the complete old cohort.

## Measurement compatibility

The existing benchmark uses Avana/2DS with its pinned gene-effect processing.
Broad NextGen passing screens use Humagne-CD and four screen types. Its paper
describes Chronos pretraining on traditional and NextGen CNS models before
application to organoids. This shared upstream fitting matters even when model
identities are disjoint. Sanger uses Yusa/MinLib-derived processed fitness effects
with its own correction and normalization. Raw MSE values across those scales
cannot simply be put on one leaderboard.

The Broad Figshare inventory includes analytical outputs; it is not the full input
dataset. Sanger's inventory includes expression and molecular-feature files, and
its supplementary archive lists gene-level response tables. Listing a file is not
verification of required gene coverage, feature semantics or values. None of those
new matrices was opened or scored in this round.

Approve a contract for gene IDs, expression units, copy-number definition, mutation
classes, missingness, assay score orientation, QC and preprocessing provenance
before joining data. Report distinct questions separately: absolute score
calibration, ranking models for one gene, and ranking genes within one model.

## Prior work and exposure

Fırat and Kılıçaslan's October 2026 study explicitly evaluates expression-based
2D-to-organoid prediction on Broad and Sanger resources. Its reported Sanger cohort
is also 148 models/144 donors. This agreement is a useful reconciliation clue,
not independent validation of our mappings or their methods. We read the indexed
publisher abstract and PubMed record; direct publisher full-text requests failed.
Full methodological reproduction and comparison to our restricted panel remain
open. [Publisher](https://doi.org/10.3390/biology15191782),
[PubMed](https://pubmed.ncbi.nlm.nih.gov/42883455/).

All new primary row-level outcomes remain uninspected here, but literature summaries
and assay methods have been read. A future evaluation can be frozen prospectively
relative to our candidate, while still being a public-data replication informed by
prior literature. It cannot honestly be described as wholly unseen evidence.
