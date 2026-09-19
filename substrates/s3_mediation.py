"""S3 - a gate that reads a third term.

A pairwise gate can only see its two endpoints. A mediated gate also reads a
term computed from the whole configuration. exp3 measures what that buys.
"""
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet

from .s0_substrate import Substrate
from .s2_topology import Pair, pair

Config = Dict[str, Substrate]


def total_load(config: Config) -> int:
    """The mediating term used in exp3: the summed state of the configuration."""
    return sum(s.state for s in config.values())


@dataclass(frozen=True)
class MediatedTopology:
    """Adjacency is a function of the two endpoints AND a configuration-wide term."""
    gate: Callable[[Substrate, Substrate, int], bool]
    medium: Callable[[Config], int] = total_load

    def edge_set(self, config: Config) -> FrozenSet[Pair]:
        ctx = self.medium(config)
        sids = sorted(config)
        return frozenset(
            pair(a, b)
            for i, a in enumerate(sids)
            for b in sids[i + 1:]
            if self.gate(config[a], config[b], ctx)
        )

    def neighbours(self, config: Config, sid: str) -> FrozenSet[str]:
        return frozenset(x for e in self.edge_set(config) if sid in e for x in e if x != sid)


def load_gated_ring(modulus: int, wide: int, narrow: int, threshold: int):
    """Ring adjacency whose radius widens or narrows with the mediating term."""
    def gate(a: Substrate, b: Substrate, ctx: int) -> bool:
        d = abs(a.state - b.state) % modulus
        ring_d = min(d, modulus - d)
        radius = wide if ctx < threshold else narrow
        return ring_d <= radius
    return gate
