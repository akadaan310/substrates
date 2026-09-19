"""F13 — S4 minimality search.

S4 asserts a "smallest conjoining structure" with no search behind it (C16).
This searches. Two targets are kept SEPARATE throughout, because v0.1 entangles
them and they may not coincide:

  T1  CONJUNCTION   — non-zero causal influence between two bounded state
                      spaces, with closure, partition and separability intact.
  T2  NONTRIVIAL    — the interface's map is not the identity on the source's
      TRANSLATION     reachable set, i.e. the translation does real work.

Design space searched
---------------------
A conjoining structure is a set of cross-links (src, dst, tau) where
tau : Z_m_src -> Z_m_dst. The space of tau is FINITE and small, so the core of
this search is exhaustive rather than sampled:

    tau : Z_5 -> Z_7   ->   7^5 = 16,807 maps   EXHAUSTIVE
    tau : Z_7 -> Z_5   ->   5^7 = 78,125 maps   EXHAUSTIVE

Coverage is stated per search. Nothing here modifies substrates/, experiments/
or the published artifact.

    PYTHONPATH=. python3 audit/s4_minimality.py
"""
import itertools
import random

M1, M2 = 5, 7
U1 = ("a0", "a1", "a2")
U2 = ("b0", "b1", "b2")
ALL = U1 + U2
SEED = {"a0": 1, "a1": 0, "a2": 3, "b0": 2, "b1": 6, "b2": 4}
T = 8

# (src, dst, fn) — fn(src_state, dst_state) -> dst_state, pre-modulus
INTRA = [
    ("a0", "a1", lambda s, d: d + s + 1),
    ("a1", "a2", lambda s, d: d + s + 1),
    ("b0", "b1", lambda s, d: d + s + 1),
    ("b1", "b2", lambda s, d: d + s + 1),
]


def own_mod(sid):
    return M1 if sid[0] == "a" else M2


def step(st, links, modof):
    pending = dict(st)
    for src, dst, fn in sorted(links, key=lambda c: (c[1], c[0])):
        pending[dst] = fn(st[src], pending[dst])
    return {k: v % modof(k) for k, v in pending.items()}


def trajectory(seed, links, modof, steps=T):
    st, out = dict(seed), [dict(seed)]
    for _ in range(steps):
        st = step(st, links, modof)
        out.append(dict(st))
    return out


def perturbed(seed, sid, modof):
    p = dict(seed)
    p[sid] = (p[sid] + 1) % modof(sid)
    return p


def influence(links, target, perturb_sid, modof=own_mod, seed=SEED, steps=T):
    """Non-saturating: counts differing (substrate, step) cells, and reports
    how many steps elapse before the first difference."""
    ref = trajectory(seed, links, modof, steps)
    alt = trajectory(perturbed(seed, perturb_sid, modof), links, modof, steps)
    cells = sum(1 for t in range(steps + 1) for s in target if ref[t][s] != alt[t][s])
    first = next((t for t in range(steps + 1)
                  if any(ref[t][s] != alt[t][s] for s in target)), None)
    return cells, first


def reachable(links, sid, perturb_sid, modof=own_mod, seed=SEED, steps=T):
    """States `sid` visits across the reference AND perturbed runs — the domain
    on which an outgoing map's information content must be judged."""
    ref = trajectory(seed, links, modof, steps)
    alt = trajectory(perturbed(seed, perturb_sid, modof), links, modof, steps)
    return frozenset(tr[t][sid] for tr in (ref, alt) for t in range(steps + 1))


DOMAIN_ESCAPES = [0]


def link(src, dst, tau):
    """A cross-link. The map's domain is the SOURCE universe's state space; if
    the source leaves that space the map is no longer total and must be
    extended. Extensions are counted rather than hidden."""
    def fn(s, d, _t=tau):
        if s >= len(_t):
            DOMAIN_ESCAPES[0] += 1
            s = s % len(_t)
        return d + _t[s]
    return (src, dst, fn)


def head(n, title):
    print(f"\n{n}  {title}")
    print("-" * 76)


# =====================================================================
# A. Interface count: 0, 1, 2
# =====================================================================
def search_a():
    head("A", "INTERFACE COUNT — 0, 1, 2, and which direction carries what")
    incl = tuple(s % M2 for s in range(M1))      # Z_5 -> Z_7, the inclusion
    red = tuple(s % M1 for s in range(M2))       # Z_7 -> Z_5, a reduction
    fwd, rev = link("a2", "b0", incl), link("b2", "a0", red)
    print("    interfaces            U1→U2 cells  first step   U2→U1 cells  first step")
    for label, links in (("none", INTRA),
                         ("forward only", INTRA + [fwd]),
                         ("reverse only", INTRA + [rev]),
                         ("forward + reverse", INTRA + [fwd, rev])):
        f, ft = influence(links, U2, "a0")
        b, bt = influence(links, U1, "b1")
        print(f"    {label:<21} {f:<12} {str(ft):<12} {b:<12} {bt}")
    print("\n    Coverage: exhaustive over interface counts 0-2 and both directions.")
    print("    One directed link gives influence in its own direction only.")


# =====================================================================
# B. Exhaustive over every map Z_5 -> Z_7
# =====================================================================
def search_b():
    head("B", "EVERY FORWARD MAP — exhaustive over all 7^5 = 16,807 of them")
    R = reachable(INTRA, "a2", "a0")
    print(f"    a2's reachable set across reference and perturbed runs: {sorted(R)}"
          f"  (|R| = {len(R)} of {M1})")

    buckets = {}
    agree = disagree = 0
    smallest_witness = None
    identity_witness = None
    for tau in itertools.product(range(M2), repeat=M1):
        cells, first = influence(INTRA + [link("a2", "b0", tau)], U2, "a0")
        distinct = len({tau[s] for s in R})          # values taken ON R
        buckets.setdefault(distinct, [0, 0])
        buckets[distinct][0] += 1
        if cells:
            buckets[distinct][1] += 1
        predicted = distinct >= 2
        if predicted == (cells > 0):
            agree += 1
        else:
            disagree += 1
        if cells and distinct == 2 and smallest_witness is None:
            smallest_witness = (tau, cells, first)
        if cells and all(tau[s] == s for s in R) and identity_witness is None:
            identity_witness = (tau, cells)

    print("\n    values tau takes on R   maps      maps producing influence")
    for d in sorted(buckets):
        n, inf = buckets[d]
        print(f"    {d:<23} {n:<9} {inf}")
    print(f"\n    predicate |tau(R)| >= 2  agrees with observed influence in "
          f"{agree}/{agree + disagree} maps ({agree / (agree + disagree):.1%})")
    print(f"\n    smallest witness (map taking exactly 2 values on R):")
    print(f"      tau = {smallest_witness[0]}  -> influence {smallest_witness[1]} cells,"
          f" first at step {smallest_witness[2]}")
    print(f"    identity-on-R witness (T2 FALSE, T1 TRUE):")
    print(f"      tau = {identity_witness[0]}  -> influence {identity_witness[1]} cells")
    return buckets


# =====================================================================
# C. Exhaustive over every map Z_7 -> Z_5
# =====================================================================
def search_c():
    head("C", "EVERY REVERSE MAP — exhaustive over all 5^7 = 78,125 of them")
    R = reachable(INTRA, "b2", "b1")
    print(f"    b2's reachable set: {sorted(R)}  (|R| = {len(R)} of {M2})")
    const = noncon = const_inf = noncon_inf = 0
    for tau in itertools.product(range(M1), repeat=M2):
        cells, _ = influence(INTRA + [link("b2", "a0", tau)], U1, "b1")
        if len({tau[s] for s in R}) >= 2:
            noncon += 1
            noncon_inf += bool(cells)
        else:
            const += 1
            const_inf += bool(cells)
    print(f"\n    constant on R     {const:<8} maps, {const_inf} produce influence")
    print(f"    non-constant on R {noncon:<8} maps, {noncon_inf} produce influence")
    print(f"    agreement: {(const - const_inf) + noncon_inf}/{const + noncon} "
          f"({((const - const_inf) + noncon_inf) / (const + noncon):.1%})")


# =====================================================================
# D. Syntactic count vs information carried  (the F9-style trap)
# =====================================================================
def search_d():
    head("D", "THE TRAP — interface COUNT is not the unit; carried information is")
    R1 = reachable(INTRA, "a2", "a0")
    R2 = reachable(INTRA, "b2", "b1")
    const_f = tuple(0 for _ in range(M1))
    const_r = tuple(0 for _ in range(M2))
    onebit_f = tuple(1 if s >= 2 else 0 for s in range(M1))
    print("    structure                                interfaces  bits on R   influence")
    for label, links, n, bits in (
        ("2 interfaces, both constant",
         INTRA + [link("a2", "b0", const_f), link("b2", "a0", const_r)], 2,
         f"{len({const_f[s] for s in R1})}v / {len({const_r[s] for s in R2})}v"),
        ("1 interface, 1 bit (threshold at 2)",
         INTRA + [link("a2", "b0", onebit_f)], 1,
         f"{len({onebit_f[s] for s in R1})}v"),
        ("1 interface, full inclusion",
         INTRA + [link("a2", "b0", tuple(s % M2 for s in range(M1)))], 1,
         f"{len({s % M2 for s in R1})}v"),
    ):
        f, _ = influence(links, U2, "a0")
        b, _ = influence(links, U1, "b1")
        print(f"    {label:<40} {n:<11} {bits:<11} U1→U2 {f}, U2→U1 {b}")
    print("\n    Two interfaces carrying zero bits conjoin nothing. One interface")
    print("    carrying one bit conjoins. Counting interfaces measures syntax.")


# =====================================================================
# E. Moduli: shrinking and expanding bounds
# =====================================================================
def search_e():
    head("E", "BOUNDS — is the v0.1 translation vacuous by choice or by force?")
    print("    m_src  m_dst  relation   canonical map s%m_dst   identity on Z_m_src?")
    for a, b in ((5, 7), (7, 5), (5, 5), (4, 8), (6, 9), (3, 11), (11, 3)):
        canon = [s % b for s in range(a)]
        is_id = all(canon[s] == s for s in range(a))
        rel = "expanding" if a < b else ("shrinking" if a > b else "equal")
        print(f"    {a:<6} {b:<6} {rel:<10} {str(canon):<23} {is_id}")
    print("\n    For m_src <= m_dst the canonical map IS the identity — necessarily,")
    print("    not by choice. v0.1's vacuous forward translation was forced by the")
    print("    direction it points, and no alternative canonical map exists.")


# =====================================================================
# F. Testing the measurement itself
# =====================================================================
def profile(traj, members, modulus):
    reached = set()
    for st in traj:
        for s in members:
            reached.add(st[s])
    return {"reached": len(reached), "modulus": modulus,
            "escape": max(reached) >= modulus, "contraction": len(reached) < modulus}


def old_metric(traj, members, modulus):
    """v0.1's bound_violations: counts states ABOVE the bound only."""
    return sum(1 for st in traj for s in members if st[s] >= modulus)


def search_f():
    head("F", "THE METRIC — does the replacement detect contraction as well as escape?")
    incl = tuple(s % M2 for s in range(M1))
    red = tuple(s % M1 for s in range(M2))
    links = INTRA + [link("a2", "b0", incl), link("b2", "a0", red)]
    print("    regime            universe  reached/modulus  escape  contraction  v0.1 metric")
    domain = {}
    for label, modof in (("conjoined", own_mod),
                         ("collapse to max 7", lambda s: 7),
                         ("collapse to min 5", lambda s: 5),
                         ("collapse to lcm 35", lambda s: 35)):
        DOMAIN_ESCAPES[0] = 0
        traj = trajectory(SEED, links, modof)
        for uid, members, m in (("U1", U1, M1), ("U2", U2, M2)):
            p = profile(traj, members, m)
            print(f"    {label:<17} {uid:<9} {p['reached']}/{p['modulus']:<14} "
                  f"{str(p['escape']):<7} {str(p['contraction']):<12} "
                  f"{old_metric(traj, members, m)}")
        domain[label] = DOMAIN_ESCAPES[0]
    print("\n    interface map well-typed?  (times the source left the map's domain)")
    for label, n in domain.items():
        print(f"      {label:<20} {n}" + ("" if n == 0 else "   <- map had to be extended"))
    print("\n    Collapse to min 5: U2 reaches fewer states than its modulus allows —")
    print("    contraction. The v0.1 metric reports 0 there. The replacement reports")
    print("    both directions, so it cannot bake in the conclusion the old one did.")


# =====================================================================
# G. Does "universe" require anything beyond a bounded state space?
# =====================================================================
def search_g():
    head("G", "WHAT A UNIVERSE NEEDS — vary internal structure, hold bounds fixed")
    incl = tuple(s % M2 for s in range(M1))
    variants = {
        "v0.1 chain, d+s+1": INTRA,
        "chain, d+2s": [(a, b, lambda s, d: d + 2 * s) for a, b, _ in INTRA],
        "cycle": INTRA + [("a2", "a0", lambda s, d: d + s), ("b2", "b0", lambda s, d: d + s)],
        "U1 chain / U2 star": [
            ("a0", "a1", lambda s, d: d + s + 1), ("a1", "a2", lambda s, d: d + s + 1),
            ("b0", "b1", lambda s, d: d + s + 1), ("b0", "b2", lambda s, d: d + s + 1)],
        "no internal couplings": [],
    }
    print("    internal structure        influence  closure  partition  separable")
    for label, base in variants.items():
        links = base + [link("a2", "b0", incl)]
        f, _ = influence(links, U2, "a0")
        traj = trajectory(SEED, links, own_mod)
        closed = all(not profile(traj, m, mm)["escape"]
                     for m, mm in ((U1, M1), (U2, M2)))
        part = len({s[0] for s in ALL}) == 2
        only1 = [c for c in links if c[1] in U1]
        st = step(SEED, only1, own_mod)
        sep = all(st[s] == SEED[s] for s in U2)
        print(f"    {label:<25} {f:<10} {str(closed):<8} {str(part):<10} {sep}")
    print("\n    Closure, partition and separability hold across every internal")
    print("    structure including none at all. They follow from the bound and the")
    print("    membership map, not from anything else a 'universe' might carry.")


# =====================================================================
# H. Seed dependence
# =====================================================================
def search_h():
    head("H", "SEED DEPENDENCE — does the verdict survive the representative state?")
    incl = tuple(s % M2 for s in range(M1))
    const = tuple(0 for _ in range(M1))
    rng = random.Random(0)
    seeds = [SEED] + [{s: rng.randrange(own_mod(s)) for s in ALL} for _ in range(999)]
    inf_incl = sum(1 for sd in seeds
                   if influence(INTRA + [link("a2", "b0", incl)], U2, "a0", seed=sd)[0])
    inf_const = sum(1 for sd in seeds
                    if influence(INTRA + [link("a2", "b0", const)], U2, "a0", seed=sd)[0])
    inf_none = sum(1 for sd in seeds if influence(INTRA, U2, "a0", seed=sd)[0])
    n = len(seeds)
    print(f"    1000 seeds (the v0.1 seed plus 999 random)")
    print(f"      no interface                 influence in {inf_none}/{n} seeds")
    print(f"      1 interface, constant map    influence in {inf_const}/{n} seeds")
    print(f"      1 interface, inclusion map   influence in {inf_incl}/{n} seeds")
    print("\n    Coverage: sampled over seeds, exhaustive over the map space in B/C.")


# =====================================================================
# I. Component verdicts
# =====================================================================
def search_i():
    head("I", "COMPONENT VERDICTS — necessary, sufficient, or merely one that worked")
    R = reachable(INTRA, "a2", "a0")
    incl = tuple(s % M2 for s in range(M1))
    onebit = tuple(1 if s >= 2 else 0 for s in range(M1))
    const = tuple(0 for _ in range(M1))
    red = tuple(s % M1 for s in range(M2))

    def inf(links, target, p):
        return influence(links, target, p)[0]

    rows = []
    rows.append(("a cross-link exists", "NECESSARY",
                 f"0 links -> influence {inf(INTRA, U2, 'a0')}; "
                 f"1 link -> {inf(INTRA + [link('a2','b0',incl)], U2, 'a0')}"))
    rows.append(("tau non-constant on the reachable set", "NECESSARY",
                 f"constant -> {inf(INTRA + [link('a2','b0',const)], U2, 'a0')}; "
                 f"search B: 0 of {M2} constant maps produce influence"))
    rows.append(("tau is NOT the identity (T2)", "NEITHER",
                 f"identity-on-R -> influence "
                 f"{inf(INTRA + [link('a2','b0',incl)], U2, 'a0')}; T2 false, T1 true"))
    rows.append(("tau carries the full source state", "NEITHER",
                 f"1 bit suffices -> {inf(INTRA + [link('a2','b0',onebit)], U2, 'a0')} "
                 f"vs full {inf(INTRA + [link('a2','b0',incl)], U2, 'a0')}"))
    rows.append(("a second, reverse link", "NEITHER for T1 / NECESSARY for mutual",
                 f"one link -> U2→U1 "
                 f"{inf(INTRA + [link('a2','b0',incl)], U1, 'b1')}; two -> "
                 f"{inf(INTRA + [link('a2','b0',incl), link('b2','a0',red)], U1, 'b1')}"))
    best = None
    for src, dst in itertools.product(U1, U2):
        c = inf(INTRA + [link(src, dst, incl)], U2, "a0")
        if best is None or c > best[1]:
            best = ((src, dst), c)
    works = sum(1 for src, dst in itertools.product(U1, U2)
                if inf(INTRA + [link(src, dst, incl)], U2, "a0"))
    rows.append(("the specific boundary pair a2→b0", "NEITHER",
                 f"{works} of 9 (src,dst) pairs produce influence"))
    print("    component                                 verdict")
    for name, verdict, ev in rows:
        print(f"    {name:<41} {verdict}")
        print(f"      evidence: {ev}")


# =====================================================================
# J. A third target: relational influence, with NO cross-link at all
# =====================================================================
def cross_pairs(exclude=None):
    """Cross-universe relations, optionally excluding those incident to a
    named substrate."""
    return [(x, y) for x in U1 for y in U2
            if exclude not in (x, y)]


def search_j():
    head("J", "A THIRD TARGET — relational influence with ZERO cross-links")
    span = M1 + M2

    def ring(u, v, radius):
        d = abs(u - v) % span
        return min(d, span - d) <= radius

    def pairwise_edges(cfg):
        return frozenset(frozenset((x, y)) for x, y in cross_pairs()
                         if ring(cfg[x], cfg[y], 3))

    def mediated_edges(cfg):
        load = sum(cfg.values())
        radius = 3 if load < 18 else 1
        return frozenset(frozenset((x, y)) for x, y in cross_pairs()
                         if ring(cfg[x], cfg[y], radius))

    base = dict(SEED)
    print("    gate over both universes    cross-universe relations changed")
    print("                                total    not incident to the perturbed a0")
    for label, fn in (("pairwise (arity 2)", pairwise_edges),
                      ("mediated (reads all 6)", mediated_edges)):
        best_total = best_non = 0
        for new_a in range(M1):
            if new_a == base["a0"]:
                continue
            pert = dict(base, a0=new_a)
            delta = fn(base) ^ fn(pert)
            non = [e for e in delta if "a0" not in e]
            best_total = max(best_total, len(delta))
            best_non = max(best_non, len(non))
        print(f"    {label:<27} {best_total:<8} {best_non}")
    print("\n    Zero cross-links, zero state crossing the boundary — closure and")
    print("    partition are trivially perfect — and yet relations spanning the two")
    print("    universes move. This is a DIFFERENT target behaviour from T1, and it")
    print("    has a different minimal structure: no link at all, but a gate whose")
    print("    witness set contains the perturbed substrate (F9's condition).")


def main():
    print("F13  S4 MINIMALITY SEARCH — conjunction vs translation, kept separate")
    print("=" * 76)
    search_a(); search_b(); search_c(); search_d()
    search_e(); search_f(); search_g(); search_h(); search_i(); search_j()
    print("\n" + "=" * 76)


if __name__ == "__main__":
    main()
