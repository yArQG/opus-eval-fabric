# Finalization topology

## Integrated development spine

The finalization pack is based on the stacked, observed development lineage rather than on a synthetic merge of every branch:

```text
main
  |
  v
bootstrap/v0.2.0
  |
  v
feature/command-center-v0.3
  |
  v
feature/closed-loop-assurance-v0.3
  |
  v
benchmark/dogfood-incremental-v0.3
  |
  v
benchmark/proof-lanes-v0.3
  |
  v
benchmark/factorized-ci-shadow-v0.3
  |
  v
benchmark/paired-timing-v0.4
  |
  v
audit/receipt-hardening-v0.5
  |
  v
finalize/open-science-pack-v0.6
```

The finalization base commit is `876b779acef59343485a491bd77630eff302077c`.

## Experimental branches

The following branches are treated as evidence-producing shadow experiments rather than automatic promotion inputs:

```text
experiment/proof-lanes-shadow-v0.3
experiment/install-subcost-shadow-v0.3
```

Their useful observations may be cited by an integration decision, but branch existence or a green run does not grant release authority.

## Assurance topology

```text
EVIDENCE / EIR
      |
      v
SEMANTIC CONTRACT / SIR
      |
      v
CANDIDATE CHANGE
      |
      v
ASSURANCE / ADMISSIBILITY GATE
  |       |        |        |
 PASS   REPAIR   UNKNOWN   BLOCK
  |
  v
AUTHORIZED BOUNDED EXECUTION
  |
  v
OBSERVED READBACK / XIR
  |
  v
POST-CONDITION CHECK
  |
  +--> KEEP / REPAIR / ROLLBACK RECOMMENDATION
```

This is one synchronized state viewed through evidence, semantics and execution. It is not a voting ensemble.

## Storage and authority topology

```text
                     CANONICAL AUTHORITY
                            |
             +--------------+--------------+
             |                             |
        public code                    system policy
          GitHub                     CORE_SYSTEM/Drive
             |                             |
             +--------------+--------------+
                            |
                      verified snapshots
                            |
             +--------------+--------------+
             |                             |
       BACKUP_COPY                     REPLICA
     cloud capsules              local/synchronized copy
             |                             |
             +--------------+--------------+
                            |
                     restore candidate
                            |
                     integrity + tests
                            |
                     explicit promotion
```

`CONTENT IDENTITY`, `LOCATION`, `AVAILABILITY` and `AUTHORITY` are separate attributes. Synchronization or duplication does not promote a copy to canonical state.

## Naming layer versus engineering layer

Project metaphors such as ULTRATRON, VOLTRATRON, CAUSALTRON and related names may label architectural views or capsules. In the public engineering core they must resolve to explicit contracts such as typed state, dependency closure, verification, provenance, readback, rollback, topology or reproducibility. A metaphor never selects a physical, causal, quantum or specialist solver by itself.
