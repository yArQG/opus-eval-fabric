# Dogfood: incremental receipt reuse on OPUS PR history

This benchmark uses an observed change from OPUS Eval Fabric's own PR #3 rather than a synthetic software-change example.

Between commits:

- base `1b2c1efafddfe4cdf6c991cb84fa8594a31840b6`
- head `28f80f8c5c72bebb65eab47cd125f32b821d94cf`

GitHub compare reported one modified file: `.github/workflows/ci.yml`. The change pinned current GitHub Actions releases to exact commit SHAs. `src/opus_eval_fabric/closed_loop.py` retained the same Git blob SHA across the two commits.

The fixture therefore asks a narrow question: given explicit receipt dependencies, which receipts must be invalidated by this observed delta and which content-only receipt may be reused?

## Fail-closed scope rule

Receipt reuse is no longer implicit. `ReceiptDependency.scope` is one of:

- `LOCAL` — reuse is possible only when at least one dependency is declared and none is in `Affected(Delta)`;
- `GLOBAL` — any observed delta invalidates the receipt;
- `UNKNOWN` — any observed delta invalidates the receipt.

The default is `UNKNOWN`. A `LOCAL` receipt with an empty dependency list also invalidates on change. This is intentional: an optimization must not silently assume dependency completeness.

For this fixture, the changed CI workflow invalidates CI/toolchain receipts plus GLOBAL/UNKNOWN receipts. A receipt whose only declared dependency is the unchanged `closed_loop.py` source identity is reusable.

## Run

```bash
opus-eval benchmark-incremental benchmarks/dogfood/pr3_ci_action_pinning.json \
  --json-out artifacts/dogfood-incremental.json
```

## Scope

This is a structural dogfood result, not a performance result. `performance_measured` is deliberately `false`.

It does **not** prove:

- that every possible dependency has been modeled;
- that incremental verification is faster in wall-clock time;
- that a reused receipt remains valid if its dependency declaration is incomplete;
- that graph reachability establishes causality;
- real-world AI safety or correctness.

The next promotion gate is a timed, full-vs-incremental verifier benchmark on multiple real pull requests with stale-receipt false reuse and omitted invalidation explicitly measured.
