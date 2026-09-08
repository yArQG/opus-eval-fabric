# Closed-loop assurance and incremental verification

OPUS is not another planning agent. A generator proposes a candidate; OPUS defines the typed admissibility boundary around execution and verifies the observed outcome afterward.

## Core equations

```text
u_t = G(x_t)
a_t = Projection_A(x_t)(u_t)
```

`Projection` is a typed engineering interpretation:

- `PASS / IDENTITY`: candidate already satisfies the declared admissibility contract;
- `REPAIR`: bounded repair may exist, but OPUS does not fabricate or auto-apply it;
- `UNKNOWN`: available information is insufficient to resolve admissibility;
- `BLOCK`: reaching admissibility would cross a hard boundary such as missing authority.

After an external executor performs an admitted action:

```text
x_(t+1) = F(x_t, a_t)
y_(t+1) = Readback(x_(t+1))
post = OPUS_POST(a_t, y_(t+1))
```

OPUS itself remains side-effect free in this slice.

## Proof-carrying change

`ProofCarryingChange` binds a `MissionPacket`, explicit `ProofObligation[]` and `Postcondition[]`. Its fingerprint identifies the encoded contract; it does not establish truth.

Pre-execution law:

```text
EXECUTE(change) => PRE(change) == PASS
```

An otherwise-PASS packet with no explicit proof obligations is `UNKNOWN` on the proof-carrying path rather than receiving fabricated coverage.

## Post-execution law

`verify_observed_outcome()` verifies explicit caller-supplied observations. Current deterministic comparators are deliberately small: exact equality and presence. Unsupported comparators remain `UNKNOWN`.

Observed mismatch yields `REPAIR / ROLLBACK_RECOMMENDED`, but OPUS never executes rollback. A successful-looking postcondition cannot retroactively authorize an action that lacked PRE PASS.

## Delta and receipt reuse

```text
Delta = changed_keys(before, after)
Affected(Delta) = reachable_dependents(Delta)
Eval_(t+1) = Eval(Affected(Delta)) + Reuse(UnaffectedBoundReceipts)
```

Reuse has two independent gates.

**Dependency scope**:

- `LOCAL`: requires explicit dependencies and none may intersect `Affected(Delta)`;
- `GLOBAL`: reusable only when there is no observed delta;
- `UNKNOWN`: never auto-reused and is the default.

**Issuance binding**:

A receipt must carry `source_snapshot_root` equal to the exact `before` state. Missing or stale issuance binding invalidates it. This stops an old receipt from being reused solely because a dependency label appears unchanged.

This optimization never weakens a required verifier. Unknown scope, missing dependencies or stale binding select re-verification rather than reuse.

## Hard invariants

- OPUS does not grant or infer authority.
- OPUS does not fabricate provenance, rollback targets, readback observations or proof coverage.
- Generated/model output does not self-promote to observed fact.
- Hash equality is state identity, not truth.
- Graph reachability is dependency scope, not causal proof.
- A postcondition PASS does not retroactively authorize an action that lacked pre-admission.

## Promotion gate

The PR #3 dogfood fixture is structural evidence only. Persistent default promotion requires timed full-vs-incremental evaluation on multiple real pull requests, measuring verifier calls avoided, wall-clock time, stale-receipt false reuse, omitted invalidations, verdict transitions and fingerprint reproducibility.
