from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class MissionWindow:
    roots: tuple[str, ...]
    nodes: tuple[str, ...]


def dependency_closure(graph: Mapping[str, Iterable[str]], roots: Iterable[str]) -> MissionWindow:
    """Return the smallest transitive dependency closure reachable from roots."""
    ordered_roots = tuple(dict.fromkeys(str(x) for x in roots))
    seen: set[str] = set()
    stack = list(reversed(ordered_roots))
    order: list[str] = []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        deps = tuple(str(x) for x in graph.get(node, ()))
        for dep in reversed(deps):
            if dep not in seen:
                stack.append(dep)
    return MissionWindow(ordered_roots, tuple(order))
