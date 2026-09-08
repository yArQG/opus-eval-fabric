# Mathematical core: admissible projection

The project can be reduced to one compact control law.

Let:

- `x_t` be the typed current state,
- `G(x_t)` be any generator/planner/orchestrator proposal,
- `A(x_t)` be the OPUS admissible set defined by evidence, semantics, authority, proof obligations, rollback/readback, and execution constraints,
- `Pi_A` be the typed projection operator,
- `F` be the external execution/environment transition,
- `R` be readback/post-condition observation.

Then:

```text
u_t       = G(x_t)
a_t       = Pi_A(x_t)(u_t)
x_(t+1)   = F(x_t, a_t)
y_(t+1)   = R(x_(t+1))
```

with the hard release invariant:

```text
EXECUTE(a_t) implies OPUS_PRE(a_t, x_t) == PASS
```

and persistent promotion requiring post-condition evidence:

```text
PROMOTE(a_t) implies OPUS_POST(a_t, y_(t+1)) == PASS
                    and measured_benchmark(a_t) >= baseline
```

## Verdicts as geometry

```text
PASS    : u_t is already in A(x_t)       -> identity projection
REPAIR  : bounded admissible repair exists -> repair candidate
UNKNOWN : A(x_t) cannot be resolved      -> no execution promotion
BLOCK   : admissibility would cross a hard boundary -> fail closed
```

## Typed distance

Minimal repair is not based on an invented scalar score. It uses ordered edit classes:

```text
T0_NONE
T1_LOCAL_STRUCTURAL
T2_CONTRACT_COMPLETION
T3_SEMANTIC_CHANGE
T4_AUTHORITY_CHANGE_FORBIDDEN
```

Authority escalation, fabricated provenance, MODEL->FACT promotion, TOOL->AUTHORITY promotion, and metaphor->solver inference are outside the automatically projectable space.

## Compression of the larger architecture

Most architectural names become views/operators over six objects:

```text
STATE -> WINDOW -> CANDIDATE -> ADMISSIBLE SET -> RECEIPT -> DELTA
```

- Mission Compiler: produces the typed mission/signature.
- Spectral Centralizer: types state coordinates and rejects ambiguous spectrum labels.
- MissionWindow: projects state to the smallest dependency closure.
- SemanticIndex: defines stable basis/identity for concepts.
- TRI-VECTOR 3x8: address/view coordinates over Evidence/Model/Action state.
- NANO K0..K6: lifecycle around proposal, admission, bounded execution, verification, and pruning.
- OPUS Assurance Kernel: defines `A(x_t)` and the projection receipt.
- Anti-Malfunction: detects structural contradiction in the encoded result.
- Snapshot/Merkle root: identifies encoded state for delta/reuse; it does not prove truth.
- Benchmark Ledger: supplies evidence for promotion or pruning.

This is the intended simplification target: fewer persistent modules, stronger contracts, and explicit mathematical boundaries.
