# Findings

Every number below is printed by an experiment in `experiments/` and asserted
by a test in `tests/test_primitives.py`. Claims not backed by a number are not
made here.

Starting point: the repository was empty — no commits, no files. There was no
prior system to locate a primitive in, so the ladder below was built from
nothing and each rung measured.

---

## EXP0 — the smallest substrate that does not collapse

Two substrates holding the same value (3, 3):

| distinguished by | resulting population |
|---|---|
| state only | **1** |
| label | **2** |

Distinguishing by state alone destroys one of the two. A label also survives a
state change: after `a: 3 → 4`, the label still reads `a`, while a state-keyed
view cannot separate that substrate from a different one already holding 4.

**Smallest demonstrable primitive: a label attached to a value.** The value
alone is not a substrate — it is a state that two things can share. The label
is what resists collapse, and it is what the rest of the ladder is built on.

## EXP1 — interaction without merging

A `Coupling` is a directed read: it takes the source's state and writes a new
state into the destination.

| | population | labels preserved | source unchanged | distinct destination states reachable |
|---|---|---|---|---|
| `Coupling(a→b)` | 2 → **2** | yes | yes | **12 / 12** |
| `merge(a, b)` | 2 → **1** | no (`a+b`) | — | — |

Sweeping the source across its whole state space produces 12 distinct
destination states, so the read genuinely carries the source's state; the
population and both labels are nonetheless unchanged. The merge operation is
the contrast: it returns one substrate and destroys both labels.

**Smallest operation for interaction without merging: a directed state read
that writes only to state, never to a label.**

## EXP2 — can one substrate's state change another's neighbourhood?

Four substrates on a ring of 12, adjacency radius 2, same edge set at t0
(`ab`). Substrate `a` was perturbed across all 12 of its states:

| topology | changed pairs (summed over all 12 perturbations) | touching `a` | not touching `a` |
|---|---|---|---|
| edges stored | **0** | 0 | 0 |
| edges derived from state | **17** | 17 | **0** |

With stored edges the answer is flatly no: 0 changes across the entire state
space. With adjacency derived from the endpoints' states, the answer is yes —
17 changed relations.

**The missing primitive at this rung is a state-dependent adjacency
predicate.** Adding it yields adaptive topology, but only in a restricted
sense: every one of the 17 changes touches the substrate that was perturbed.
A pairwise gate cannot change a relation it is not an endpoint of.

## EXP3 — relations that change without touching the perturbed substrate

Two candidates were measured against that limit.

**(A) a mediating term.** The gate reads the two endpoints *and* a
configuration-wide term (here, summed state). Perturbing `a` shifts that term,
which changes the adjacency of pairs `a` is not part of.

| gate | non-incident changes, no dynamics |
|---|---|
| pairwise | **0** |
| mediated | **8** |

**(B) no new primitive — just time.** Keep the pairwise gate, and let the
coupling from EXP1 carry the perturbation, re-deriving the topology at each
step:

| steps elapsed | total changed pairs | touching `a` | not touching `a` |
|---|---|---|---|
| 0 | 2 | 2 | **0** |
| 1 | 4 | 2 | **2** |
| 2 | 3 | 1 | **2** |
| 3 | 0 | 0 | **0** |

Both routes reach non-incident relations, and they are not equivalent. The
mediating term does it in zero steps; propagation needs at least one step and
is not monotone — by step 3 the two trajectories have reconverged and the
difference is gone entirely. So a mediating term is *sufficient* for
instantaneous non-local relational change, but it is not *necessary* for
non-local relational change as such.

## EXP4 — conjoining bounded state spaces without collapsing them

U1: three substrates over `range(5)`. U2: three substrates over `range(7)`.
`Interface` is one directed boundary link carrying a translation from one
state space into the other. Collapse is the contrast: re-bound every substrate
to a single shared modulus.

| over 6 steps | conjoined | collapsed |
|---|---|---|
| states outside their own universe's space | **0** | **3** |
| distinct universes remaining | **2** | **1** |

Collapse is not a neutral relabelling: U1's substrates reach states 5 and 6,
which do not exist in U1's state space. Conjoining leaves both spaces closed.

Under conjunction the universes also remain separately steppable — running
only U1's couplings changes U1 and leaves U2 bit-for-bit unchanged
(`U1_changed=True U2_unchanged=True`) — while still reaching each other:

| interfaces present | U1 → U2 influence | U2 → U1 influence |
|---|---|---|
| none | 0 | 0 |
| forward only | **3** | 0 |
| forward + reverse | **3** | **1** |

With no interface the two are causally sealed. One interface carries influence
strictly one way; the reverse direction measures exactly 0. Mutual conjunction
takes two.

**Smallest structure that conjoins bounded state spaces without collapsing
them: one directed boundary link carrying a translation between the spaces —
a partial map, not a union.** It is directed, so it is also the unit in which
asymmetric conjunction is expressible.

---

## The ladder, as measured

| rung | primitive added | what it buys | what it still cannot do |
|---|---|---|---|
| S0 | label on a value | two substrates with equal state stay two | nothing interacts |
| S1 | directed state read | interaction at constant population | relations are fixed |
| S2 | state-derived adjacency | adaptive topology, incident only | third-party relations |
| S3 | gate reads a shared term | non-incident change in zero steps | — |
| S4 | translating boundary link | conjunction with closure preserved | — |

EXP3(B) is the one place where a rung turned out not to be strictly required:
S1 plus S2 plus elapsed time already reaches non-incident relations, so S3 buys
immediacy and reliability, not reachability.
