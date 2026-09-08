from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AdapterStatus:
    language: str
    available: bool
    version: str | None
    executable: str | None
    detail: str


class LanguageAdapter(Protocol):
    language: str

    def detect(self) -> AdapterStatus:
        ...

    def check_syntax(self, source: str) -> tuple[bool, str]:
        ...
