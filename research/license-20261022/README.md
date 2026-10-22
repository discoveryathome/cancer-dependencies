# Source-license notice update — 2026-10-22 UTC

Base: `730abd211ea8438c42efb6404cb2a465464efd60` (GitHub main).
Scope: document source-specific reuse conditions and preserve historical evidence.
Repository visibility, intake and the separate launch branch are outside this change.

## Findings and correction

The two prediction artifacts identified in the updated root DATA_LICENSE.md embed
77-model, 30-gene NextGen expression extracts. Ignoring full downloads did not
exclude these extracts from Git. The portal terms require a full terms repost and
downstream adherence when rehosting data. The prior license inventory covered
24Q2/24Q4 but did not supply this notice for the later portal source.

The root license inventory now identifies the sources, transformations and
affected data/model artifacts. The full April 2, 2026 DepMap terms are reproduced
in `licenses/DEPMAP_TERMS_2026-04-02.md`; README, QUICKSTART and LICENSE link or
refer to the requirements. MIT software rights remain separate from data/model
rights. The notices explicitly require users and onward recipients to comply.
No claim of unrestricted commercial data/model licensing is made.

Publisher source: https://depmap.org/portal/terms/ . Inspected directly in the
existing Chrome tab on 2026-10-22 UTC. The complete terms body, including every
heading and the final trademark notice, was compared against the Markdown copy
after removing Markdown syntax and normalizing whitespace: 5,787 characters,
FNV-1a-32 `55ed8e72` on both sides. This is a transcription comparison, not a
publisher digital signature. Navigation/footer are not part of the copied body.

The source-specific Figshare license records and acquisition manifests remain
unchanged. This update does not establish new permissions, alter publisher terms,
resolve independent third-party rights or provide scientific acceptance.

## Historical evidence

`snapshots.json` records five exact document/checker versions from the base commit.
All five snapshots were compared byte-for-byte with their original Git blobs.
`src/license_history.py` resolves only those exact path/hash pairs; unknown
versions and scientific paths continue to resolve to current files. Changed
snapshots fail verification. Historical evidence manifests are not regenerated.
The program manifest checker resolves its own original source snapshot so its
original manifest remains verifiable after this explicit documentation migration.

No data rows, models, predictions, scientific source, numerical protocols,
results, or original evidence manifests changed. Old operational statements in
dated evidence packages remain historical; they are not current licensing grants.

## Validation

- Six historical packages: all 225 recorded file hashes passed.
- Program-v2 package: all 26 recorded file hashes passed.
- Wide-expression package: all 34 recorded file hashes passed.
- Full test suite: 53 passed, including snapshot-tampering and unrecognized-path
  rejection checks.
- Seven task cards and both program tracks passed declaration validation.
- Relative links in the four current notice/entry documents resolve.
- `git diff --check` passed; existing-file changes are limited to the declared
  license/entry documents and two historical-document checkers.

These checks verify documentation integration and evidence preservation. They are
author-performed checks, not independent legal or scientific review.
