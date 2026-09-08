# OPUS Eval Fabric

**Cross-domain evaluation and anti-malfunction harness for agentic AI workflows.**

OPUS Eval Fabric is an open-source framework for testing agentic workflows without treating model confidence, a single green test, or repeated same-family judgment as proof.

The public project deliberately translates a larger experimental architecture into a small engineering core:

- typed **Evidence / Model / Action** packets;
- explicit **PASS / REPAIR / BLOCK / UNKNOWN** verdicts;
- source-before-claim and authority-before-side-effect guards;
- contextual robustness probes;
- typed backward feedback (**retorsion**) without backward truth/authority promotion;
- **CODE-24**, a lazy registry of 24 open language/toolchain hubs;
- three synchronized intermediate views: **EIR / SIR / XIR**;
- eight reusable transformation operators rather than eight separate AI models;
- reversible, testable, dependency-light design.

## Why

Agentic systems can appear correct while still failing because:

- the prompt/context changes;
- evidence is missing or stale;
- a model judges another model with correlated failure modes;
- a tool can write but was never authorized to do so;
- a successful patch has no rollback/readback;
- an inferred process model is mistaken for the real process;
- a passing benchmark was overfit to its own fixture.

OPUS Eval Fabric turns those failure classes into explicit checks.

## Quick start

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
opus-eval doctor
opus-eval validate examples/mission.json
opus-eval run examples/mission.json
opus-eval code24
```

No third-party runtime dependency is required for the core.

## Architecture

```text
                 MISSION
                    |
          +---------+---------+
          |         |         |
          v         v         v
        EIR       SIR       XIR
     Evidence   Semantic   Execution
          |         |         |
          +---------+---------+
                    |
               VERIFY/COLLIDE
                    |
          PASS / REPAIR / BLOCK / UNKNOWN
                    |
              observed outcome
                    |
             typed feedback only
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## CODE-24

CODE-24 is metadata-first. It does **not** bulk-install 24 compilers. Each language hub is an optional capsule around an upstream open repository/toolchain and may later expose parser/build/test/lint/package adapters.

See [src/opus_eval_fabric/code24.json](src/opus_eval_fabric/code24.json).

## Eight operators

`T0..T7` are reusable workflow operators:

1. INGEST
2. NORMALIZE
3. REVERSE
4. TRANSLATE
5. TRANSFORM
6. PATCH
7. VERIFY
8. RECREATE

The public project uses neutral names. Experimental aliases are kept in a profile, not presented as scientific claims.

## Status

`v0.2.0` is an alpha, measurable foundation. It provides deterministic regression fixtures, verifier contracts, fingerprints, a safe Python adapter, JSON/JUnit reports, and CI integration. It does **not** claim production-grade AI safety, universal correctness, or real-world accuracy from fixture pass rates.

## Design direction: proof-carrying changes

The next maintainer-facing milestone is a **proof-carrying change** contract: a proposed change should carry its provenance, semantic obligations, verifier receipts, rollback plan, observed readback, and reproducibility fingerprints. This is a design target for v0.3, not a claim that v0.2 already implements the full maintainer transaction.

See [docs/PROOF_CARRYING_CHANGE.md](docs/PROOF_CARRYING_CHANGE.md).

## License

MIT.


## v0.2: measurable foundation

Version 0.2 moves the project from architecture-only validation toward reproducible evaluation:

- three deterministic workflow benchmark families;
- JSON + JUnit benchmark reports;
- SHA-256 provenance fingerprints;
- explicit verifier interface;
- first safe CODE-24 adapter (`PythonAdapter`);
- contextual perturbation helpers;
- CI benchmark artifacts.

Run the full deterministic suite:

```bash
opus-eval benchmark benchmarks/suite.json \
  --json-out artifacts/benchmark.json \
  --junit-out artifacts/benchmark.xml
```

The current fixture match rate is a regression-test metric only. It is not presented as real-world AI accuracy or safety.
