# Dogfood: snapshot-bound incremental receipt reuse

This benchmark uses an observed change from OPUS Eval Fabric's own PR #3 rather than a synthetic software-change example.

Between commits:

- base `1b2c1efafddfe4cdf6c991cb84fa8594a31840b6`
- head `28f80f8c5c72bebb65eab47cd125f32b821d94cf`

GitHub compare reported one modified file: `.github/workflows/ci.yml`. The change pinned current GitHub Actions releases to exact commit SHAs. `src/opus_eval_fabric/closed_loop.py` retained the same Git blob SHA across the two commits.

## Two gates before reuse

Receipt reuse now requires both **scope** and **issuance binding**.

`ReceiptDependency.scope` is one of:

- `LOCAL` — reusable only when at least one dependency is declared and none is in `Affected(Delta)`;
- `GLOBAL` — reusable only when the bound state has no observed delta;
- `UNKNOWN` — never reused automatically.

The default is `UNKNOWN`. A `LOCAL` receipt with an empty dependency list also fails closed.

Every reusable receipt must additionally carry `source_snapshot_root` equal to the exact `before` state supplied to the reuse planner. An unbound receipt or a receipt issued for an older snapshot is invalidated even when its named dependency appears unchanged. This prevents a stale receipt from entering the fast path merely because its label matches.

For the historical fixture, the observed before root is:

`e022497f94f4842910b753298bf7e0560e3007c9a6e492d706cd115471067928`

The CI workflow delta invalidates CI-local, GLOBAL and UNKNOWN receipts. One explicitly content-only LOCAL receipt can be reused because it is bound to that exact before snapshot and its sole declared dependency is the unchanged `closed_loop.py` source identity.

## Run

```bash
opus-eval benchmark-incremental benchmarks/dogfood/pr3_ci_action_pinning.json \
  --json-out artifacts/dogfood-incremental.json
```

## Scope

This is a structural dogfood result, not a performance result. `performance_measured` is deliberately `false`.

It does **not** prove dependency declarations are complete, that incremental verification is faster, or that graph reachability is causal evidence. The next promotion gate is a timed multi-PR full-vs-incremental benchmark measuring verifier calls, latency, stale-receipt false reuse and omitted invalidations.
