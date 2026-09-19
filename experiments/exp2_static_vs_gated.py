"""EXP2: can changing one substrate's state change the neighbourhood
relations of another?

Two topologies over the same four substrates:
  static - edges are stored
  gated  - edges are derived from the endpoints' states
"""
from substrates.s0_substrate import Substrate
from substrates.s2_topology import (
    GatedTopology, StaticTopology, edge_delta, ring_gate, split_delta,
)

M, RADIUS = 12, 2
BASE = {"a": 0, "b": 2, "c": 5, "d": 9}


def config(overrides=None):
    vals = dict(BASE, **(overrides or {}))
    return {k: Substrate(k, v) for k, v in vals.items()}


def show(edges):
    return sorted("".join(sorted(e)) for e in edges)


def main():
    print("EXP2  static vs state-derived neighbourhood")
    print("-" * 62)

    base = config()
    gated = GatedTopology(ring_gate(M, RADIUS))
    static = StaticTopology(gated.edge_set(base))  # same edges at t0

    print(f"  states t0       : {sorted((k, v.state) for k, v in base.items())}")
    print(f"  edges  t0       : {show(static.edges)}  (both topologies)")
    print()
    print("  perturb a across its whole state space:")
    print("    a   static_delta   gated_delta   incident   non_incident")

    static_total = gated_total = incident_total = nonincident_total = 0
    for s in range(M):
        pert = config({"a": s})
        sd = edge_delta(static.edge_set(base), static.edge_set(pert))
        gd = edge_delta(gated.edge_set(base), gated.edge_set(pert))
        inc, non = split_delta(gd, "a")
        static_total += len(sd)
        gated_total += len(gd)
        incident_total += len(inc)
        nonincident_total += len(non)
        print(f"    {s:<3} {len(sd):<14} {len(gd):<13} {len(inc):<10} {len(non)}")

    print()
    print(f"  RESULT static_changed_pairs={static_total} "
          f"gated_changed_pairs={gated_total} "
          f"gated_incident={incident_total} gated_non_incident={nonincident_total}")
    return {
        "static_total": static_total,
        "gated_total": gated_total,
        "incident_total": incident_total,
        "nonincident_total": nonincident_total,
    }


if __name__ == "__main__":
    main()
