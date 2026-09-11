# Open Science finalization gate

## Current classification

```text
FINALIZATION_PREP
CANON_UNCHANGED
RELEASE_NOT_PROMOTED
LOCAL_REPLICA_PENDING_OBSERVATION
SIDE_EFFECT_REPLAY_FORBIDDEN
```

This classification is intentionally stricter than “works on my branch.”

## What is already closed enough to preserve

The integrated development spine has deterministic tests, benchmark fixtures, proof-lane evidence, closed-loop assurance contracts, incremental receipt rules, paired timing evidence and manifest/receipt hardening. The existing public release metadata remains v0.2.0 until an explicit later release decision.

The finalization pack adds an inspectable explanation of lineage, authority, recovery and capsule integrity without changing runtime behavior or canonical CI.

## Gates required before release promotion

1. **Stack reconciliation** — review the stacked PR chain and decide which layers belong in the next promoted release. Do not merge shadow experiments merely for branch cleanup.
2. **Fresh integrated verification** — run CI/tests/benchmarks on the exact candidate commit after the intended integration graph is resolved.
3. **Scoped manifest decision** — either preserve a release-scoped manifest with explicit partial inventory or intentionally generate a new complete release inventory. The choice must be documented.
4. **Local replica observation** — directly inspect the local repository/system-state replica and verify its selected authority anchor. Until then status is `PENDING_NOT_OBSERVED`.
5. **Restore rehearsal** — reconstruct a clean isolated copy from the chosen public/cloud backup sources and pass the declared verification sequence without replaying external side effects.
6. **Release metadata update** — only after the above gates pass, update version, changelog and citation release metadata together and create an immutable release/tag.
7. **Public/private boundary audit** — confirm that no private identifiers, credentials, personal data or private backup topology entered public artifacts.

## Non-blocking hardening after functional closure

These are useful but do not justify delaying a correctly scoped finalization indefinitely:

- branch-protection/ruleset policy for the eventual canonical release branch;
- archival of obsolete temporary branches after explicit review;
- DOI/archival repository integration if desired for formal open-science citation;
- automated generation of the finalization capsule manifest from immutable file identities;
- optional machine-readable provenance graph export.

## Stop rule

Do not keep adding architectural layers merely because a new name or abstraction is possible. After the gates above are satisfied, prefer defect repair, reproducibility evidence and documentation over ontology expansion.

A final system is not one with the most components. It is one whose authority, evidence, recovery path and failure states are explicit enough that another person can reproduce and audit it.
