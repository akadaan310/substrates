"""F9 — gate-arity sweep, 2 → N.

Tests S3's minimality claim. v0.1 asserted that a configuration-wide term is
the smallest addition that lets a perturbation of `a` change a relation `a` is
not part of. The audit's P4 showed arity 3 suffices. This asks the harder
question: is arity 2 IMPOSSIBLE, and under exactly which assumptions?

Model under test
----------------
Substrates carry a label and a state in Z_M. A topology assigns to each
unordered pair {x,y} a WITNESS SET W(x,y) with {x,y} subset-of W(x,y), and a gate
    adj(x,y) = g( states of W(x,y), in a fixed order )
The gate's ARITY is |W(x,y)|. Arity 2 means W(x,y) = {x,y} exactly, which is
the v0.1 pairwise gate.

A relation is NON-INCIDENT to `a` when a is not in {x,y}.

    PYTHONPATH=. python3 audit/arity_sweep.py
"""
import itertools
import random

IDS4 = ("a", "b", "c", "d")
PERTURBED = "a"


def non_incident(ids, perturbed=PERTURBED):
    rest = [s for s in ids if s != perturbed]
    return [tuple(p) for p in itertools.combinations(rest, 2)]


def bitgate(mask, M):
    """A gate as a bitmask: one output bit per input tuple, base-M indexed.
    Enumerating masks enumerates the ENTIRE space of boolean gates of that arity."""
    def g(key):
        idx = 0
        for v in key:
            idx = idx * M + v
        return (mask >> idx) & 1
    return g


def head(title):
    print("\n" + title)
    print("-" * 74)


# =====================================================================
# 1. Arity 2 — exhaustive over the whole gate space
# =====================================================================
def arity2_exhaustive(M, ids=IDS4):
    """No reduction, no shortcut: every gate, every configuration, every
    perturbation, every non-incident pair."""
    pairs = non_incident(ids)
    ngates = 1 << (M * M)
    checked = flips = same_input = 0
    for mask in range(ngates):
        g = bitgate(mask, M)
        for combo in itertools.product(range(M), repeat=len(ids)):
            cfg = dict(zip(ids, combo))
            for new_a in range(M):
                if new_a == cfg[PERTURBED]:
                    continue
                pert = dict(cfg, a=new_a)
                for x, y in pairs:
                    checked += 1
                    if (cfg[x], cfg[y]) == (pert[x], pert[y]):
                        same_input += 1
                    if g((cfg[x], cfg[y])) != g((pert[x], pert[y])):
                        flips += 1
    return ngates, checked, flips, same_input


def arity2_sampled(M, n_gates, ids=IDS4, rng=None):
    """Same check where the gate space is too large to enumerate."""
    rng = rng or random.Random(0)
    pairs = non_incident(ids)
    span = M * M
    checked = flips = 0
    for _ in range(n_gates):
        mask = rng.getrandbits(span)
        g = bitgate(mask, M)
        for _ in range(40):
            cfg = {s: rng.randrange(M) for s in ids}
            new_a = rng.randrange(M)
            if new_a == cfg[PERTURBED]:
                continue
            pert = dict(cfg, a=new_a)
            for x, y in pairs:
                checked += 1
                if g((cfg[x], cfg[y])) != g((pert[x], pert[y])):
                    flips += 1
    return checked, flips


def part1():
    head("1  ARITY 2 — can any gate whatsoever move a non-incident relation?")
    print("    M   gate space      coverage     checks        flips   gate input unchanged")
    total_gates = 0
    for M in (2, 3):
        ngates, checked, flips, same = arity2_exhaustive(M)
        total_gates += ngates
        print(f"    {M}   2^{M*M:<3} = {ngates:<7} exhaustive   {checked:<13,} {flips:<7} {same:,}/{checked:,}")
    rng = random.Random(0)
    for M, n in ((4, 20000), (5, 20000), (12, 20000)):
        checked, flips = arity2_sampled(M, n, rng=rng)
        print(f"    {M:<3} 2^{M*M:<3}           sampled {n:<5,} {checked:<13,} {flips}")
    print(f"\n    Exhaustive at M=2 and M=3 covers {total_gates} gates — the COMPLETE")
    print("    space of boolean arity-2 gates at those moduli, against every")
    print("    configuration and every perturbation. Zero flips, everywhere.")
    return total_gates


# =====================================================================
# 2. Arity 3 — possibility, and whether `a` must be the witness
# =====================================================================
def arity3_exhaustive(M, witness, ids=IDS4, target=("c", "d")):
    """Exhaustive over all arity-3 gates for one witness set (x, y, witness)."""
    x, y = target
    order = (x, y, witness)
    ngates = 1 << (M ** 3)
    gates_that_can = 0
    configs_that_flip = 0
    config_total = 0
    max_flips_one_gate = 0
    for mask in range(ngates):
        g = bitgate(mask, M)
        flips_here = 0
        for combo in itertools.product(range(M), repeat=len(ids)):
            cfg = dict(zip(ids, combo))
            for new_a in range(M):
                if new_a == cfg[PERTURBED]:
                    continue
                pert = dict(cfg, a=new_a)
                if mask == 0:
                    config_total += 1
                if g(tuple(cfg[s] for s in order)) != g(tuple(pert[s] for s in order)):
                    flips_here += 1
        if flips_here:
            gates_that_can += 1
            configs_that_flip = max(configs_that_flip, flips_here)
        max_flips_one_gate = max(max_flips_one_gate, flips_here)
    return ngates, gates_that_can, max_flips_one_gate, config_total


def part2():
    head("2  ARITY 3 — is arity enough, or must the perturbed substrate be read?")
    M = 2
    print(f"    M={M}, substrates {IDS4}, target non-incident relation {{c,d}}")
    print("\n    witness set      a in W?   gate space   gates admitting a flip   max flips/gate")
    for w in ("a", "b"):
        ngates, can, mx, ctot = arity3_exhaustive(M, w)
        print(f"    (c, d, {w})        {'yes' if w == PERTURBED else 'no ':<9} 2^{M**3:<2} = {ngates:<5} "
              f"{can:<24} {mx}")
    print("\n    Arity is not the operative condition. (c,d,b) is arity 3 and moves")
    print("    nothing: b's state does not change when a is perturbed.")


# =====================================================================
# 3. The actual condition, stated as a predicate and checked
# =====================================================================
def part3():
    head("3  THE CONDITION — flips occur exactly when a is inside the witness set")
    M = 2
    ids = IDS4
    agree = disagree = 0
    rows = []
    for k in (2, 3, 4):
        rest = [s for s in ids if s not in ("c", "d")]
        for extra in itertools.combinations(rest, k - 2):
            W = ("c", "d") + extra
            ngates = 1 << (M ** k)
            can = 0
            for mask in range(ngates):
                g = bitgate(mask, M)
                found = False
                for combo in itertools.product(range(M), repeat=len(ids)):
                    cfg = dict(zip(ids, combo))
                    for new_a in range(M):
                        if new_a == cfg[PERTURBED]:
                            continue
                        pert = dict(cfg, a=new_a)
                        if g(tuple(cfg[s] for s in W)) != g(tuple(pert[s] for s in W)):
                            found = True
                            break
                    if found:
                        break
                if found:
                    can += 1
            predicted = PERTURBED in W
            observed = can > 0
            (agree if predicted == observed else disagree).__class__  # no-op guard
            if predicted == observed:
                agree += 1
            else:
                disagree += 1
            rows.append((k, W, predicted, can, ngates))
    print("    arity  witness set      a in W?   gates admitting a flip / total")
    for k, W, pred, can, ngates in rows:
        print(f"    {k:<6} {str(W):<16} {'yes' if pred else 'no ':<9} {can} / {ngates}")
    print(f"\n    predicate 'a in W(x,y)' agrees with observation in {agree}/{agree + disagree} witness sets")
    return agree, disagree


# =====================================================================
# 4. How many non-incident relations can move at once
# =====================================================================
def part4():
    head("4  CAPACITY — non-incident relations movable in a single perturbation")
    M = 2
    ids = IDS4
    pairs = non_incident(ids)
    print(f"    substrates {ids}, non-incident relations {pairs}")
    print("\n    arity  witness rule             max simultaneous non-incident changes")
    for k, rule, label in (
        (2, lambda x, y: (x, y), "W(x,y) = (x,y)"),
        (3, lambda x, y: (x, y, "a"), "W(x,y) = (x,y,a)"),
        (3, lambda x, y: (x, y, "b"), "W(x,y) = (x,y,b)"),
        (4, lambda x, y: (x, y, "a", "b"), "W(x,y) = (x,y,a,b)"),
    ):
        ngates = 1 << (M ** k)
        best = 0
        for mask in range(ngates):
            g = bitgate(mask, M)
            for combo in itertools.product(range(M), repeat=len(ids)):
                cfg = dict(zip(ids, combo))
                for new_a in range(M):
                    if new_a == cfg[PERTURBED]:
                        continue
                    pert = dict(cfg, a=new_a)
                    n = 0
                    for x, y in pairs:
                        W = rule(x, y)
                        if g(tuple(cfg[s] for s in W)) != g(tuple(pert[s] for s in W)):
                            n += 1
                    best = max(best, n)
        print(f"    {k:<6} {label:<24} {best} of {len(pairs)}")


# =====================================================================
# 5. Does the result depend on topology, gate, or seed?
# =====================================================================
def part5():
    head("5  DEPENDENCE — topology, gate function, seed")
    M = 2

    print("  (a) topology: number of substrates N")
    print("      N   non-incident relations   arity-2 flips   arity-3 (witness a) flips")
    for N in (3, 4, 5):
        ids = tuple("abcdef"[:N])
        pairs = non_incident(ids)
        res = {}
        for k, rule in ((2, lambda x, y: (x, y)), (3, lambda x, y: (x, y, "a"))):
            ngates = 1 << (M ** k)
            total = 0
            for mask in range(ngates):
                g = bitgate(mask, M)
                for combo in itertools.product(range(M), repeat=N):
                    cfg = dict(zip(ids, combo))
                    for new_a in range(M):
                        if new_a == cfg[PERTURBED]:
                            continue
                        pert = dict(cfg, a=new_a)
                        for x, y in pairs:
                            W = rule(x, y)
                            if g(tuple(cfg[s] for s in W)) != g(tuple(pert[s] for s in W)):
                                total += 1
            res[k] = total
        print(f"      {N}   {len(pairs):<24} {res[2]:<15} {res[3]}")

    print("\n  (b) gate function: fraction of arity-3 gates (witness a) that can move {c,d}")
    for M2 in (2, 3):
        ngates = 1 << (M2 ** 3) if M2 == 2 else None
        if ngates is None:
            rng = random.Random(1)
            span, trials, can = M2 ** 3, 4000, 0
            for _ in range(trials):
                mask = rng.getrandbits(span)
                g = bitgate(mask, M2)
                found = False
                for combo in itertools.product(range(M2), repeat=4):
                    cfg = dict(zip(IDS4, combo))
                    for new_a in range(M2):
                        if new_a == cfg[PERTURBED]:
                            continue
                        pert = dict(cfg, a=new_a)
                        if g((cfg["c"], cfg["d"], cfg["a"])) != g((pert["c"], pert["d"], pert["a"])):
                            found = True
                            break
                    if found:
                        break
                can += found
            print(f"      M={M2}: {can}/{trials} sampled gates  ({can / trials:.1%})")
        else:
            _, can, _, _ = arity3_exhaustive(M2, "a")
            print(f"      M={M2}: {can}/{ngates} gates exhaustively  ({can / ngates:.1%})")

    print("\n  (c) seed: for ONE fixed arity-3 gate (parity of c,d,a), which seeds flip {c,d}?")
    g = lambda key: (key[0] + key[1] + key[2]) % 2
    flip = total = 0
    for combo in itertools.product(range(2), repeat=4):
        cfg = dict(zip(IDS4, combo))
        for new_a in range(2):
            if new_a == cfg[PERTURBED]:
                continue
            pert = dict(cfg, a=new_a)
            total += 1
            if g((cfg["c"], cfg["d"], cfg["a"])) != g((pert["c"], pert["d"], pert["a"])):
                flip += 1
    print(f"      {flip}/{total} (configuration, perturbation) cases flip — "
          f"{'seed-independent' if flip == total else 'seed-dependent'}")


# =====================================================================
# 6. Apparent arity vs effective arity
# =====================================================================
def part6():
    head("6  APPARENT vs EFFECTIVE ARITY — where the impossibility stops holding")
    M, ids = 3, IDS4
    pairs = non_incident(ids)

    def raw_gate(cfg, x, y):
        """Genuinely arity 2: reads two raw states."""
        return (cfg[x] + cfg[y]) % 2

    def derived_gate(cfg, x, y):
        """LOOKS arity 2 — same two-argument signature — but each argument is a
        configuration-derived quantity, so its information set is all of it."""
        mean = sum(cfg.values()) / len(cfg)
        rx, ry = cfg[x] >= mean, cfg[y] >= mean
        return int(rx == ry)

    print("    gate                              signature   information set      flips")
    for label, fn, info in (("(s_x + s_y) mod 2", raw_gate, "{x, y}"),
                            ("rank(x) == rank(y), rank vs mean", derived_gate, "all substrates")):
        flips = 0
        for combo in itertools.product(range(M), repeat=len(ids)):
            cfg = dict(zip(ids, combo))
            for new_a in range(M):
                if new_a == cfg[PERTURBED]:
                    continue
                pert = dict(cfg, a=new_a)
                for x, y in pairs:
                    if fn(cfg, x, y) != fn(pert, x, y):
                        flips += 1
        print(f"    {label:<33} 2 args      {info:<20} {flips}")
    print("\n    Both take two arguments. Only the first is arity 2 under this model.")
    print("    The impossibility is a statement about the INFORMATION SET, not the")
    print("    number of formal parameters — a gate reading configuration-derived")
    print("    arguments is arity N wearing an arity-2 signature.")


def main():
    print("F9  GATE-ARITY SWEEP 2 → N — testing S3's minimality claim")
    print("=" * 74)
    part1(); part2(); part3(); part4(); part5(); part6()
    print("\n" + "=" * 74)
    print("RESULT  minimum arity at which a non-incident change is possible: 3")
    print("        and arity 3 alone is NOT sufficient — the perturbed substrate")
    print("        must be inside the witness set of the relation that moves.")


if __name__ == "__main__":
    main()
