# Featured-pilot assessment

> **Historical (2026-10-20).** This assessment predates the launch: the project has been
> open to donated sessions since 2026-10-21, with a maintainer. Current status is in `CURRENT.md`.

**Recommendation: keep this as a supporting inaugural pilot; defer lead-feature status.**
It has excellent public relevance and modest hardware requirements, and contributors can
produce checkable work quickly. This trial did not establish useful new biology or a
predictive advantage from the agent's biological reasoning. Independent assay transfer
is the main scientific weakness. A narrower, curated challenge could become feature-ready.

## What was actually tested

The prospective self-run trial started at 20:13:24 UTC on 2026-10-20 and reached its primary
final-test result by 20:46:54 UTC: 33.5 minutes. Packaging, visualization and clean-checkout
replay followed. This was performed by the same agent that built the pipeline, interleaved
with setup and debugging. It is **not an independent newcomer study**, and author familiarity
makes onboarding look easier than it may be for an unrelated contributor.

The corrected cohort contains 967 distinct cancer-model identity groups, with 773 for
development and 194 held out. A separate set of 49 Sanger identities is absent from the
whole Avana cohort. The fixed panel covers 12 target genes and 107 available molecular
features drawn from 30 genes. Each target's initial search considers 284 threshold rules.

The contribution was a small, prospective model change: replace the best one-threshold
rule with two-feature ridge regression using published biological relationships. A blind
two-feature model controls for improvements obtainable by simple feature selection.
The stronger comparison is a ridge/elastic-net/self-expression baseline selected using
development data. All baselines use the same restricted 30-gene predictor panel; genome-wide
features and published end-to-end prediction systems were not reproduced. All final models were frozen before the final evaluation, including
those which ultimately failed. No candidate was retuned after final or Sanger scoring.

## Results that matter for the decision

| Comparison on 194 untouched model groups | Error reduction | Paired 95% interval | Interpretation |
|---|---:|---|---|
| Biology-chosen pair versus one-threshold rule | −0.6% | −3.4% to +2.6% | No reliable gain; the primary trial gate failed |
| Data-chosen pair versus one-threshold rule | +3.5% | +0.4% to +6.7% | A small secondary improvement; below the prespecified 5% practical-gain target |
| Biology-chosen pair versus data-chosen pair | −4.2% | −6.1% to −2.2% | The biological prior did worse in this particular test |
| Data-chosen pair versus best development-selected linear baseline | +2.1% | −1.6% to +5.7% | No demonstrated superiority over the stronger baseline |

These are normalized aggregate MSE comparisons, with targets scaled by development
variance and cell identities resampled jointly across targets. Only the first comparison
was the trial's declared primary endpoint; the others are descriptive. They do not prove
that biological knowledge is generally unhelpful, nor that agents cannot discover anything.
They show that this particular plausible contribution did not deliver a robust overall gain.

Four one-feature rules passed the initial pilot's combined internal gates: BRAF hotspot,
KRAS hotspot, ARID1A damaging mutation for ARID1B dependency, and TP53 damaging mutation
for MDM2 dependency. Those are familiar relationships, not four new discoveries. Their
held-out MSE reductions over lineage were approximately 51%, 38%, 23% and 44%, respectively.
Several other apparently strong development associations had wide final uncertainty.

The independent-identity assay check is less encouraging. **No rule combined positive
95% interval with the required minimum support of 15 observations in both branches** in
Sanger. Most biomarker-positive groups are small. BRAF's held-out Avana improvement of
51% became roughly −151% relative to the lineage baseline on Sanger, where only five
models carried the hotspot indicator. This is a real transfer failure for the frozen
predictor, not a refutation of the established biology of BRAF. Cohort composition,
variant classes, assay differences and score calibration are possible explanations;
this trial does not identify the cause.

## Assessment against the launch criteria

| Criterion | Judgment | Evidence and qualification |
|---|---|---|
| Tangible early progress | Good for bounded tasks | A five-fold SMARCA2 starter run completed in 11.79 seconds and passed its verifier. Development skill rose from 15.2% to 25.9%, but the blind pair matched the biological pair. A plausible local gain did not ensure aggregate final improvement. |
| Can initially be hill-climbed | Moderate | Compact models, feature encodings and cohort/validation repairs offer real work. The tested 3.5% secondary gain is modest and does not establish an advantage over strong linear baselines. Endless tuning on the public test would manufacture progress. |
| Public demonstration | Good, with careful framing | “Can a few molecular clues predict which genes cancer cells need?” is understandable. Show the complexity/error tradeoff and the failed transfer, with known biomarkers labeled as controls. A claim of new cancer treatments would outrun the evidence. |
| Meaningful scientific results | Plausible but unproven | Reliable biomarker hypotheses and better evaluations could help research. This run produced a useful benchmark, negative evidence and known-control reproduction; it produced no demonstrated novel biological relationship. |
| High-end home PC | Strong | No GPU. Apple M2, one fitting thread: full baseline 159 CPU seconds, 370 MB peak resident memory; paired-model trial 66 CPU seconds, 249 MB. Wall times were about 10 and 4 minutes under contention. Compact panel data total about 1 MB; raw-source rebuild is about 1.24 GB. No quiet Windows/x86 PC timing was measured. |
| Agent intelligence matters | Credible role, predictive edge unproven | Source interpretation prevented integrated-Sanger leakage, caught non-cancer models hidden under ordinary lineage labels, distinguished missing calls from biological absence, and identified assay-transfer caveats. The literature-informed prediction family lost to the blind control. This is evidence for reasoning-intensive curation and falsification, not proof of superior autonomous biological discovery. |

The main observed bottleneck was scientific validity, not hardware. Three nominal tissue
lineages hid explicitly Non-Cancerous models; fixing that changed the cohort before final
inspection. Other useful engineering work included a 13× isolated threshold-kernel speedup
(with identical thresholds), cached label-independent null designs, and stronger rejection
of altered or selectively omitted results. These are tangible contributions, but should
be credited as tooling and validation rather than biological discoveries.

## What I would feature

A bounded **“small, reliable explanations of cancer dependencies”** challenge is a better
launch proposition than an unrestricted search for targets. Score improvements on a
predeclared development benchmark, display feature counts and uncertainty, and require
separate confirmation before promoting a scientific claim. Make known biomarker recovery
an explicitly labeled onboarding task. Give credit for verified failure explanations,
cohort corrections and independent reproduction as well as better predictions.

A public demo can use [the frozen-model comparison](public-demo.png) alongside
[the transfer check](transfer-check.png). The first chart shows that compact predictors
can beat an average or cancer-type baseline. The second shows why that is insufficient
for a discovery claim. All 12 targets, including failures, remain in [RESULTS.md](RESULTS.md)
and [the all-target plot](all-targets.png). These are comparisons from a single frozen
final evaluation, not a chronological learning curve of adaptive improvements on the test.

## Conditions before making it a lead feature

1. **Appoint a scientific maintainer with review capacity.** No person has agreed yet;
   donor intake is closed. The reference manifest validator deliberately reports the
   missing maintainer, rather than naming a fictitious one or asserting a project stage.
2. **Secure a fresh evaluation process.** The initial public final set is now historical
   evaluation data. Repeated contributors need curator-controlled, newly acquired public
   cohorts with explicit source/identity overlap checks, versioned licensing and limited
   evaluation frequency. Reserve adequate biomarker-positive sample sizes. Randomly
   reshuffling the same now-inspected labels is not new independent evidence.
3. **Run an independent newcomer trial and require stronger confirmation.** Give an
   unrelated contributor the quickstart and one bounded card, without author guidance.
   Require a predeclared compact improvement that survives seeds, lineages and a sufficiently
   supported external cohort. Compare against strong linear baselines and literature priors.

A specific follow-up worth testing computationally is whether allele-class-aware encoding
improves BRAF transfer. Distinct BRAF classes are established prior knowledge
([Yao et al., 2017](https://doi.org/10.1038/nature23291)); the hypothesis that their mixture
explains this pilot's failure is untested. That task must use development data and new
confirmation data, not repair the already inspected Sanger score and call it a fresh win.
This illustrates where reasoning could help beyond more CPU time, while preserving an
honest distinction between a useful follow-up hypothesis and a new biological discovery.

All biological findings and proposed explanations are computational research hypotheses.
This pilot establishes neither cancer-versus-normal selectivity nor validated drug targets.
