# v0.3 pre-promotion polishing notes

This document records hardening applied before any broader command-center promotion.

## Admission tightened

The v0.3 command-center path is intentionally stricter than the v0.2 evaluator. A core PASS is not enough to produce a command-center PASS when required planning metadata is unresolved. Missing `ProblemSignature` fields or rejected spectrum labels downgrade only an otherwise-PASS result to `UNKNOWN`; they never soften an existing `REPAIR` or `BLOCK` verdict.

Required planning fields are explicit object type, domain, temporal scope, evidence mode, representation, goal and proof obligation. The mission text and declared evidence uncertainty may populate their corresponding fields, but specialist solver semantics are never inferred from metaphorical labels.

## Route ordering

Declared capabilities are ordered deterministic-first, then lower-risk, then lower-cost. Availability remains a hard admission requirement. This router still performs no hidden execution.

## Benchmark ledger integrity

Duplicate `run_id` values are rejected rather than silently appended. The ledger remains side-effect-free and caller-persisted.

## CI supply-chain hardening

GitHub Actions used by CI are pinned to the exact commits currently referenced by the official major-version tags. Checkout does not persist credentials. CI has bounded time, concurrent superseded runs are cancelled, the Python matrix does not fail-fast, and benchmark artifacts have bounded retention.

## Promotion condition

Structural green tests remain necessary but insufficient. Default promotion still requires real pull-request benchmark evidence against the simpler v0.2 baseline.
