"""Assertions for F13, the S4 minimality search. Every figure AUDIT.md reports
for F13 is pinned here, including both exhaustive map searches."""
import itertools
import unittest

from audit.s4_minimality import (
    INTRA, M1, M2, SEED, U1, U2, influence, link, old_metric, own_mod,
    profile, reachable, trajectory,
)

INCLUSION = tuple(s % M2 for s in range(M1))
REDUCTION = tuple(s % M1 for s in range(M2))
CONST_F = tuple(0 for _ in range(M1))
CONST_R = tuple(0 for _ in range(M2))
ONE_BIT = tuple(1 if s >= 2 else 0 for s in range(M1))


class TargetsAreNotTheSame(unittest.TestCase):
    """T1 (conjunction) and T2 (nontrivial translation) come apart."""

    def test_a_map_that_is_the_identity_on_the_reachable_set_still_conjoins(self):
        R = reachable(INTRA, "a2", "a0")
        tau = tuple(s if s in R else 0 for s in range(M1))
        self.assertTrue(all(tau[s] == s for s in R))          # T2 is FALSE
        cells, _ = influence(INTRA + [link("a2", "b0", tau)], U2, "a0")
        self.assertGreater(cells, 0)                           # T1 is TRUE

    def test_the_canonical_expanding_map_is_forced_to_be_the_identity(self):
        for src, dst in ((5, 7), (4, 8), (3, 11)):
            canon = [s % dst for s in range(src)]
            self.assertEqual(canon, list(range(src)))


class InfluenceRequiresInformationNotIdentity(unittest.TestCase):
    def test_forward_map_space_exhaustively(self):
        R = reachable(INTRA, "a2", "a0")
        agree = total = constant = constant_with_influence = 0
        for tau in itertools.product(range(M2), repeat=M1):
            cells, _ = influence(INTRA + [link("a2", "b0", tau)], U2, "a0")
            distinct = len({tau[s] for s in R})
            if distinct == 1:
                constant += 1
                constant_with_influence += bool(cells)
            agree += (distinct >= 2) == (cells > 0)
            total += 1
        self.assertEqual(total, M2 ** M1)          # 16807 — the whole space
        self.assertEqual(agree, total)             # predicate is exact
        self.assertEqual(constant, 49)
        self.assertEqual(constant_with_influence, 0)

    def test_reverse_map_space_exhaustively(self):
        R = reachable(INTRA, "b2", "b1")
        agree = total = 0
        for tau in itertools.product(range(M1), repeat=M2):
            cells, _ = influence(INTRA + [link("b2", "a0", tau)], U1, "b1")
            agree += (len({tau[s] for s in R}) >= 2) == (cells > 0)
            total += 1
        self.assertEqual(total, M1 ** M2)          # 78125 — the whole space
        self.assertEqual(agree, total)

    def test_one_bit_is_enough(self):
        cells, _ = influence(INTRA + [link("a2", "b0", ONE_BIT)], U2, "a0")
        self.assertGreater(cells, 0)


class CountIsNotTheUnit(unittest.TestCase):
    def test_two_constant_interfaces_conjoin_nothing(self):
        links = INTRA + [link("a2", "b0", CONST_F), link("b2", "a0", CONST_R)]
        self.assertEqual(influence(links, U2, "a0")[0], 0)
        self.assertEqual(influence(links, U1, "b1")[0], 0)

    def test_one_informative_interface_conjoins(self):
        self.assertGreater(influence(INTRA + [link("a2", "b0", ONE_BIT)], U2, "a0")[0], 0)


class Directionality(unittest.TestCase):
    def test_one_link_carries_one_way_only(self):
        links = INTRA + [link("a2", "b0", INCLUSION)]
        self.assertGreater(influence(links, U2, "a0")[0], 0)
        self.assertEqual(influence(links, U1, "b1")[0], 0)

    def test_two_links_carry_both_ways(self):
        links = INTRA + [link("a2", "b0", INCLUSION), link("b2", "a0", REDUCTION)]
        self.assertGreater(influence(links, U2, "a0")[0], 0)
        self.assertGreater(influence(links, U1, "b1")[0], 0)

    def test_no_link_carries_nothing(self):
        self.assertEqual(influence(INTRA, U2, "a0")[0], 0)
        self.assertEqual(influence(INTRA, U1, "b1")[0], 0)


class TheMetricIsTwoSided(unittest.TestCase):
    """The replacement metric must detect contraction, which v0.1's could not."""

    def _traj(self, modof):
        links = INTRA + [link("a2", "b0", INCLUSION), link("b2", "a0", REDUCTION)]
        return trajectory(SEED, links, modof)

    def test_old_metric_is_blind_to_contraction(self):
        traj = self._traj(lambda s: 5)                  # collapse to the minimum
        self.assertEqual(old_metric(traj, U2, M2), 0)   # v0.1 sees nothing
        p = profile(traj, U2, M2)
        self.assertTrue(p["contraction"])               # the replacement sees it
        self.assertFalse(p["escape"])

    def test_new_metric_still_detects_escape(self):
        traj = self._traj(lambda s: 7)                  # collapse to the maximum
        self.assertGreater(old_metric(traj, U1, M1), 0)
        self.assertTrue(profile(traj, U1, M1)["escape"])

    def test_conjoining_shows_neither(self):
        p1 = profile(self._traj(own_mod), U1, M1)
        p2 = profile(self._traj(own_mod), U2, M2)
        for p in (p1, p2):
            self.assertFalse(p["escape"])
            self.assertFalse(p["contraction"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
