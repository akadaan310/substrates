"""Assertions for F9, the gate-arity sweep. Every figure AUDIT.md reports for
F9 is pinned here."""
import itertools
import unittest

from audit.arity_sweep import (
    IDS4, PERTURBED, arity2_exhaustive, arity3_exhaustive, bitgate, non_incident,
)


class Arity2Impossible(unittest.TestCase):
    def test_no_arity2_gate_at_all_moves_a_non_incident_relation(self):
        for M in (2, 3):
            ngates, checked, flips, same = arity2_exhaustive(M)
            self.assertEqual(ngates, 1 << (M * M))      # the complete gate space
            self.assertEqual(flips, 0, f"M={M}")
            self.assertGreater(checked, 0)

    def test_the_mechanism_is_an_unchanged_input_not_a_collision(self):
        for M in (2, 3):
            _, checked, _, same = arity2_exhaustive(M)
            self.assertEqual(same, checked, f"M={M}")


class Arity3NeedsTheWitness(unittest.TestCase):
    def test_witness_a_admits_flips(self):
        ngates, can, mx, _ = arity3_exhaustive(2, "a")
        self.assertEqual(ngates, 256)
        self.assertEqual(can, 240)
        self.assertEqual(mx, 16)

    def test_witness_b_admits_none_despite_equal_arity(self):
        ngates, can, mx, _ = arity3_exhaustive(2, "b")
        self.assertEqual(ngates, 256)
        self.assertEqual(can, 0)
        self.assertEqual(mx, 0)


class TheCondition(unittest.TestCase):
    """A relation can move iff the perturbed substrate is in its witness set."""

    def _can_flip(self, W, M=2, ids=IDS4):
        for mask in range(1 << (M ** len(W))):
            g = bitgate(mask, M)
            for combo in itertools.product(range(M), repeat=len(ids)):
                cfg = dict(zip(ids, combo))
                for new_a in range(M):
                    if new_a == cfg[PERTURBED]:
                        continue
                    pert = dict(cfg, a=new_a)
                    if g(tuple(cfg[s] for s in W)) != g(tuple(pert[s] for s in W)):
                        return True
        return False

    def test_predicate_matches_observation_for_every_witness_set(self):
        for W in (("c", "d"), ("c", "d", "a"), ("c", "d", "b"), ("c", "d", "a", "b")):
            self.assertEqual(self._can_flip(W), PERTURBED in W, str(W))


class EffectiveArity(unittest.TestCase):
    def test_a_two_argument_gate_over_derived_values_is_not_arity_two(self):
        M, ids = 3, IDS4
        pairs = non_incident(ids)

        def derived(cfg, x, y):
            mean = sum(cfg.values()) / len(cfg)
            return int((cfg[x] >= mean) == (cfg[y] >= mean))

        flips = 0
        for combo in itertools.product(range(M), repeat=len(ids)):
            cfg = dict(zip(ids, combo))
            for new_a in range(M):
                if new_a == cfg[PERTURBED]:
                    continue
                pert = dict(cfg, a=new_a)
                flips += sum(1 for x, y in pairs if derived(cfg, x, y) != derived(pert, x, y))
        self.assertEqual(flips, 72)


if __name__ == "__main__":
    unittest.main(verbosity=2)
