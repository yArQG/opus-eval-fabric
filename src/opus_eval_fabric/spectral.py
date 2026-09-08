from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class SpectrumClass(str, Enum):
    SEMANTIC = "SEMANTIC"
    EVIDENCE = "EVIDENCE"
    TEMPORAL = "TEMPORAL"
    SIGNAL = "SIGNAL"
    PHYSICAL = "PHYSICAL"
    GRAPH = "GRAPH"
    PROBABILISTIC = "PROBABILISTIC"
    GEOMETRIC = "GEOMETRIC"
    CONTROL = "CONTROL"
    RESOURCE = "RESOURCE"
    RISK_AUTHORITY = "RISK_AUTHORITY"
    MISSION_DOMAIN = "MISSION_DOMAIN"


@dataclass(frozen=True)
class SpectralSelection:
    active: tuple[SpectrumClass, ...]
    rejected: tuple[str, ...] = ()

    @property
    def admissible(self) -> bool:
        return not self.rejected


def centralize_spectra(values: Iterable[str]) -> SpectralSelection:
    """Type explicit spectrum labels without guessing from metaphors.

    Unknown labels remain rejected instead of being coerced into a physical,
    signal, graph, or other mathematical spectrum.
    """
    active: list[SpectrumClass] = []
    rejected: list[str] = []
    seen: set[SpectrumClass] = set()
    for raw in values:
        label = str(raw).strip().upper()
        try:
            item = SpectrumClass(label)
        except ValueError:
            rejected.append(str(raw))
            continue
        if item not in seen:
            seen.add(item)
            active.append(item)
    return SpectralSelection(tuple(active), tuple(rejected))
