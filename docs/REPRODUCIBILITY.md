# Reproducibility

For published benchmarks:
1. pin source repository commit;
2. record interpreter/toolchain version;
3. record dependency lock/checksum;
4. preserve baseline and candidate separately;
5. preserve failing cases and invariants;
6. run an independent verifier/readback where practical;
7. disclose assumptions and remaining UNKNOWNs.

## Manifest validation

`MANIFEST.json` is a release-core inventory, not an implicit claim that every
shadow experiment, generated receipt or later development file is included.
Run `python scripts/validate_manifest.py` to verify every declared path,
byte-count and SHA-256 digest. The result is `PARTIAL_INVENTORY` when declared
entries are intact but additional repository files are present. Use
`--strict` only for a deliberately frozen release snapshot; it fails closed on
any unlisted file or declaration mismatch.
