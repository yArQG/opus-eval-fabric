from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ToolLayer(str, Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    WEB = "WEB"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    layer: ToolLayer
    deterministic: bool
    cost_rank: int = 0
    risk_rank: int = 0
    available: bool = True

    @property
    def score(self) -> tuple[int, int, int, str]:
        return (
            0 if self.deterministic else 1,
            self.cost_rank,
            self.risk_rank,
            self.capability_id,
        )


def select_capability(candidates: Iterable[Capability]) -> Capability | None:
    eligible = [c for c in candidates if c.available]
    if not eligible:
        return None
    return min(eligible, key=lambda c: c.score)
