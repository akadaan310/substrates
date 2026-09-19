"""EXP0: what is the smallest substrate that does not collapse?

Question: is `state` alone enough to make two substrates distinguishable,
or is a label required?
"""
from substrates.s0_substrate import (
    Substrate, population_by_state, population_by_identity,
)


def main():
    print("EXP0  smallest non-collapsing substrate")
    print("-" * 62)

    # Two substrates that happen to hold the same value.
    a = Substrate("a", 3)
    b = Substrate("b", 3)

    by_state = population_by_state([a, b])
    by_id = population_by_identity([a, b])
    print(f"  two substrates, equal state (3,3)")
    print(f"    distinguished by state only : population = {len(by_state)}")
    print(f"    distinguished by label      : population = {len(by_id)}")

    # Continuity across a state change: is the thing at state 4 the same
    # thing that was at state 3, or is it b?
    a2 = a.with_state(4)
    c = Substrate("c", 4)
    same_label = a2.sid == a.sid
    state_key_collision = a2.state == c.state
    print(f"  substrate a moves 3 -> 4, substrate c already holds 4")
    print(f"    label says a2 is still a         : {same_label}")
    print(f"    state key cannot separate a2,c   : {state_key_collision}")

    print()
    print(f"  RESULT collapse_without_label={len(by_state) == 1} "
          f"survives_with_label={len(by_id) == 2} "
          f"identity_survives_state_change={same_label}")
    return {
        "population_by_state": len(by_state),
        "population_by_identity": len(by_id),
        "identity_survives_state_change": same_label,
    }


if __name__ == "__main__":
    main()
