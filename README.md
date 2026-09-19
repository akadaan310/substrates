# substrates

A ladder of primitives, built bottom-up. Each module adds exactly one thing
over the one below it, and each addition is justified by an experiment that
measures what the system could not do before it.

```
substrates/s0_substrate.py   a label and a value
substrates/s1_coupling.py    a directed state read (interaction, not merging)
substrates/s2_topology.py    adjacency stored  vs  adjacency derived from state
substrates/s3_mediation.py   a gate that also reads a configuration-wide term
substrates/s4_universe.py    bounded state spaces, and an Interface between them
```

Run everything:

```
PYTHONPATH=.:experiments python3 experiments/run_all.py   # measurements
PYTHONPATH=. python3 -m unittest discover -s tests -v     # 20 assertions
```

No dependencies, Python 3.11. Every number in `FINDINGS.md` is printed by an
experiment and asserted by a test. Nothing in this repo models anything
outside itself.
