"""EXP3: exp2 showed a state-gated topology only changes edges TOUCHING the
perturbed substrate. Two candidate primitives for changing relations that do
NOT touch it:

  (A) a mediating term the gate reads, in addition to the two endpoints
  (B) no new primitive at all - let the coupling of exp1 carry the change
      through time, and re-derive the pairwise topology afterwards
"""
from substrates.s0_substrate import Substrate
from substrates.s1_coupling import Coupling, run
from substrates.s2_topology import GatedTopology, edge_delta, ring_gate, split_delta
from substrates.s3_mediation import MediatedTopology, load_gated_ring, total_load

M = 12
BASE = {"a": 0, "b": 2, "c": 5, "d": 9}
WIDE, NARROW, THRESHOLD = 3, 1, 20


def config(overrides=None):
    vals = dict(BASE, **(overrides or {}))
    return {k: Substrate(k, v) for k, v in vals.items()}


def main():
    print("EXP3  relational change that does not touch the perturbed substrate")
    print("-" * 62)

    base = config()
    mediated = MediatedTopology(load_gated_ring(M, WIDE, NARROW, THRESHOLD))
    pairwise = GatedTopology(ring_gate(M, WIDE))

    print("  (A) mediated gate, no dynamics, single perturbation of a")
    print("      a   load   pairwise_non_incident   mediated_non_incident")
    pw_non = md_non = 0
    for s in range(M):
        pert = config({"a": s})
        _, pn = split_delta(edge_delta(pairwise.edge_set(base),
                                       pairwise.edge_set(pert)), "a")
        _, mn = split_delta(edge_delta(mediated.edge_set(base),
                                       mediated.edge_set(pert)), "a")
        pw_non += len(pn)
        md_non += len(mn)
        print(f"      {s:<3} {total_load(pert):<6} {len(pn):<23} {len(mn)}")
    print(f"      subtotal: pairwise={pw_non}  mediated={md_non}")
    print()

    # (B) pairwise gate only, but let couplings move state through time.
    couplings = (Coupling("a", "b", lambda s, d: d + s),
                 Coupling("b", "c", lambda s, d: d + s),
                 Coupling("c", "d", lambda s, d: d + s))
    mod = lambda sid: M
    print("  (B) pairwise gate + couplings, perturbation of a at t0")
    print("      steps   total_delta   incident   non_incident")
    prop = {}
    for k in range(4):
        u = run(config(), couplings, mod, k)
        p = run(config({"a": 6}), couplings, mod, k)
        delta = edge_delta(pairwise.edge_set(u), pairwise.edge_set(p))
        inc, non = split_delta(delta, "a")
        prop[k] = len(non)
        print(f"      {k:<7} {len(delta):<13} {len(inc):<10} {len(non)}")

    print()
    print(f"  RESULT pairwise_static_non_incident={pw_non} "
          f"mediated_non_incident={md_non} "
          f"propagated_non_incident_by_step={prop}")
    return {"pairwise_non_incident": pw_non, "mediated_non_incident": md_non,
            "propagated": prop}


if __name__ == "__main__":
    main()
