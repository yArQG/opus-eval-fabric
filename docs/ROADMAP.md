# Roadmap

## 0.1 — foundation
- [x] typed E/M/A packets
- [x] PASS / REPAIR / BLOCK / UNKNOWN
- [x] retorsion guard
- [x] CODE-24 metadata registry
- [x] eight neutral transform operators
- [x] stdlib-only core
- [x] unit tests and CI

## 0.2 — measurable foundation
- [x] three reproducible workflow benchmark families
- [x] contextual perturbation helpers
- [x] verifier interface
- [x] JSON/JUnit benchmark reports
- [x] provenance/environment fingerprinting
- [x] first safe CODE-24 adapter (Python detection + syntax)
- [x] CI benchmark artifacts

## 0.3 — proof-carrying maintainer workflow
- [ ] `ProofCarryingChange` / change-envelope contract
- [ ] typed proof obligations and verifier receipts
- [ ] rollback plan vs observed readback receipt separation
- [ ] GitHub PR evaluation adapter (read-only first)
- [ ] incremental evaluation graph: recompute only affected checks
- [ ] dependency/config/commit fingerprint report
- [ ] issue -> patch -> verify example
- [ ] release checklist and checksummed artifact
- [ ] first external contributor issue
- [ ] first external-model benchmark with held-out contexts

## 0.4 — orthogonal verification
- [ ] optional SymPy verifier
- [ ] optional Z3 verifier
- [ ] optional Hypothesis counterexample generator
- [ ] lm-evaluation-harness plugin
- [ ] contextual robustness benchmark with multiple seeds/samples where appropriate

## Promotion rule

`baseline -> shadow -> independent/method-diverse verify -> holdout/context perturbation -> reversible canary -> promote/merge/reject`
