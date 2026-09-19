"""S0 - the smallest substrate.

A substrate here is two things and nothing more:
  - sid:   a label
  - state: a value

Whether both are needed is not assumed; exp0 measures it.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Substrate:
    sid: str
    state: int

    def with_state(self, state: int) -> "Substrate":
        """Return a substrate with the same label and a different value."""
        return Substrate(self.sid, state)


def population_by_state(subs):
    """How many substrates survive if the only distinguishing mark is state."""
    return frozenset(s.state for s in subs)


def population_by_identity(subs):
    """How many substrates survive if the distinguishing mark is the label."""
    return frozenset(s.sid for s in subs)


def merge(a: Substrate, b: Substrate, modulus: int) -> Substrate:
    """Contrast operation: two substrates in, ONE out. Identities are destroyed."""
    return Substrate(f"{a.sid}+{b.sid}", (a.state + b.state) % modulus)
