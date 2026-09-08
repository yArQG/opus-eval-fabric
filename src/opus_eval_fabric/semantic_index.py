from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticKey:
    namespace: str
    concept_id: str
    sense_id: str = "default"


@dataclass(frozen=True)
class SemanticEntry:
    key: SemanticKey
    label: str
    aliases: tuple[str, ...] = ()


class SemanticIndex:
    """Small stable-ID index; labels and aliases never become machine identity."""

    def __init__(self) -> None:
        self._by_key: dict[SemanticKey, SemanticEntry] = {}
        self._alias_to_keys: dict[str, set[SemanticKey]] = {}

    def add(self, entry: SemanticEntry) -> None:
        if entry.key in self._by_key:
            raise ValueError(f"duplicate semantic key: {entry.key}")
        self._by_key[entry.key] = entry
        for token in (entry.label, *entry.aliases):
            norm = token.casefold().strip()
            self._alias_to_keys.setdefault(norm, set()).add(entry.key)

    def get(self, key: SemanticKey) -> SemanticEntry:
        return self._by_key[key]

    def resolve_label(self, label: str) -> tuple[SemanticKey, ...]:
        return tuple(sorted(self._alias_to_keys.get(label.casefold().strip(), ()), key=lambda k: (k.namespace, k.concept_id, k.sense_id)))
