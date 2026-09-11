# Reproducibility and restore contract

This procedure restores **state and evidence**. It must not silently re-execute external side effects.

## 1. Select an authority anchor

Use an explicit branch/tag/commit and record it before materialization. For this finalization capsule the integrated base is:

```text
audit/receipt-hardening-v0.5
876b779acef59343485a491bd77630eff302077c
```

Do not restore from “latest” without resolving it to an immutable identity.

## 2. Acquire independently addressable copies

Recommended roles:

- public Git repository: code, tests, public documentation and public evidence;
- cloud system-state store: private policy/checkpoint/capsule records;
- local replica: offline recovery copy after observed synchronization;
- optional exported archive: transport-only backup, never self-promoting authority.

A successful copy operation is not sufficient. Record source identity, destination role, observation time and integrity result.

## 3. Validate the scoped release inventory

From the repository root run the manifest validator on the scoped `MANIFEST.json` inventory. The expected finalization behavior is that declared release files validate while later development/shadow files may remain explicit `PARTIAL_INVENTORY` rather than being silently assimilated.

Do not rewrite the release manifest merely to make an audit green.

## 4. Rebuild in a clean environment

Use a supported Python version and a fresh environment. The canonical install path remains the normal isolated build path unless a specific experiment explicitly states otherwise.

Minimum verification sequence:

```bash
python -m compileall -q scripts src tests
python -m pip install -e .
python -m unittest discover -s tests -v
opus-eval doctor
opus-eval validate examples/mission.json
opus-eval benchmark benchmarks/suite.json --json-out artifacts/benchmark.json --junit-out artifacts/benchmark.xml
```

Run additional dogfood/shadow workflows only when reproducing the corresponding experiment. Their success does not alter release authority.

## 5. Check proof and readback obligations

A recovery candidate is not accepted solely because files exist. Verify, as applicable:

- provenance/source identity;
- manifest or capsule integrity;
- unit tests and deterministic benchmark obligations;
- packaging/installed-surface checks;
- authority/side-effect constraints;
- post-condition/readback evidence;
- rollback target or repair path;
- expected benchmark receipt schema.

Missing evidence resolves to `UNKNOWN` or a blocked promotion gate, not an invented PASS.

## 6. Materialize local replica

The local replica may be declared current only after it is directly observed and checked against the selected authority anchor. If the local device is unavailable, record `PENDING_NOT_OBSERVED`; do not infer synchronization from cloud state.

Suggested local layout:

```text
CORE_WORKFLOW/
  SOURCE/
    opus-eval-fabric/
  SYSTEM_STATE/
    manifests/
    checkpoints/
    evidence/
    graphs/
  BACKUP/
    capsules/
  RESTORE_TEST/
    isolated/
```

The exact local path is operational configuration, not public authority.

## 7. Perform a restore test, not only a backup test

A backup is unproven until a bounded restore test can reconstruct the expected state and pass its verification obligations. Restore tests should use an isolated target and must not overwrite a healthy canonical copy.

## 8. Promotion is explicit

Only an explicit release/promotion action may advance canonical authority. Synchronization, a new ZIP, a newer timestamp, a successful benchmark, a shadow workflow or a local replica does not implicitly promote the system.

## Fail-closed rules

```text
MISSING_PROVENANCE        -> UNKNOWN / BLOCK_PROMOTION
HASH_OR_ID_MISMATCH       -> BLOCK_RESTORE_ACCEPTANCE
MISSING_READBACK          -> UNKNOWN
SIDE_EFFECT_REPLAY_RISK   -> BLOCK_AUTOMATIC_REPLAY
LOCAL_REPLICA_UNOBSERVED  -> PENDING_NOT_OBSERVED
SHADOW_ONLY_EVIDENCE      -> NO_CANONICAL_PROMOTION
```
