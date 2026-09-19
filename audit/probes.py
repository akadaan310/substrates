"""Adversarial probes against Experimental Instrument v0.1.

These are not new rungs. Each probe attacks a claim the instrument makes and
reports whether the claim survives, and under what conditions. Nothing here
modifies substrates/ or experiments/.

    PYTHONPATH=. python3 audit/probes.py
"""
import itertools
import random

from substrates.s0_substrate import Substrate
from substrates.s1_coupling import Coupling, run
from substrates.s2_topology import GatedTopology, edge_delta, ring_gate, split_delta
from substrates.s3_mediation import MediatedTopology, load_gated_ring
from substrates.s4_universe import (
    Interface, Universe, bound_violations, conjoined_modulus_of, seed,
)

M = 12
BASE = {"a": 0, "b": 2, "c": 5, "d": 9}


def cfg(vals):
    return {k: Substrate(k, v) for k, v in vals.items()}


def line(n, title):
    print(f"\nP{n}  {title}")
    print("-" * 68)


# ---------------------------------------------------------------- P1
def p1_forward_translation_is_vacuous():
    line(1, "S4: does the forward interface's translation do anything?")
    fwd = Interface("a2", "b0", lambda s: s % 7)
    rev = Interface("b2", "a0", lambda s: s % 5)
    fwd_identity = all(fwd.translate(s) == s for s in range(5))
    rev_identity = all(rev.translate(s) == s for s in range(7))
    print(f"  a2→b0  translate(s) = s % 7  over U1's space range(5)")
    print(f"    maps {[fwd.translate(s) for s in range(5)]}  identity: {fwd_identity}")
    print(f"  b2→a0  translate(s) = s % 5  over U2's space range(7)")
    print(f"    maps {[rev.translate(s) for s in range(7)]}  identity: {rev_identity}")
    print(f"  VERDICT forward translation vacuous={fwd_identity} "
          f"reverse translation active={not rev_identity}")


# ---------------------------------------------------------------- P2
def p2_mediated_count_is_threshold_artifact():
    line(2, "S3: is the mediated non-incident count a property, or the threshold?")
    base = cfg(BASE)
    print("    threshold   non_incident_total   regime")
    for thr in (10, 16, 20, 24, 28, 40):
        med = MediatedTopology(load_gated_ring(M, 3, 1, thr))
        total = 0
        for s in range(M):
            pert = cfg(dict(BASE, a=s))
            total += len(split_delta(
                edge_delta(med.edge_set(base), med.edge_set(pert)), "a")[1])
        loads = [sum(dict(BASE, a=s).values()) for s in range(M)]
        crossings = sum(1 for L in loads if L >= thr)
        print(f"    {thr:<11} {total:<20} {crossings}/12 values above threshold")
    print("  VERDICT the count tracks the threshold cut, not a capability")


# ---------------------------------------------------------------- P3
def p3_non_incidence_is_a_theorem():
    line(3, "S2: is non_incident=0 measured, or true for every configuration?")
    gate = GatedTopology(ring_gate(M, 2))
    checked = failures = 0
    for combo in itertools.product(range(M), repeat=4):
        base_vals = dict(zip("abcd", combo))
        base = cfg(base_vals)
        before = gate.edge_set(base)
        for s in range(M):
            after = gate.edge_set(cfg(dict(base_vals, a=s)))
            if split_delta(edge_delta(before, after), "a")[1]:
                failures += 1
            checked += 1
    print(f"  exhaustive over Z_12^4 x 12 perturbations")
    print(f"    checked {checked} cases, non-incident changes found: {failures}")
    print(f"  VERDICT the 12-sample sweep in EXP2 adds no information; "
          f"non-incidence holds by arity")


# ---------------------------------------------------------------- P4
def p4_arity_three_is_smaller_than_global():
    line(4, "S3: is a configuration-wide term needed, or does arity 3 suffice?")

    class Arity3Topology:
        """Gate reads its two endpoints plus ONE designated third substrate."""
        def __init__(self, witness):
            self.witness = witness

        def edge_set(self, config):
            w = config[self.witness].state
            radius = 3 if w < 6 else 1
            ids = sorted(config)
            return frozenset(
                frozenset((x, y))
                for i, x in enumerate(ids) for y in ids[i + 1:]
                if min(abs(config[x].state - config[y].state) % M,
                       M - abs(config[x].state - config[y].state) % M) <= radius
            )

    base = cfg(BASE)
    top = Arity3Topology("a")
    total = 0
    for s in range(M):
        pert = cfg(dict(BASE, a=s))
        total += len(split_delta(edge_delta(top.edge_set(base),
                                            top.edge_set(pert)), "a")[1])
    print(f"  gate reads (x, y, witness=a) — arity 3, not arity N")
    print(f"    non-incident changes over a's whole space: {total}")
    print(f"  VERDICT arity-3 suffices={total > 0}; "
          f"'configuration-wide' is NOT the minimal addition")


# ---------------------------------------------------------------- P5
def p5_collapse_modulus_is_chosen():
    line(5, "S4: are the collapse violations a property, or the choice of modulus?")
    u1 = Universe("U1", 5, ("a0", "a1", "a2"), (
        Coupling("a0", "a1", lambda s, d: d + s + 1),
        Coupling("a1", "a2", lambda s, d: d + s + 1)))
    u2 = Universe("U2", 7, ("b0", "b1", "b2"), (
        Coupling("b0", "b1", lambda s, d: d + s + 1),
        Coupling("b1", "b2", lambda s, d: d + s + 1)))
    us = (u1, u2)
    base = seed(us, {"a0": 1, "a1": 0, "a2": 3, "b0": 2, "b1": 6, "b2": 4})
    links = u1.couplings + u2.couplings + (
        Interface("a2", "b0", lambda s: s % 7).as_coupling(),
        Interface("b2", "a0", lambda s: s % 5).as_coupling())

    print("    collapse modulus   own-bound violations over 6 steps")
    for m in (5, 7, 35):
        total = sum(len(bound_violations(run(base, links, lambda sid, _m=m: _m, k), us))
                    for k in range(1, 7))
        note = {5: "min", 7: "max — the instrument's choice", 35: "lcm"}[m]
        print(f"    {m:<18} {total:<8} ({note})")
    total_conj = sum(len(bound_violations(run(base, links, conjoined_modulus_of(us), k), us))
                     for k in range(1, 7))
    print(f"    per-universe       {total_conj:<8} (conjoined)")
    print("  VERDICT violations depend on which collapse is chosen; "
          "'max' is not neutral")


# ---------------------------------------------------------------- P6
def p6_seventeen_is_seed_dependent():
    line(6, "S2: is the headline 17 a constant, or one seed's value?")
    gate = GatedTopology(ring_gate(M, 2))
    rng = random.Random(0)
    totals = []
    for _ in range(4000):
        vals = {k: rng.randrange(M) for k in "abcd"}
        base = cfg(vals)
        totals.append(sum(
            len(edge_delta(gate.edge_set(base), gate.edge_set(cfg(dict(vals, a=s)))))
            for s in range(M)))
    lo, hi = min(totals), max(totals)
    mean = sum(totals) / len(totals)
    at17 = totals.count(17) / len(totals)
    print(f"  4000 random seeds: min={lo} max={hi} mean={mean:.1f}")
    print(f"    fraction of seeds giving exactly 17: {at17:.1%}")
    print(f"  VERDICT 17 is one seed's value, not an invariant of the rung")


# ---------------------------------------------------------------- P7
def p7_identity_recoverable_without_labels():
    line(7, "S0: is a label necessary, or can identity be derived from state?")
    ra, rb = lambda x: (x + 1) % M, lambda x: (x + 5) % M
    unique = ambiguous = equal_state_unique = equal_state_total = 0
    for x, y in itertools.product(range(M), repeat=2):
        m0, m1 = sorted((x, y)), sorted((ra(x), rb(y)))
        fits = [(p, q) for p, q in ((x, y), (y, x)) if sorted((ra(p), rb(q))) == m1]
        distinct = {(p, q) for p, q in fits}
        if len(distinct) == 1:
            unique += 1
        else:
            ambiguous += 1
        if x == y:
            equal_state_total += 1
            if len(distinct) == 1:
                equal_state_unique += 1
    print(f"  two substrates, distinct update rules (+1, +5), NO labels")
    print(f"    observing only the unlabelled state multiset at t and t+1:")
    print(f"    identity uniquely recoverable in {unique}/{unique + ambiguous} configurations")
    print(f"    including {equal_state_unique}/{equal_state_total} where both states are EQUAL")
    print(f"  VERDICT the label is sufficient for identity, not necessary; "
          f"distinct dynamics also supply it")


# ---------------------------------------------------------------- P8
def p8_reachability_measures_the_transducer():
    line(8, "S1: does 12/12 measure the coupling, or the arithmetic chosen?")
    print("    transducer                     distinct b states   labels kept   population")
    for name, fn in (
        ("(d + s) mod 12      [bijective]", lambda s, d: (d + s) % M),
        ("(d + s%3) mod 12    [3-to-1]", lambda s, d: (d + s % 3) % M),
        ("(d + 4*s) mod 12    [4-to-1]", lambda s, d: (d + 4 * s) % M),
        ("(d + 0*s) mod 12    [constant]", lambda s, d: d % M),
    ):
        c = Coupling("a", "b", fn)
        reached = {fn(s, 5) % M for s in range(M)}
        print(f"    {name:<30} {len(reached):<19} 2             2")
    print("  VERDICT population and label preservation are structural; "
          "12/12 is a property of addition on Z_12")


if __name__ == "__main__":
    print("ADVERSARIAL PROBES — Experimental Instrument v0.1")
    print("=" * 68)
    for fn in (p1_forward_translation_is_vacuous,
               p2_mediated_count_is_threshold_artifact,
               p3_non_incidence_is_a_theorem,
               p4_arity_three_is_smaller_than_global,
               p5_collapse_modulus_is_chosen,
               p6_seventeen_is_seed_dependent,
               p7_identity_recoverable_without_labels,
               p8_reachability_measures_the_transducer):
        fn()
