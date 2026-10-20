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

## Engineering observation during setup

The first development run was stopped after BRAF, before a final-test evaluation. The
threshold kernel repeated the same X-only quantiles across null permutations. A synthetic
response microbenchmark on the development feature matrix found a 13.08x CPU-time speedup
for vectorized threshold calculation, with thresholds exactly equal. This is a kernel
speedup, not a claimed whole-pipeline speedup. See setup/logs/kernel-benchmark.json.

The revised null implementation caches imputation/threshold design matrices (which never
depend on the permuted labels), then refits all leaf means and reselects all candidates
for each null. Tests compare the resulting statistics against complete uncached selection
at 1e-12 tolerance. No search space, outcome, split, or acceptance gate was changed.
The incomplete first run is preserved as develop-preoptimization.log and is not a result.

Two setup bugs were also corrected before completed evaluation: an index-name mismatch
when joining source metadata, and a status script named inspect.py that shadowed Python's
standard library. The final package uses status.py. A newcomer using the finished compact
package should not face those same issues; this trial therefore overstates repeat-user
setup cost but benefits from author knowledge.

## Eligibility correction before final inspection

A metadata-only audit found that ACH-001310, ACH-001453 and ACH-002462 were annotated
Non-Cancerous in OncotreePrimaryDisease despite ordinary Kidney, Prostate and Eye lineage
labels. The initial lineage-only exclusion missed them. The interrupted second baseline
run is preserved in develop-before-disease-audit.log; its results are discarded.

The cohort construction now explicitly excludes Non-Cancerous or missing primary disease,
as well as the previously excluded lineage categories and engineered models. This repairs
the stated cancer-cell eligibility requirement, not a response-based exclusion. All panels,
identity partitions and evaluations are regenerated. No final-test predictions or scores
had been computed or inspected. Both the correction and earlier protocol remain in git.

## First bounded task completed

The one-target SMARCA2 starter run used development data only and took 11.79 seconds
including interpreter/import startup (3.91 seconds inside the evaluator; 3.61 CPU seconds;
maximum resident set 186,040,320 bytes). Its five-fold mean skill relative to the lineage
baseline rose from 0.1524 for the one-feature rule to 0.2590 for the biological pair.
The blind pair matched 0.2590. Every development model was predicted exactly once and all
15 fold/model scores were verified. See research/starter/RESULT.json and
setup/logs/starter.log. This is checkable early progress, but not final validation and not
evidence that the literature prior outperforms simple automatic feature selection.
