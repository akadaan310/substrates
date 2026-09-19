"""Every assertion here is a claim the experiments print. If a claim is not
tested here, it is not a claim the code supports."""
import unittest

from substrates.s0_substrate import (
    Substrate, merge, population_by_identity, population_by_state,
)
from substrates.s1_coupling import Coupling, apply_coupling, run
from substrates.s2_topology import (
    GatedTopology, StaticTopology, edge_delta, ring_gate, split_delta,
)
from substrates.s3_mediation import MediatedTopology, load_gated_ring
from substrates.s4_universe import (
    Interface, Universe, bound_violations, collapsed_modulus_of,
    conjoined_modulus_of, home_universe, restrict, seed,
)

M = 12
BASE = {"a": 0, "b": 2, "c": 5, "d": 9}


def cfg(overrides=None):
    vals = dict(BASE, **(overrides or {}))
    return {k: Substrate(k, v) for k, v in vals.items()}


class S0Identity(unittest.TestCase):
    def test_state_alone_collapses_two_substrates_into_one(self):
        subs = [Substrate("a", 3), Substrate("b", 3)]
        self.assertEqual(len(population_by_state(subs)), 1)
        self.assertEqual(len(population_by_identity(subs)), 2)

    def test_label_survives_a_state_change(self):
        a = Substrate("a", 3)
        self.assertEqual(a.with_state(4).sid, a.sid)
        self.assertNotEqual(a.with_state(4).state, a.state)


class S1Coupling(unittest.TestCase):
    def setUp(self):
        self.c = Coupling("a", "b", lambda s, d: (d + s) % M)
        self.config = {"a": Substrate("a", 2), "b": Substrate("b", 5)}

    def test_population_and_labels_are_preserved(self):
        after = apply_coupling(self.config, self.c)
        self.assertEqual(len(after), len(self.config))
        self.assertEqual(set(after), set(self.config))

    def test_coupling_is_directed(self):
        after = apply_coupling(self.config, self.c)
        self.assertEqual(after["a"].state, self.config["a"].state)
        self.assertNotEqual(after["b"].state, self.config["b"].state)

    def test_something_actually_crosses(self):
        reached = {
            apply_coupling({"a": Substrate("a", s), "b": Substrate("b", 5)},
                           self.c)["b"].state
            for s in range(M)
        }
        self.assertGreater(len(reached), 1)

    def test_merge_is_the_contrast_case(self):
        one = merge(self.config["a"], self.config["b"], M)
        self.assertIsInstance(one, Substrate)
        self.assertNotIn(one.sid, self.config)

    def test_apply_coupling_does_not_mutate_its_input(self):
        snapshot = {k: v.state for k, v in self.config.items()}
        apply_coupling(self.config, self.c)
        self.assertEqual({k: v.state for k, v in self.config.items()}, snapshot)


class S2Topology(unittest.TestCase):
    def setUp(self):
        self.base = cfg()
        self.gated = GatedTopology(ring_gate(M, 2))
        self.static = StaticTopology(self.gated.edge_set(self.base))

    def test_static_topology_never_responds_to_state(self):
        total = sum(
            len(edge_delta(self.static.edge_set(self.base),
                           self.static.edge_set(cfg({"a": s}))))
            for s in range(M)
        )
        self.assertEqual(total, 0)

    def test_gated_topology_responds_to_state(self):
        total = sum(
            len(edge_delta(self.gated.edge_set(self.base),
                           self.gated.edge_set(cfg({"a": s}))))
            for s in range(M)
        )
        self.assertGreater(total, 0)

    def test_pairwise_gate_only_moves_edges_touching_the_perturbed_substrate(self):
        non_incident = 0
        for s in range(M):
            delta = edge_delta(self.gated.edge_set(self.base),
                               self.gated.edge_set(cfg({"a": s})))
            non_incident += len(split_delta(delta, "a")[1])
        self.assertEqual(non_incident, 0)


class S3Mediation(unittest.TestCase):
    def test_mediating_term_moves_edges_not_touching_the_perturbed_substrate(self):
        base = cfg()
        med = MediatedTopology(load_gated_ring(M, 3, 1, 20))
        non_incident = 0
        for s in range(M):
            delta = edge_delta(med.edge_set(base), med.edge_set(cfg({"a": s})))
            non_incident += len(split_delta(delta, "a")[1])
        self.assertGreater(non_incident, 0)

    def test_propagation_reaches_non_incident_pairs_without_a_mediating_term(self):
        gated = GatedTopology(ring_gate(M, 3))
        links = (Coupling("a", "b", lambda s, d: d + s),
                 Coupling("b", "c", lambda s, d: d + s),
                 Coupling("c", "d", lambda s, d: d + s))
        mod = lambda sid: M
        found = []
        for k in range(4):
            u = run(cfg(), links, mod, k)
            p = run(cfg({"a": 6}), links, mod, k)
            delta = edge_delta(gated.edge_set(u), gated.edge_set(p))
            found.append(len(split_delta(delta, "a")[1]))
        self.assertEqual(found[0], 0)          # no dynamics, no reach
        self.assertGreater(max(found), 0)      # with dynamics, reach


class S4Universes(unittest.TestCase):
    def setUp(self):
        self.u1 = Universe("U1", 5, ("a0", "a1", "a2"), (
            Coupling("a0", "a1", lambda s, d: d + s + 1),
            Coupling("a1", "a2", lambda s, d: d + s + 1),
        ))
        self.u2 = Universe("U2", 7, ("b0", "b1", "b2"), (
            Coupling("b0", "b1", lambda s, d: d + s + 1),
            Coupling("b1", "b2", lambda s, d: d + s + 1),
        ))
        self.us = (self.u1, self.u2)
        self.seed_vals = {"a0": 1, "a1": 0, "a2": 3,
                          "b0": 2, "b1": 6, "b2": 4}
        self.base = seed(self.us, self.seed_vals)
        self.fwd = Interface("a2", "b0", lambda s: s % 7)
        self.rev = Interface("b2", "a0", lambda s: s % 5)
        self.links = (self.u1.couplings + self.u2.couplings
                      + (self.fwd.as_coupling(), self.rev.as_coupling()))

    def _violations(self, modulus_of, steps=6):
        return sum(len(bound_violations(run(self.base, self.links, modulus_of, k),
                                        self.us))
                   for k in range(1, steps + 1))

    def test_conjoining_keeps_each_universe_inside_its_own_state_space(self):
        self.assertEqual(self._violations(conjoined_modulus_of(self.us)), 0)

    def test_collapsing_breaks_the_smaller_state_space(self):
        self.assertGreater(self._violations(collapsed_modulus_of(self.us)), 0)

    def test_conjoining_keeps_the_partition(self):
        self.assertEqual(len(set(home_universe(self.us).values())), 2)

    def test_each_universe_is_still_separately_steppable(self):
        mod = conjoined_modulus_of(self.us)
        stepped = run(self.base, restrict(self.links, self.u1.members), mod, 1)
        self.assertEqual([stepped[s].state for s in self.u2.members],
                         [self.base[s].state for s in self.u2.members])
        self.assertNotEqual([stepped[s].state for s in self.u1.members],
                            [self.base[s].state for s in self.u1.members])

    def _influence(self, ifaces, steps=6):
        mod = conjoined_modulus_of(self.us)
        links = (self.u1.couplings + self.u2.couplings
                 + tuple(i.as_coupling() for i in ifaces))
        ref = run(self.base, links, mod, steps)
        p1 = run(seed(self.us, dict(self.seed_vals, a0=(self.seed_vals["a0"] + 1) % 5)),
                 links, mod, steps)
        p2 = run(seed(self.us, dict(self.seed_vals, b1=(self.seed_vals["b1"] + 1) % 7)),
                 links, mod, steps)
        return (sum(1 for s in self.u2.members if p1[s].state != ref[s].state),
                sum(1 for s in self.u1.members if p2[s].state != ref[s].state))

    def test_without_an_interface_the_universes_do_not_reach_each_other(self):
        self.assertEqual(self._influence(()), (0, 0))

    def test_one_interface_carries_influence_in_one_direction_only(self):
        forward, backward = self._influence((self.fwd,))
        self.assertGreater(forward, 0)
        self.assertEqual(backward, 0)

    def test_two_interfaces_carry_influence_both_ways(self):
        forward, backward = self._influence((self.fwd, self.rev))
        self.assertGreater(forward, 0)
        self.assertGreater(backward, 0)

    def test_interface_translation_lands_inside_the_destination_space(self):
        for s in range(self.u1.modulus):
            self.assertIn(self.fwd.translate(s), range(self.u2.modulus))
        for s in range(self.u2.modulus):
            self.assertIn(self.rev.translate(s), range(self.u1.modulus))


if __name__ == "__main__":
    unittest.main(verbosity=2)
