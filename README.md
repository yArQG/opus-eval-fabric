# OPUS Eval Fabric

Evidence-first evaluation and anti-malfunction harness for agentic AI workflows.

The release candidate keeps four things separate by construction:

1. **Evidence class** — FACT / MEASUREMENT / INFERENCE / MODEL / HYPOTHESIS / SIMULATION / UNKNOWN.
2. **Authority** — observing or evaluating an action does not authorize the action.
3. **Verification scope** — changed objects select only applicable verifier contracts; unclassified dependency scope fails closed.
4. **Reproducibility** — packets can be serialized canonically and hashed for stable receipts.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e '.[test]'
pytest
opus-eval doctor
```

Example:

```bash
opus-eval eval --goal "verify claim" --claim "build passed" --evidence-class MEASUREMENT --source receipt:ci-123
```

Verifier planning:

```bash
opus-eval select-verifiers src/opus_eval_fabric/model.py
```

Unclassified changes fail closed and select the full verifier set.

## Scope

This is a deliberately small public-core candidate. It is not a claim of AGI, autonomous authority, scientific truth, consciousness, or universal causal inference.

## Core invariant

`PLAN != DISPATCH != EFFECT` and `TECHNICAL PASS != AUTHORITY`.

Effectful integrations should add explicit adapters and human authority gates rather than weakening the core model.
