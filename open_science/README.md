# OPUS Eval Fabric — Open Science Finalization Pack

This directory is a **finalization and reproducibility capsule**, not a release promotion and not a replacement for the scoped `MANIFEST.json` release inventory.

## Authority boundary

The integrated engineering base for this pack is:

- branch: `audit/receipt-hardening-v0.5`
- commit: `876b779acef59343485a491bd77630eff302077c`
- finalization branch: `finalize/open-science-pack-v0.6`

The finalization branch adds documentation, topology, restore contracts and machine-readable capsule metadata only. It does not modify the canonical CI path, runtime package behavior, permissions, release version, or citation release date.

## State classes

The project keeps these roles distinct:

```text
CANONICAL_STABLE      authoritative promoted state
LIVE_VOLATILE         current working/integration state
DERIVED_EPHEMERAL     rebuildable evidence, reports and transient products
BACKUP_COPY           integrity-preserving recovery copy
REPLICA               synchronized copy whose authority is inherited, not self-created
```

A location, hash, successful test, replica, backup or repeated result does not by itself create authority.

## Finalization invariants

1. **Evidence before claim.** A scientific or engineering claim must point to an observed source, fixture, receipt or reproducible procedure.
2. **Authority before side effect.** A successful-looking action does not retroactively authorize itself.
3. **Identity is not truth.** Hashes and Merkle-style roots prove encoded-state identity, not factual correctness.
4. **Replay is not re-execution.** Restore/replay procedures must not silently repeat external side effects.
5. **Shadow evidence stays shadow.** Experimental workflows are not promoted merely because they pass.
6. **Local/cloud convergence is checked, not presumed.** A replica is marked current only after observation and integrity verification.
7. **Release metadata remains frozen until a release gate passes.** `CITATION.cff`, version declarations and canonical release inventory are not advanced by this documentation pack.

## Capsules

- `CAPSULE_INDEX.json` — machine-readable state/lineage registry.
- `TOPOLOGY.md` — development lineage and authority graph.
- `REPRODUCIBILITY_AND_RESTORE.md` — deterministic recovery and verification sequence.
- `FINALIZATION_GATE.md` — explicit closure gates, blockers and non-claims.
- `FINALIZATION_MANIFEST.json` — integrity index for this finalization capsule itself.

## Scope

This pack is designed to make the project easier to inspect, reproduce, restore, audit and eventually release without collapsing experimental evidence into canonical claims. It deliberately preserves the distinction between the stable public foundation, the stacked development line, shadow experiments and private recovery replicas.
