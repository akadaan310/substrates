"""S2 - neighbourhood relations, two ways.

StaticTopology stores its edges.  GatedTopology derives them from state via a
pairwise predicate.  The difference between the two is the primitive under
test in exp2.
"""
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, Iterable, Tuple

from .s0_substrate import Substrate

Pair = FrozenSet[str]
Config = Dict[str, Substrate]


def pair(a: str, b: str) -> Pair:
    return frozenset((a, b))


@dataclass(frozen=True)
class StaticTopology:
    """Edges are stored data. State is not consulted."""
    edges: FrozenSet[Pair]

    def edge_set(self, config: Config) -> FrozenSet[Pair]:
        return self.edges

    def neighbours(self, config: Config, sid: str) -> FrozenSet[str]:
        return frozenset(x for e in self.edges if sid in e for x in e if x != sid)


@dataclass(frozen=True)
class GatedTopology:
    """Edges are derived: adjacency is a function of the two endpoints' states."""
    gate: Callable[[Substrate, Substrate], bool]

    def edge_set(self, config: Config) -> FrozenSet[Pair]:
        sids = sorted(config)
        return frozenset(
            pair(a, b)
            for i, a in enumerate(sids)
            for b in sids[i + 1:]
            if self.gate(config[a], config[b])
        )

    def neighbours(self, config: Config, sid: str) -> FrozenSet[str]:
        return frozenset(x for e in self.edge_set(config) if sid in e for x in e if x != sid)


def ring_gate(modulus: int, radius: int) -> Callable[[Substrate, Substrate], bool]:
    """Adjacent iff the two states are within `radius` on a ring of size `modulus`."""
    def gate(a: Substrate, b: Substrate) -> bool:
        d = abs(a.state - b.state) % modulus
        return min(d, modulus - d) <= radius
    return gate


def edge_delta(before: FrozenSet[Pair], after: FrozenSet[Pair]) -> FrozenSet[Pair]:
    return before ^ after


def split_delta(delta: Iterable[Pair], sid: str) -> Tuple[FrozenSet[Pair], FrozenSet[Pair]]:
    """Partition changed pairs into those touching `sid` and those that do not."""
    delta = frozenset(delta)
    incident = frozenset(e for e in delta if sid in e)
    return incident, delta - incident
