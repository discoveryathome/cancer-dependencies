# Contributor feasibility trial

Requested by the project initiator: a 30–60 minute test to assess early progress,
public demonstration, meaningful science, home-PC feasibility and the role of agent
intelligence. Trial start: 2026-10-20 20:13:24 UTC. Target: 30–45 minutes of active
work, bounded at 60 minutes. This is a self-run simulation by the setup author, not an
independent contributor or human newcomer study. Initial infrastructure is still being
completed; record setup friction separately rather than hiding it.

Final-test outcomes were unopened at trial start. Candidate development may inspect
only the development split. Freeze the candidate before final evaluation. The baseline
is the predeclared finite one-feature rule search and established linear baselines.

Machine contention is present: other processes are running on this shared host. Wall
clock benchmarks are indicative, not calibrated performance predictions for a home PC.

## Prospective candidate (fixed before inspecting benchmark performance)

Fit a two-feature ridge regression using target-specific literature-motivated pairs in
protocol.json. This tests continuous dosage plus mutation state, or a paralog's expression
plus damaging calls, rather than treating a single coarse threshold as sufficient.
For TP53/MDM2, combine the two mutation classes rather than conflating a missing call with
wild type. These are deliberately familiar biological priors, not newly discovered biology.
The linear form is an approximation; interactions, variant alleles and biallelic state are
not modeled. The original gene-level binary encodings remain unchanged.

Compare with a blind two-feature ridge model: within each training fold, rank molecular
features by absolute Pearson association to the target after training-only imputation;
select the first two, then tune ridge alpha in inner folds. Feature selection is rerun
inside those inner folds. Both models use the same alpha grid and data splits. This is a
control for compactness, not a perfect equal-compute or equal-information experiment.

Primary trial outcome: final normalized MSE skill of biology_pair against the frozen
rule_all baseline. Weight targets by inverse development variance, average losses per
cell line over available targets, and bootstrap independent cell-line identities jointly
across targets. Success requires >=5% improvement, paired 95% CI above zero, and >=80%
positive development outer-fold comparisons. Secondary comparisons to blind_pair and
the best baseline linear family (selected using development outer MSE) are descriptive.
No cherry-picking a successful target after final inspection. Report every target.

Sources for choosing pairs, not proof that the precise model will work:
- Oncogene and expression biomarkers: https://doi.org/10.1038/s43018-024-00789-y
- SMARCA4/SMARCA2: https://pmc.ncbi.nlm.nih.gov/articles/PMC3958034/
- Reciprocal direction: https://pmc.ncbi.nlm.nih.gov/articles/PMC6691015/
- ARID1A/ARID1B: https://doi.org/10.1038/nm.3480
- STAG2/STAG1: https://pmc.ncbi.nlm.nih.gov/articles/PMC5514935/
- MTAP/PRMT5: https://pubmed.ncbi.nlm.nih.gov/26912360/
- TP53-related dependencies and assay artifacts: https://doi.org/10.1038/s41467-022-32285-1

MTAP/PRMT5 is an intentional assay-transfer challenge: evidence from partial inhibition
or RNA interference need not carry over to complete CRISPR knockout. TP53-associated
CRISPR-cut toxicity is an additional alternative explanation, not a molecular mechanism
to assume away. A scientifically helpful agent should notice these distinctions.
