from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkEntry:
    run_id: str
    benchmark_id: str
    verdict: str
    input_fingerprint: str
    output_fingerprint: str
    scope_note: str


class BenchmarkLedger:
    """Append-only in-memory ledger representation.

    Persistence is intentionally left to the caller so this class has no hidden
    filesystem or network side effects.
    """

    def __init__(self, entries: Iterable[BenchmarkEntry] = ()) -> None:
        self._entries = list(entries)

    def append(self, entry: BenchmarkEntry) -> None:
        self._entries.append(entry)

    def rows(self) -> tuple[dict[str, str], ...]:
        return tuple(asdict(x) for x in self._entries)
