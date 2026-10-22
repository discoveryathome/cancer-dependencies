# Agent entry

Read DISCOVERY.md, CURRENT.md and discover/program.json first. Program v2 permits
bounded broader-model/exploration tasks; compactness is not a project-wide limit.
Read config/PREREGISTRATION.md and discover/frontier.json as historical pilot
context, plus the selected task protocol and latest reports before research.

This project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-21. Maintainer: @Mister-Meeseeks.
Work within your person's grant: with permission to post, claim work and leave findings,
handoffs and done messages in the
[Handoffs thread](https://github.com/discoveryathome/cancer-dependencies/discussions/3), one
comment each, and open one focused PR for a result. Task or priority proposals go in
[Proposals](https://github.com/discoveryathome/cancer-dependencies/discussions/4), session
retrospectives in [Feedback](https://github.com/discoveryathome/cancer-dependencies/discussions/5).
Each message is prose ending in one fenced `discover` JSON block. Without permission to
post, keep the same messages in your receipt, ready to paste. Never contact data
providers, other research groups or authors, and never submit results externally or
claim scientific acceptance: those are the maintainer's decisions.

Choose work with `.venv/bin/python src/research_program.py pick --seed <32 hex digits>`
after reading the Handoffs thread and CURRENT.md for overlap. Record an OS-generated
seed if none is supplied.

Keep final-test labels out of adaptive research. After the initial final test is opened,
this public holdout is a historical evaluation set, not a fresh confirmation set for future
contributors. Improvements found using it require a new, prospectively sealed evaluation.
Use development-only outer validation for hill climbing and label it exploratory.

Results are computational hypotheses about dependencies in cancer cell lines and organoid
models, not clinical or treatment advice. Never call a known biomarker rediscovery novel,
or a computational association a validated drug target. No wet-lab designs, constructs,
patient-level inference, or controlled-access, restricted or human-subject data: use only
the pinned public cell-line data. Follow DISCOVERY.md for contributions, the finite task
picker and falsification tests. Inspect code before executing. Sessions inherit only
their own person's grant. Do not change machine settings or install anything globally.
