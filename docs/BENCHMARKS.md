# Benchmarks

`benchmarks/suite.json` is the first reproducible deterministic regression suite.

It contains three workflow families:

1. **Patch release transaction** — catches a write path that lacks rollback.
2. **Research claim provenance** — catches missing provenance and model self-promotion.
3. **Workflow drift causality** — catches `DRIFT -> CAUSE` semantic-authority inversion.

The suite reports **fixture match rate**. This metric answers only:

> Did the harness produce the verdict encoded by these fixtures?

It does **not** measure general AI accuracy, production safety, scientific truth, or robustness on unseen tasks.

Run:

```bash
opus-eval benchmark benchmarks/suite.json \
  --json-out artifacts/benchmark.json \
  --junit-out artifacts/benchmark.xml
```

A future benchmark version should add model/provider runs, held-out prompts, multi-seed sampling where relevant, and an independent verifier family.
