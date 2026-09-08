$ErrorActionPreference = "Stop"
python -m unittest discover -s tests -v
python -m opus_eval_fabric.cli doctor
python -m opus_eval_fabric.cli validate examples/mission.json
python -m opus_eval_fabric.cli run examples/mission.json
python -m opus_eval_fabric.cli adapter-python --source src/opus_eval_fabric/evaluator.py
New-Item -ItemType Directory -Force artifacts | Out-Null
python -m opus_eval_fabric.cli benchmark benchmarks/suite.json `
  --json-out artifacts/benchmark.json `
  --junit-out artifacts/benchmark.xml
