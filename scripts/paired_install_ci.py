"""Bounded shadow pilot. Results are descriptive, never promotion authorization."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tomllib


def orders(pairs, block):
    if pairs < 2 or pairs > 10 or pairs % 2:
        raise ValueError('use an even pair count between 2 and 10')
    return [('baseline', 'explicit') if (i + block) % 2 == 0 else ('explicit', 'baseline') for i in range(pairs)]


def summarize(rows):
    if not rows or len(rows) % 2:
        raise ValueError('incomplete pairs')
    pairs = {}
    for row in rows:
        if row['status'] != 'PASS' or row['variant'] not in ('baseline', 'explicit'):
            raise ValueError('failed or unknown arm')
        arms = pairs.setdefault(row['pair'], {})
        if row['variant'] in arms:
            raise ValueError('duplicate arm')
        arms[row['variant']] = row
    deltas = []
    for arms in pairs.values():
        if set(arms) != {'baseline', 'explicit'}:
            raise ValueError('unpaired evidence')
        deltas.append(arms['explicit']['install_total_s'] - arms['baseline']['install_total_s'])
    return {'pairs': len(deltas), 'paired_deltas_s': deltas,
            'median_delta_s': statistics.median(deltas), 'min_delta_s': min(deltas),
            'max_delta_s': max(deltas), 'promotion': 'BLOCKED_PILOT_ONLY'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pairs', type=int, default=4)
    p.add_argument('--block', type=int, default=0)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    schedule = orders(args.pairs, args.block)
    root = Path(__file__).resolve().parents[1]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if head != os.environ.get('GITHUB_SHA'):
        raise ValueError('checked-out commit does not match GITHUB_SHA')
    config = tomllib.loads((root / 'pyproject.toml').read_text())
    requirements = config['build-system']['requires']
    report = {'schema_version': '0.1', 'head_sha': head, 'block': args.block,
              'run_id': os.environ.get('GITHUB_RUN_ID'), 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
              'python': sys.version, 'platform': platform.platform(),
              'runner_image': os.environ.get('ImageVersion'), 'build_requirements': requirements,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cache_policy': 'pip cache disabled per command; upstream network caches uncontrolled',
              'status': 'INCOMPLETE', 'rows': [], 'promotion': 'BLOCKED_PILOT_ONLY'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    logdir = args.output.parent / 'logs'; logdir.mkdir(exist_ok=True)
    try:
        for pair, order in enumerate(schedule):
            for position, variant in enumerate(order):
                row = {'pair': pair, 'position': position, 'variant': variant, 'status': 'INCOMPLETE', 'phases': {}}
                report['rows'].append(row)
                with tempfile.TemporaryDirectory(prefix='opus-paired-') as temp:
                    envdir = Path(temp) / 'venv'
                    env = dict(os.environ)
                    env.pop('PYTHONPATH', None)
                    env.update(PIP_NO_CACHE_DIR='1', PIP_DISABLE_PIP_VERSION_CHECK='1', PYTHONNOUSERSITE='1')
                    def run(label, command):
                        start = time.perf_counter_ns()
                        with (logdir / f'{pair}-{variant}-{label}.txt').open('w') as log:
                            result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
                        row['phases'][label] = (time.perf_counter_ns() - start) / 1e9
                        if result.returncode:
                            raise RuntimeError(f'{variant} {label} failed: {result.returncode}')
                    run('venv', [sys.executable, '-m', 'venv', str(envdir)])
                    python = str(envdir / 'bin/python')
                    cli = str(envdir / 'bin/opus-eval')
                    if variant == 'explicit':
                        run('bootstrap', [python, '-m', 'pip', 'install', *requirements])
                    run('install', [python, '-m', 'pip', 'install', *(['--no-build-isolation'] if variant == 'explicit' else []), '-e', '.'])
                    row['install_total_s'] = row['phases']['install'] + row['phases'].get('bootstrap', 0)
                    run('versions', [python, '-m', 'pip', 'list', '--format=json'])
                    run('unit', [python, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
                    commands = [['doctor'], ['validate', 'examples/mission.json'], ['run', 'examples/mission.json'],
                                ['plan', 'examples/mission.json'], ['command-center', 'examples/mission.json'],
                                ['adapter-python', '--source', 'src/opus_eval_fabric/evaluator.py'],
                                ['benchmark', 'benchmarks/suite.json', '--json-out', str(logdir / f'{pair}-{variant}-foundation.json')],
                                ['benchmark-incremental', 'benchmarks/dogfood/pr3_ci_action_pinning.json', '--json-out', str(logdir / f'{pair}-{variant}-incremental.json')]]
                    for index, command in enumerate(commands):
                        run(f'proof-{index}', [cli, *command])
                    row['status'] = 'PASS'
        report['summary'] = summarize(report['rows'])
        report['status'] = 'PASS'
    finally:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
