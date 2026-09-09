from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def _ts(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() is None:
        raise ValueError('timestamps must include a timezone')
    return result


def analyze(payload: dict) -> dict:
    """Analyze wall intervals; never infer CPU time or scheduler cause."""
    created = _ts(payload['created_at'])
    completed = _ts(payload['completed_at'])
    if completed < created:
        raise ValueError('workflow ends before creation')
    raw = payload['jobs']
    if not raw:
        raise ValueError('no jobs: timing evidence is incomplete')
    names = [j['name'] for j in raw]
    if any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
        raise ValueError('job names must be nonempty and unique')
    intervals = {}
    for job in raw:
        start, end = _ts(job['started_at']), _ts(job['completed_at'])
        if not created <= start <= end <= completed:
            raise ValueError('job interval outside workflow or negative')
        intervals[job['name']] = (start, end)
    dependencies = payload.get('dependencies')
    paths, ready = {}, {}
    if dependencies is not None:
        if set(dependencies) != set(names):
            raise ValueError('dependencies must enumerate every job, including roots')
        visiting = set()

        def visit(name):
            if name in paths:
                return
            if name in visiting:
                raise ValueError('dependency cycle')
            visiting.add(name)
            parents = dependencies[name]
            if not isinstance(parents, list) or any(not isinstance(p, str) for p in parents):
                raise ValueError('dependencies must be lists of job names')
            if len(set(parents)) != len(parents) or any(p not in intervals for p in parents):
                raise ValueError('duplicate or unknown dependency')
            for parent in parents:
                visit(parent)
            ready[name] = max([created] + [intervals[p][1] for p in parents])
            start, end = intervals[name]
            if start < ready[name]:
                raise ValueError('job starts before dependency completion')
            paths[name] = (end - start).total_seconds() + max([0] + [paths[p] for p in parents])
            visiting.remove(name)

        for name in names:
            visit(name)
    jobs = []
    for job in raw:
        name = job['name']
        start, end = intervals[name]
        jobs.append({
            'name': name,
            'start_offset_s': (start - created).total_seconds(),
            'job_elapsed_s': (end - start).total_seconds(),
            'dependency_wait_s': (ready[name] - created).total_seconds() if dependencies is not None else None,
            'ready_to_start_s': (start - ready[name]).total_seconds() if dependencies is not None else None,
        })
    last_end = max(end for start, end in intervals.values())
    return {
        'schema_version': '0.2',
        'end_to_end_s': (completed - created).total_seconds(),
        'max_job_elapsed_s': max(j['job_elapsed_s'] for j in jobs),
        'execution_path_elapsed_s': max(paths.values()) if dependencies is not None else None,
        'max_start_offset_s': max(j['start_offset_s'] for j in jobs),
        'finalization_s': (completed - last_end).total_seconds(),
        'topology_status': 'DECLARED' if dependencies is not None else 'UNKNOWN',
        'jobs': jobs,
        'scope': 'Wall time includes setup, I/O, network and teardown; not CPU compute. Ready-to-start is a residual, not attributed scheduler time. Longest weighted DAG path excludes waits.',
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = analyze(json.loads(args.input.read_text(encoding='utf-8')))
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
