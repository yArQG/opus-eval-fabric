# Proof-Carrying Change — v0.3 design target

OPUS should evaluate a change as more than a patch plus a green test. A release candidate should carry the machine-readable material needed to justify release and recovery.

## Proposed envelope

```text
Change = proposal + evidence + semantic contract + execution contract
       + proof obligations + verifier receipts + rollback plan
       + observed readback + fingerprints
```

A future `ProofCarryingChange` should distinguish **plans** from **receipts**:

- a rollback plan states how recovery would be attempted;
- a readback receipt records what was actually observed after execution;
- a verifier receipt records what was checked, by which method family/version, against which input fingerprint.

## Release rule

A release is admissible only when required evidence, semantic, authority and verification gates are satisfied for the declared scope. Missing material remains `UNKNOWN` or `REPAIR`; it must not be silently promoted to `PASS`.

## Non-goals

- no universal AST for all programming languages;
- no claim that one verifier proves real-world correctness;
- no automatic widening of permissions from successful execution;
- no automatic merge in the initial GitHub adapter.

## Incremental evaluation

Checks should declare dependencies. When a change modifies only one field or artifact, OPUS should invalidate and recompute only reachable dependent checks, while reusing unchanged receipts with matching fingerprints.

`Affected(delta) = reachable_dependents(delta)`

This design remains benchmark-gated until implemented and measured on real pull requests.
