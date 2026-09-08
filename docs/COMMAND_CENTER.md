# Command Center substrate (v0.3 design/implementation slice)

This layer compiles the larger experimental desktop/orchestration idea into a small, auditable OSS control plane.

```text
MISSION
  |
  v
Mission Compiler
  |
  v
Spectral Centralizer -- explicit type firewall
  |
  +--> MissionWindow / dependency closure
  +--> SemanticIndex / stable identity
  |
  v
NANO stages K0..K6
  |
  v
Evidence / Model / Action -- TRI-VECTOR 3x8 address view
  |
  v
Capability Router -- LOCAL / CLOUD / WEB metadata only
  |
  v
Anti-Malfunction structural audit
  |
  v
Verify / readback semantics
  |
  v
Merkle-style integrity snapshot
  |
  v
Benchmark ledger interface
  |
  v
STOP / REPAIR / BLOCK / UNKNOWN
```

## Implemented in this slice

- `mission_compiler.py` — explicit `ProblemSignature`; no solver selection from metaphors.
- `spectral.py` — typed spectrum firewall. Unknown labels remain rejected/UNKNOWN.
- `mission_window.py` — deterministic transitive dependency closure.
- `semantic_index.py` — stable `Namespace/ConceptID/SenseID`; labels are aliases, not identity.
- `trivector.py` — 3 axes x 8 ports = 24 addressable contacts as a schema only.
- `router.py` — deterministic-first selection over declared LOCAL/CLOUD/WEB candidates.
- `anti_malfunction.py` — structural contradiction checks on evaluation output.
- `snapshot.py` — deterministic Merkle-style state fingerprint. Integrity identity is not truth.
- `ledger.py` — side-effect-free benchmark ledger representation.
- `command_center.py` — bounded orchestrator emitting a machine-readable receipt and stop state.

## NANO stages

1. `K0_LOAD_RESUME`
2. `K1_INTENT_CONSTRAINTS`
3. `K2_EVIDENCE_STATE`
4. `K3_ROUTE`
5. `K4_EXECUTE_BOUNDED`
6. `K5_VERIFY_READBACK`
7. `K6_LEARN_PRUNE_STOP`

`K4` does not grant authority. Current execution remains bounded by the existing `ActionPacket` and evaluator guards.

## Spectrum firewall

The word *spectrum* is overloaded. OPUS keeps semantic, evidence, temporal, literal signal, literal physical, graph, probabilistic, geometric, control, resource, risk/authority and mission-domain classes separate. A display metaphor never automatically selects a Fourier transform, graph eigensolver, quantum simulator, or physical model.

## CLI

```bash
opus-eval plan examples/mission.json
opus-eval command-center examples/mission.json
```

## Non-goals

This slice does not install/execute arbitrary tools, self-modify a model, grant permissions, auto-merge pull requests, infer physics from metaphorical names, treat 24 contacts as independent evidence votes, or claim that a hash/graph metric/benchmark pass establishes truth.

## Next benchmark

Compare this command-center path with the simpler v0.2 evaluator on real pull requests: omitted requirements, verifier coverage, false-PASS rate, time/tool calls, unnecessary capability activations, and reproducibility/readback completeness. Only measured net value should justify default promotion.
