# OPUS Assurance Kernel

The strongest mathematical coupling between a planner/orchestrator and OPUS is not `planner + evaluator`. It is **constrained projection**.

Let `x_t` be the current typed state and let a generator/orchestrator propose a candidate `u_t`:

```text
u_t = Generator(x_t)
```

OPUS defines the admissible set `A(x_t)` from evidence, semantic, authority, proof-obligation, rollback/readback, and execution contracts.

The execution candidate is therefore conceptually:

```text
a_t = Pi_A(x_t)(u_t)
```

where `Pi_A` is a typed projection onto the admissible set.

## Verdict geometry

- **PASS / IDENTITY** — the candidate is already admissible; projection is the identity.
- **REPAIR / REPAIR_CANDIDATE** — a bounded repair may make the candidate admissible, but OPUS does not fabricate the missing evidence, rollback, readback, or semantics and does not auto-apply the repair.
- **UNKNOWN / UNRESOLVED** — the admissible set cannot be resolved from the available evidence/contracts.
- **BLOCK / HARD_BLOCK** — reaching an admissible candidate would cross a hard boundary, such as authority escalation or a forbidden semantic-authority inversion.

## Typed edit distance

The practical metric is ordinal and typed rather than a fabricated floating-point score:

```text
T0_NONE
T1_LOCAL_STRUCTURAL
T2_CONTRACT_COMPLETION
T3_SEMANTIC_CHANGE
T4_AUTHORITY_CHANGE_FORBIDDEN
```

Conceptually:

```text
Pi_A(u) = argmin d_typed(u, v)  for v in A(x)
```

but `d_typed` is effectively infinite across hard authority/evidence boundaries. OPUS therefore cannot make an action admissible by silently expanding authority, inventing provenance, promoting MODEL to FACT, or interpreting a metaphor as a specialist solver.

## Why this simplifies the larger architecture

The larger command-center vocabulary can be reduced to a few mathematical objects:

1. **Typed state** — the current evidence/model/action state and stable semantic identities.
2. **Mission projection** — the smallest dependency closure relevant to the current task.
3. **Candidate** — a proposed transform/action from any generator.
4. **Admissible set** — hard contracts and proof obligations enforced by OPUS.
5. **Projection receipt** — PASS/REPAIR/UNKNOWN/BLOCK plus checks, typed repair hints, and fingerprints.
6. **Observed delta** — post-execution readback used for incremental re-evaluation and benchmark evidence.

The 3x8 TRI-VECTOR remains an address/view schema over the same state. It is not a set of independent agents or votes. The Spectral Centralizer is a type firewall, not a solver selector. NANO K0..K6 becomes the orchestration lifecycle around these objects.

## OPUS x orchestrator boundary

```text
Generator / ULTRATRON-like planner
             |
             v
        candidate u_t
             |
             v
   OPUS Assurance Kernel
   admissibility + projection receipt
             |
     +-------+--------+----------------+
     |                |                |
   PASS             REPAIR        UNKNOWN/BLOCK
     |                |                |
     v                v                v
 bounded exec     external fix       NOOP/fallback
     |
     v
 observed readback
     |
     v
 OPUS post-condition check
     |
     +--> keep / rollback / request evidence
```

OPUS remains generator-independent. A human, script, CI bot, local model, hosted model, or a larger orchestrator can all produce candidates against the same assurance boundary.

## Current implementation

`assurance_kernel.py` implements the pre-execution, non-mutating part of this design:

- `AssuranceReceipt`
- `ProjectionStatus`
- typed `ProjectionHint`
- hard authority boundaries
- unknown-spectrum fail-closed behavior
- packet fingerprinting

`command_center.py` now uses this kernel at the conceptual `K3 -> K4` boundary.

## Next measurable step

Do not promote this architecture because the equations are elegant. Benchmark it against the simpler evaluator on real pull-request workflows. Measure:

- false-PASS / omitted-contract detection,
- verifier/proof-obligation coverage,
- repair radius,
- unnecessary capability activations,
- re-evaluation scope after a delta,
- readback/rollback completeness,
- latency and tool calls.

Persistent promotion requires positive net value on real workflows.
