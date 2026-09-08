# Metrics

OPUS uses scoped metrics and avoids invented global scores.

## Fixture match rate

`matched fixture verdicts / total fixture variants`

Useful for regression testing the harness.

Not equivalent to:
- model accuracy;
- real-world safety;
- truthfulness;
- causal validity;
- ecosystem adoption.

## False-PASS count

A fixture expected to be `BLOCK`, `REPAIR`, or `UNKNOWN` but observed as `PASS`.

## UNKNOWN rate

Tracked separately because refusing unsupported certainty can be preferable to fabricating a PASS.

Future metrics should be added only with a clear denominator, scope, and benchmark provenance.
