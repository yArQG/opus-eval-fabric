# Language adapter contract

CODE-24 is a registry, not 24 installed compilers.

An adapter should expose the smallest useful interface:

```text
detect() -> toolchain status
check_syntax(source) -> bounded syntax result
```

Future language adapters may add build/test/lint/package functions, but only after a real workflow shows distinct value.

Every adapter should record:
- upstream project;
- toolchain/version;
- license snapshot;
- network requirement;
- read/write scope;
- sandbox policy;
- reproducibility/rollback strategy.

`PythonAdapter` is the first minimal implementation. It uses only the current Python runtime and `ast.parse`; it does not execute arbitrary source.
