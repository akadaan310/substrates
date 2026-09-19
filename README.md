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

## Interactive bench

`artifact/lab.html` is the public gateway into the same mechanics: five benches,
one per rung, each computing its result in the browser rather than reporting it.
Its arithmetic is a direct transcription of `substrates/` and reproduces every
figure in `FINDINGS.md` — EXP2 `0 / 17 / 17 / 0`, EXP3 `0 / 8` and
`{0:0, 1:2, 2:2, 3:0}`, EXP4 `0 / 3` violations and influence
`[0,0] / [3,0] / [3,1]`.

Substrate seeds come from live commits on this repository, read through the
viewer's GitHub connector; where no connector is available the bench falls back
to the experiments' own seed values and says so.
