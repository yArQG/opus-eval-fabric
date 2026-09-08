from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TriAxis(str, Enum):
    EVIDENCE = "E"
    MODEL = "M"
    ACTION = "A"


PORTS = (
    "SOURCE_PROVENANCE",
    "TIME_STATE",
    "UNCERTAINTY_CONTRADICTION",
    "REPRESENTATION_SEMANTICS",
    "TRANSFORM_GENERATOR",
    "VERIFIER_COUNTEREXAMPLE",
    "AUTHORITY_SIDE_EFFECT",
    "OUTCOME_LEARNING",
)


@dataclass(frozen=True)
class Contact:
    axis: TriAxis
    port_index: int
    port: str

    @property
    def address(self) -> str:
        return f"{self.axis.value}{self.port_index + 1}:{self.port}"


def contacts() -> tuple[Contact, ...]:
    return tuple(
        Contact(axis=axis, port_index=index, port=port)
        for axis in TriAxis
        for index, port in enumerate(PORTS)
    )
