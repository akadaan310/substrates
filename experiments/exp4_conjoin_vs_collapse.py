"""EXP4: two bounded state spaces. What is the smallest structure that lets
them be conjoined without collapsing into one?

U1: three substrates over range(5)
U2: three substrates over range(7)

collapse  - re-bound every substrate to one shared modulus
conjoin   - keep both bounds; relate them through Interface(s), each a single
            directed boundary link carrying a translation between the spaces
"""
from substrates.s1_coupling import run, states
from substrates.s4_universe import (
    Interface, Universe, bound_violations, collapsed_modulus_of,
    conjoined_modulus_of, home_universe, restrict, seed,
)
from substrates.s0_substrate import Substrate
from substrates.s1_coupling import Coupling

STEPS = 6

U1 = Universe("U1", 5, ("a0", "a1", "a2"), (
    Coupling("a0", "a1", lambda s, d: d + s + 1),
    Coupling("a1", "a2", lambda s, d: d + s + 1),
))
U2 = Universe("U2", 7, ("b0", "b1", "b2"), (
    Coupling("b0", "b1", lambda s, d: d + s + 1),
    Coupling("b1", "b2", lambda s, d: d + s + 1),
))
UNIVERSES = (U1, U2)
SEED = {"a0": 1, "a1": 0, "a2": 3, "b0": 2, "b1": 6, "b2": 4}

FORWARD = Interface("a2", "b0", lambda s: s % 7)   # U1 space -> U2 space
REVERSE = Interface("b2", "a0", lambda s: s % 5)   # U2 space -> U1 space


def intra():
    return U1.couplings + U2.couplings


def trace(sids, config):
    return tuple(config[s].state for s in sids)


def main():
    print("EXP4  conjoining bounded state spaces without collapsing them")
    print("-" * 62)

    conj_mod = conjoined_modulus_of(UNIVERSES)
    coll_mod = collapsed_modulus_of(UNIVERSES)
    base = seed(UNIVERSES, SEED)
    print(f"  seed            : {states(base)}")
    print(f"  U1 bound=range(5) members={U1.members}")
    print(f"  U2 bound=range(7) members={U2.members}")
    print()

    # --- closure -------------------------------------------------------
    links = intra() + (FORWARD.as_coupling(), REVERSE.as_coupling())
    cv, kv = [], []
    for k in range(1, STEPS + 1):
        cv += list(bound_violations(run(base, links, conj_mod, k), UNIVERSES))
        kv += list(bound_violations(run(base, links, coll_mod, k), UNIVERSES))
    conj = run(base, links, conj_mod, STEPS)
    coll = run(base, links, coll_mod, STEPS)
    print(f"  after {STEPS} steps, conjoined : {states(conj)}")
    print(f"  after {STEPS} steps, collapsed : {states(coll)}")
    print(f"    own-bound violations over {STEPS} steps, conjoined = {len(cv)}")
    print(f"    own-bound violations over {STEPS} steps, collapsed = {len(kv)}")
    for v in kv:
        print(f"      step-wise: {v}")
    print()

    # --- partition -----------------------------------------------------
    conj_home = home_universe(UNIVERSES)
    collapsed_universe = Universe("U*", 7, U1.members + U2.members)
    coll_home = home_universe((collapsed_universe,))
    print(f"    distinct universes conjoined = {len(set(conj_home.values()))}")
    print(f"    distinct universes collapsed = {len(set(coll_home.values()))}")
    print()

    # --- separability: step U1 alone -----------------------------------
    only_u1 = restrict(links, U1.members)
    stepped = run(base, only_u1, conj_mod, 1)
    u2_frozen = trace(U2.members, stepped) == trace(U2.members, base)
    u1_moved = trace(U1.members, stepped) != trace(U1.members, base)
    print(f"  stepping U1's couplings alone: U1_changed={u1_moved} "
          f"U2_unchanged={u2_frozen}")
    print()

    # --- cross influence, by interface set -----------------------------
    print("  perturb one universe's seed, measure the other after "
          f"{STEPS} steps")
    print("    interfaces            U1->U2   U2->U1")
    for name, ifaces in (("none", ()),
                         ("forward only", (FORWARD,)),
                         ("forward+reverse", (FORWARD, REVERSE))):
        ls = intra() + tuple(i.as_coupling() for i in ifaces)
        ref = run(base, ls, conj_mod, STEPS)

        p1 = dict(SEED, a0=(SEED["a0"] + 1) % 5)
        out1 = run(seed(UNIVERSES, p1), ls, conj_mod, STEPS)
        u1_to_u2 = sum(1 for s in U2.members if out1[s].state != ref[s].state)

        p2 = dict(SEED, b1=(SEED["b1"] + 1) % 7)
        out2 = run(seed(UNIVERSES, p2), ls, conj_mod, STEPS)
        u2_to_u1 = sum(1 for s in U1.members if out2[s].state != ref[s].state)

        print(f"    {name:<21} {u1_to_u2:<8} {u2_to_u1}")
        if name == "forward only":
            fwd = (u1_to_u2, u2_to_u1)
        if name == "none":
            none_pair = (u1_to_u2, u2_to_u1)
        if name == "forward+reverse":
            both = (u1_to_u2, u2_to_u1)

    print()
    print(f"  RESULT violations_conjoined={len(cv)} violations_collapsed={len(kv)} "
          f"universes_conjoined={len(set(conj_home.values()))} "
          f"universes_collapsed={len(set(coll_home.values()))} "
          f"separable={u1_moved and u2_frozen} "
          f"influence_none={none_pair} influence_forward={fwd} "
          f"influence_both={both}")
    return {"violations_conjoined": len(cv), "violations_collapsed": len(kv),
            "separable": u1_moved and u2_frozen,
            "influence_none": none_pair, "influence_forward": fwd,
            "influence_both": both}


if __name__ == "__main__":
    main()
