"""Bounded shadow pilot. Results are descriptive, never promotion authorization."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tomllib
from urllib.parse import urlsplit


def _index_provenance(env):
    """Record package-index provenance without exposing URL credentials."""
    configured_keys = []
    fingerprints = []
    entry_count = 0
    for key in ('PIP_INDEX_URL', 'PIP_EXTRA_INDEX_URL'):
        raw = env.get(key, '').strip()
        if not raw:
            continue
        configured_keys.append(key)
        for token in raw.split():
            entry_count += 1
            parsed = urlsplit(token)
            if parsed.scheme and parsed.hostname:
                normalized = f'{parsed.scheme.lower()}://{parsed.hostname.lower()}'
                if parsed.port:
                    normalized += f':{parsed.port}'
                fingerprints.append(hashlib.sha256(normalized.encode()).hexdigest())
            else:
                fingerprints.append('INVALID')
    return {
        'configured_keys': configured_keys,
        'entry_count': entry_count,
        'redacted_fingerprints': sorted(fingerprints),
    }


def orders(pairs, block):
    if pairs < 2 or pairs > 10 or pairs % 2:
        raise ValueError('use an even pair count between 2 and 10')
    if block not in (0, 1):
        raise ValueError('block must be 0 or 1')
    return [('baseline', 'explicit') if (i + block) % 2 == 0 else ('explicit', 'baseline') for i in range(pairs)]


def summarize(rows):
    if not rows or len(rows) % 2:
        raise ValueError('incomplete pairs')
    pairs = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('status') != 'PASS' or row.get('variant') not in ('baseline', 'explicit'):
            raise ValueError('failed or unknown arm')
        pair = row.get('pair')
        position = row.get('position')
        if type(pair) is not int or pair < 0 or type(position) is not int or position not in (0, 1):
            raise ValueError('pair and position must be bounded integers')
        elapsed = row.get('install_total_s')
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('install duration must be finite and non-negative')
        arms = pairs.setdefault(pair, {'_positions': {}})
        if row['variant'] in arms:
            raise ValueError('duplicate arm')
        if position in arms['_positions']:
            raise ValueError('duplicate position')
        arms['_positions'][position] = row['variant']
        arms[row['variant']] = row
    if set(pairs) != set(range(len(pairs))):
        raise ValueError('pair identifiers must be contiguous from zero')
    deltas = []
    for arms in pairs.values():
        if {key for key in arms if key != '_positions'} != {'baseline', 'explicit'}:
            raise ValueError('unpaired evidence')
        if arms['_positions'] != {0: 'baseline', 1: 'explicit'} and arms['_positions'] != {0: 'explicit', 1: 'baseline'}:
            raise ValueError('each pair must contain exactly two positions')
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
    report = {'schema_version': '0.2', 'head_sha': head, 'block': args.block,
              'run_id': os.environ.get('GITHUB_RUN_ID'), 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
              'python': sys.version, 'platform': platform.platform(),
              'runner_image': os.environ.get('ImageVersion'), 'build_requirements': requirements,
              'index_provenance': _index_provenance(os.environ),
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
                    def run_capture(label, command):
                        start = time.perf_counter_ns()
                        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
                        (logdir / f'{pair}-{variant}-{label}.txt').write_text(result.stdout + result.stderr)
                        row['phases'][label] = (time.perf_counter_ns() - start) / 1e9
                        if result.returncode:
                            raise RuntimeError(f'{variant} {label} failed: {result.returncode}')
                        return result.stdout.strip()
                    run('venv', [sys.executable, '-m', 'venv', str(envdir)])
                    python = str(envdir / 'bin/python')
                    cli = str(envdir / 'bin/opus-eval')
                    row['runtime'] = {
                        'python_version': run_capture('python-version', [python, '--version']),
                        'pip_version': run_capture('pip-version', [python, '-m', 'pip', '--version']),
                        'index_provenance': _index_provenance(env),
                    }
                    if variant == 'explicit':
                        run('bootstrap', [python, '-m', 'pip', 'install', *requirements])
                    run('install', [python, '-m', 'pip', 'install', *(['--no-build-isolation'] if variant == 'explicit' else []), '-e', '.'])
                    row['install_total_s'] = row['phases']['install'] + row['phases'].get('bootstrap', 0)
                    versions = run_capture('versions', [python, '-m', 'pip', 'list', '--format=json'])
                    try:
                        parsed_versions = json.loads(versions)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError(f'{variant} versions output is not JSON: {exc}') from exc
                    if not isinstance(parsed_versions, list) or any(not isinstance(item, dict) for item in parsed_versions):
                        raise RuntimeError(f'{variant} versions output is not a package list')
                    row['installed_versions'] = parsed_versions
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
