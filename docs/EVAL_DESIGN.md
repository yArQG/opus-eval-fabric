# Eval design

A single green test is not robust evidence for an agentic workflow.

The harness separates:
- evidence quality;
- model adequacy;
- action authority;
- contextual robustness;
- verifier diversity;
- outcome/readback.

Promotion path:

`baseline -> shadow -> method-diverse verify -> perturb/holdout -> reversible canary -> promote/merge/reject`

Future fixtures should contain tempting wrong solutions and context-triggered failures so an eval discriminates superficial from robust fixes.
