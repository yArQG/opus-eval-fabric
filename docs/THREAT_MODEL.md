# Threat model

Failure classes in scope:
- fabricated/stale evidence;
- same-family generator/judge correlated error;
- context-triggered regression;
- benchmark/test overfitting;
- unauthorized tool side effects;
- dependency drift;
- incomplete readback;
- promotion from a single successful run;
- confusing an inferred process with ground truth.

Insufficient evidence returns `UNKNOWN`, not a fabricated PASS.
