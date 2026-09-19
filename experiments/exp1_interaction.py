"""EXP1: the smallest operation letting two distinguishable substrates
interact WITHOUT merging.

Tested against a merge operation as the contrast case.
"""
from substrates.s0_substrate import Substrate, merge
from substrates.s1_coupling import Coupling, apply_coupling

M = 12


def main():
    print("EXP1  interaction without merging")
    print("-" * 62)

    config = {"a": Substrate("a", 2), "b": Substrate("b", 5)}
    c = Coupling("a", "b", lambda s, d: (d + s) % M)

    after = apply_coupling(config, c)
    print(f"  before        : {sorted((k, v.state) for k, v in config.items())}")
    print(f"  after a->b    : {sorted((k, v.state) for k, v in after.items())}")

    cardinality_in, cardinality_out = len(config), len(after)
    labels_kept = set(config) == set(after)
    src_untouched = after["a"].state == config["a"].state

    # Did anything actually cross? Sweep the source over its whole space.
    reached = {apply_coupling({"a": Substrate("a", s), "b": Substrate("b", 5)}, c)["b"].state
               for s in range(M)}

    merged = merge(config["a"], config["b"], M)
    print(f"  merge(a,b)    : population {cardinality_in} -> 1, label {merged.sid!r}")
    print()
    print(f"  RESULT coupling: population {cardinality_in}->{cardinality_out} "
          f"labels_preserved={labels_kept} source_unchanged={src_untouched} "
          f"distinct_dst_states_reachable={len(reached)}/{M}")
    return {
        "cardinality_in": cardinality_in,
        "cardinality_out": cardinality_out,
        "labels_preserved": labels_kept,
        "source_unchanged": src_untouched,
        "reachable": len(reached),
        "merge_cardinality_out": 1,
    }


if __name__ == "__main__":
    main()
