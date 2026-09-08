from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from .fingerprint import canonical_json, sha256_json


@dataclass(frozen=True)
class Snapshot:
    root: str
    leaves: tuple[tuple[str, str], ...]


def _pair_hash(left: str, right: str) -> str:
    return hashlib.sha256(f"{left}:{right}".encode("ascii")).hexdigest()


def build_snapshot(state: Mapping[str, Any]) -> Snapshot:
    """Build a deterministic Merkle-style integrity snapshot.

    The root identifies encoded state; it does not establish truth.
    """
    leaves = tuple((str(k), sha256_json(v)) for k, v in sorted(state.items(), key=lambda kv: str(kv[0])))
    if not leaves:
        return Snapshot(hashlib.sha256(b"").hexdigest(), ())
    level = [hashlib.sha256(f"{k}:{v}".encode("utf-8")).hexdigest() for k, v in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [_pair_hash(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return Snapshot(level[0], leaves)


def snapshot_payload(snapshot: Snapshot) -> str:
    return canonical_json({"root": snapshot.root, "leaves": snapshot.leaves})
