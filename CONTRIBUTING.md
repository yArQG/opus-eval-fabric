# Contributing

Principles:
- evidence before claim;
- minimal reproducible changes;
- no silent broad rewrites;
- new dependencies require distinct capability value;
- tests should include failure cases;
- verifier diversity is preferred where practical.

Workflow:
1. open an issue describing the invariant/problem;
2. create a focused branch;
3. add/update tests;
4. make the smallest sufficient change;
5. run `python -m unittest discover -s tests -v`;
6. open a PR describing assumptions, risks and rollback.

Contributions are provided under the MIT license.
