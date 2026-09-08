# Closed-loop assurance and incremental verification

This document defines the smallest current coupling between a generator/orchestrator and OPUS Eval Fabric.

OPUS is **not** another planning agent. A generator proposes a candidate; OPUS defines the typed admissibility boundary around execution and verifies the observed outcome afterward.

## Core equations

Let `x_t` be the declared state and `G` any generator (human, script, CI bot, local model, hosted model, or orchestrator):

```text
u_t = G(x_t)
```

OPUS defines an admissible set `A(x_t)` from evidence, semantic, authority, proof-obligation, rollback/readback and other explicit contracts.

```text
a_t = Projection_A(x_t)(u_t)
```

The implementation does not pretend to solve a continuous geometric optimization problem. `Projection` is a typed engineering interpretation:

- `PASS / IDENTITY`: candidate already satisfies the declared admissibility contract;
- `REPAIR`: a bounded contract/semantic repair may exist, but OPUS does not fabricate or auto-apply it;
- `UNKNOWN`: available information is insufficient to resolve admissibility;
- `BLOCK`: reaching admissibility would cross a hard boundary, such as missing authority.

After an external executor performs an admitted action:

```text
x_(t+1) = F(x_t, a_t)
y_(t+1) = Readback(x_(t+1))
post = OPUS_POST(a_t, y_(t+1))
```

OPUS itself remains side-effect free in this slice.

## Proof-carrying change

`pcc.py` adds a generator-independent envelope:

```text
ProofCarryingChange
  change_id
  MissionPacket
  ProofObligation[]
  Postcondition[]
```

The change fingerprint binds the declared proposal, evidence/model/action packet, proof obligations and postconditions. A hash identifies encoded content; it does not establish truth.

## Pre-execution law

```text
EXECUTE(change) => PRE(change) == PASS
```

`prepare_change()` produces a `PreExecutionReceipt`. An otherwise-PASS legacy packet with no explicit proof obligations is downgraded to `UNKNOWN` in this proof-carrying path rather than fabricating coverage.

## Post-execution law

`verify_observed_outcome()` checks explicit observations against declared postconditions. Current deterministic comparators are deliberately small:

- `eq` — exact equality;
- `present` — the observation key must be present.

Unsupported comparators remain `UNKNOWN` instead of being guessed.

Observed mismatch yields `REPAIR / ROLLBACK_RECOMMENDED`. The library recommends rollback but never executes it. Missing readback evidence yields `UNKNOWN`.

An outcome that looks successful cannot erase a missing pre-execution admission: executing a candidate without a PASS pre-receipt yields a BLOCK post-receipt.

## Delta and receipt reuse

For shallow state records:

```text
Delta = changed_keys(before, after)
Affected(Delta) = reachable_dependents(Delta)
```

A verification receipt may be reused only if none of its declared dependencies lies in `Affected(Delta)`.

```text
Eval_(t+1) = Eval(Affected(Delta)) + Reuse(UnchangedReceipts)
```

This is an optimization of recomputation, not of epistemic standards. Reuse requires stable dependency identity. Unknown/global dependencies must broaden the invalidation scope rather than silently reuse stale receipts.

## Hard invariants

- OPUS does not grant or infer authority.
- OPUS does not fabricate provenance, rollback targets, readback observations or proof coverage.
- Generated/model output does not self-promote to observed fact.
- Hash equality is state identity, not truth.
- Graph reachability is dependency scope, not causal proof.
- A postcondition PASS does not retroactively authorize an action that lacked pre-admission.
- Reuse optimizes repeated verification; it never weakens a required verifier.

## Next real-workflow benchmark

The next promotion gate should compare full re-evaluation against delta-based receipt reuse on real pull requests. Measure:

1. verifier calls avoided;
2. wall-clock time;
3. stale-receipt false reuse (target: zero on the evaluated suite);
4. omitted invalidations;
5. false PASS / UNKNOWN / REPAIR / BLOCK transitions;
6. reproducibility of before/after fingerprints;
7. rollback/readback completeness.

Persistent default promotion requires measured net benefit, not architecture elegance alone.
