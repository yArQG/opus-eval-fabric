# Architecture

## Design objective

Maximize **verified useful outcome** while minimizing active dependencies, side effects and correlated failure modes.

## EIR / SIR / XIR

- **EIR (Evidence IR):** source identity, provenance, version, time, uncertainty, source-family dependence.
- **SIR (Semantic IR):** claim, assumptions, types, invariants, data/control flow, proof obligation.
- **XIR (Execution IR):** build/test/runtime, authority, side effects, readback, rollback and observed outcome.

They are synchronized views of one workflow state, not independent votes.

## Eight reusable operators

`T0 INGEST -> T1 NORMALIZE -> T2 REVERSE -> T3 TRANSLATE -> T4 TRANSFORM -> T5 PATCH -> T6 VERIFY -> T7 RECREATE`

`J(T_i)=T_(7-i)` is a design symmetry for round-trip thinking; it is not a scientific law.

## CODE-24

CODE-24 is a curated adapter profile over a common **control plane**, not a universal AST or a claim that full language semantics can be normalized losslessly. Language-native ASTs, compilers, linters and test tools remain authoritative for language-specific checks.

Conceptually:

`language-native toolchain -> EIR/SIR/XIR control contracts -> VERIFY/REPORT`

A new language primarily adds one adapter to the common control contracts instead of a bespoke pairwise integration with every existing language. This keeps control-plane integration roughly linear while leaving semantic translation and porting language-specific and evidence-gated.

## Retorsion

Backward information flow is allowed when typed. Backward semantic authority is not.

Forbidden promotions include:

- `MODEL -> FACT`
- `TOOL -> AUTHORITY`
- `SALIENCE -> TRUTH`
- `DRIFT -> CAUSE`
- `METAPHOR -> SOLVER`
