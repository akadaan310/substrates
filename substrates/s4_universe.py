"""S4 - bounded state spaces, and the smallest structure that conjoins them.

A Universe is a named set of substrates plus the bound on their state space.
Two universes with different bounds can be related in two ways:

  collapse  - re-bound everything to one modulus (one state space)
  conjoin   - keep both bounds, and relate one boundary pair through an
              Interface, which is a partial directed map BETWEEN the two
              state spaces rather than a union of them

exp4 measures the difference.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

from .s0_substrate import Substrate
from .s1_coupling import Config, Coupling


@dataclass(frozen=True)
class Universe:
    uid: str
    modulus: int              # states live in range(modulus)
    members: Tuple[str, ...]
    couplings: Tuple[Coupling, ...] = ()


@dataclass(frozen=True)
class Interface:
    """The candidate minimal conjoining structure: ONE directed boundary link
    carrying a translation from the source state space into the destination's."""
    src_sid: str
    dst_sid: str
    translate: Callable[[int], int]

    def as_coupling(self) -> Coupling:
        tr = self.translate
        return Coupling(self.src_sid, self.dst_sid,
                        lambda s, d, _tr=tr: d + _tr(s))


def home_universe(universes: Iterable[Universe]) -> Dict[str, str]:
    """sid -> uid. Also the partition check: a merged system loses this map."""
    home: Dict[str, str] = {}
    for u in universes:
        for sid in u.members:
            home[sid] = u.uid
    return home


def conjoined_modulus_of(universes: Iterable[Universe]) -> Callable[[str], int]:
    """Each substrate stays bounded by its OWN universe."""
    table = {sid: u.modulus for u in universes for sid in u.members}
    return lambda sid: table[sid]


def collapsed_modulus_of(universes: Iterable[Universe]) -> Callable[[str], int]:
    """Every substrate re-bounded to a single shared state space."""
    m = max(u.modulus for u in universes)
    return lambda sid: m


def bound_violations(config: Config, universes: Iterable[Universe]) -> Tuple[str, ...]:
    """Substrates whose state has left the state space of their own universe."""
    out = []
    for u in universes:
        for sid in u.members:
            if not (0 <= config[sid].state < u.modulus):
                out.append(f"{sid}({u.uid}) state={config[sid].state} "
                           f"outside range(0,{u.modulus})")
    return tuple(out)


def restrict(couplings: Iterable[Coupling], members: Iterable[str]) -> Tuple[Coupling, ...]:
    """Couplings that write into `members` - used to step one universe alone."""
    members = frozenset(members)
    return tuple(c for c in couplings if c.dst in members)


def seed(universes: Iterable[Universe], values: Dict[str, int]) -> Config:
    return {sid: Substrate(sid, values[sid] % u.modulus)
            for u in universes for sid in u.members}
