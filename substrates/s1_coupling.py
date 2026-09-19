"""S1 - the smallest operation by which two substrates interact without merging.

A Coupling is a directed read: it reads the source's state, and writes a new
state into the destination. It never touches either label, and it never
reduces the population count. That is the whole claim; exp1 measures it.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

from .s0_substrate import Substrate

Config = Dict[str, Substrate]


@dataclass(frozen=True)
class Coupling:
    src: str
    dst: str
    transduce: Callable[[int, int], int]  # (src_state, dst_state) -> dst_state


def apply_coupling(config: Config, c: Coupling) -> Config:
    """One directed read. Returns a new config; inputs are not mutated."""
    src = config[c.src]
    dst = config[c.dst]
    out = dict(config)
    out[c.dst] = dst.with_state(c.transduce(src.state, dst.state))
    return out


def step(config: Config, couplings: Iterable[Coupling],
         modulus_of: Callable[[str], int]) -> Config:
    """Synchronous step: every coupling reads the PREVIOUS config.

    Multiple couplings into the same destination fold in sorted source order,
    so the step is deterministic. modulus_of bounds each substrate's value.
    """
    pending: Dict[str, int] = {sid: s.state for sid, s in config.items()}
    for c in sorted(couplings, key=lambda c: (c.dst, c.src)):
        pending[c.dst] = c.transduce(config[c.src].state, pending[c.dst])
    return {sid: Substrate(sid, v % modulus_of(sid)) for sid, v in pending.items()}


def run(config: Config, couplings: Iterable[Coupling],
        modulus_of: Callable[[str], int], steps: int) -> Config:
    couplings = tuple(couplings)
    for _ in range(steps):
        config = step(config, couplings, modulus_of)
    return config


def states(config: Config) -> Tuple[Tuple[str, int], ...]:
    return tuple(sorted((sid, s.state) for sid, s in config.items()))
