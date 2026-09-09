from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def analyze(payload: dict) -> dict:
    created = _ts(payload["created_at"])
    completed = _ts(payload["completed_at"])
    jobs = []
    for job in payload["jobs"]:
        started = _ts(job["started_at"])
        ended = _ts(job["completed_at"])
        queue = (started - created).total_seconds()
        compute = (ended - started).total_seconds()
        if queue < 0 or compute < 0:
            raise ValueError("negative timing interval")
        jobs.append({
            "name": job["name"],
            "queue_delay_s": queue,
            "compute_duration_s": compute,
            "steps": job.get("steps", []),
        })
    return {
        "schema_version": "0.1",
        "end_to_end_s": (completed - created).total_seconds(),
        "critical_compute_s": max((j["compute_duration_s"] for j in jobs), default=0.0),
        "max_queue_delay_s": max((j["queue_delay_s"] for j in jobs), default=0.0),
        "jobs": jobs,
        "law": "T_observed = T_scheduler + T_compute; compare both clocks separately",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = analyze(json.loads(args.input.read_text(encoding="utf-8")))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
