# Use cases

OPUS Eval Fabric is intended for bounded, auditable evaluation workflows such as:

- pull-request release gates for agent-generated or human-generated changes;
- evidence/provenance checks for research-style agent outputs;
- rollback/readback completeness for effectful automation;
- contextual regression fixtures that must not silently become `PASS`;
- language-native syntax/build/test adapters exposed through a shared control contract.

The project deliberately separates deterministic fixture results from claims about real-world model accuracy or safety.
