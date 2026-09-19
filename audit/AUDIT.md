# Adversarial audit — Experimental Instrument v0.1

Subject: the published Substrate Bench and the `substrates/` modules behind it,
frozen as **v0.1**.

Method: every claim the instrument makes was restated as something that could
fail, then attacked. Eight probes are in `audit/probes.py`; run them with
`PYTHONPATH=. python3 audit/probes.py`. Probe results are cited below as **P1**–**P8**.

Summary of outcome: of the instrument's five headline claims, **one survives as
stated, two survive only as tautologies, and three are falsified or materially
weakened.** Three of the five headline *numbers* are artifacts of chosen
parameters. The instrument's central organising claim — minimality — is never
tested by any bench.

---

## S0 — substrate

**1. What is measured.** The cardinality of two sets built from the same pair of
substrates: `|{a.state, b.state}|` and `|{a.sid, b.sid}|`.

**2. Primitive assumptions.** That a substrate is a label plus a value; that
`sid` and `state` are different in kind; that identity is established by
declaration rather than earned by behaviour.

**3. What it actually demonstrates.** That a set keyed on a field collapses
elements agreeing on that field. This is the definition of a set quotient. With
`a.state == b.state`, `|{3,3}| = 1` is not a fact about substrates.

**4. What it does NOT demonstrate.** That a label is *necessary*. **P7 falsifies
this directly:** two substrates with no labels at all, carrying distinct update
rules (`+1`, `+5` on Z₁₂), have their identity uniquely recovered from the
unlabelled state multiset at two consecutive times in **144/144** configurations
— including **12/12** of the cases where both states are equal, which is exactly
the case the bench presents as proof that labels are indispensable. Identity is
recoverable from dynamics. The label is sufficient, not necessary.

**5. Hidden assumptions in the implementation.** `sid` is an ordinary dataclass
field; nothing structural distinguishes it from `state`. A substrate defined as
a single state `(sid, value)` would be equally distinguishable with no second
primitive. The label/state split is a naming convention the experiment then
"discovers".

**6. Where the visualization could be mistaken for the computation.** Both cells
turn ochre when states match, which reads as an event befalling the substrates.
Nothing happens to them; only the observer's choice of key changes. The
`by state` tile renders in the violation colour, implying equal states are an
illegal condition. They are legal.

**7. Invariant, parameter-dependent, or artifact.** Invariant but **vacuously**
— it holds for every pair of values at every modulus because it is set
cardinality, not a property of the rung.

**8. Smallest experiment that would falsify or strengthen.** Already run (P7).
To strengthen rather than falsify: define identity operationally as
*re-identifiability across one step* and measure the fraction of dynamics under
which it fails. That number would be a real measurement; the current one is not.

---

## S1 — coupling

**1. What is measured.** Population before and after; label-set equality; source
state invariance; `|{f(s, d₀) : s ∈ Z₁₂}|`.

**2. Primitive assumptions.** That interaction means one substrate's state
entering another's update; that directedness is a property of the operation;
that merge is the relevant contrast.

**3. What it actually demonstrates.** That `apply_coupling` preserves population
and labels and leaves the source untouched, and that under `(d + s) mod 12` the
destination reaches all 12 states.

**4. What it does NOT demonstrate.** That this operation is the *smallest* one
with those properties — no minimality search is performed anywhere. Nor that
merge is the only alternative; it is one hand-picked contrast. **P8 shows the
`12/12` figure measures the arithmetic, not the coupling:** substituting
`d + s%3`, `d + 4s`, or `d + 0·s` gives 3, 3, and 1 reachable states while
population and label preservation are completely unaffected.

**5. Hidden assumptions.** Addition on Z₁₂ is bijective in `s` for fixed `d`;
the headline reachability is that bijectivity and nothing else. Directedness is
declared by the `src`/`dst` fields of the dataclass, not measured — the
experiment cannot observe a coupling that fails to be directed.

**6. Where the visualization could be mistaken for the computation.** Cell `b`
carries the note `→ would be 7`: a counterfactual rendered inside the cell that
displays state. The `b states reachable 12/12` tile sits in the same tile row as
`population`, in the same typeface and weight, but is the result of a
hypothetical sweep that never occurs on screen, while `population` is live.

**7. Invariant, parameter-dependent, or artifact.** Population and label
preservation: **invariant** and structural. `12/12`: **artifact** of the chosen
transducer.

**8. Smallest experiment.** Sweep a family of transducers spanning bijective to
constant, and report population, labels, and reachability side by side. This
separates the structural claim (survives) from the arithmetic claim (does not).
P8 is a four-point version of exactly this.

---

## S2 — topology

**1. What is measured.** `|before △ after|` on the derived edge set when `a`'s
state changes, partitioned by whether the changed pair contains `a`.

**2. Primitive assumptions.** Adjacency is symmetric, deterministic, memoryless,
and defined over the complete pair set; the gate reads exactly two endpoints.

**3. What it actually demonstrates.** That a stored edge set does not respond to
state, and a derived one does.

**4. What it does NOT demonstrate.** The stored result is a **tautology**:
`StaticTopology.edge_set(config)` returns `self.edges` and never reads its
argument. Measuring zero change measures that a constant function is constant.
More seriously, **the non-incidence result is a theorem, not a measurement.**
For a gate `g(sₓ, s_y)`, a pair excluding `a` has both arguments unchanged when
only `a` moves, so its adjacency cannot change. **P3 confirms exhaustively:
248,832 cases over all of Z₁₂⁴ × 12 perturbations, zero non-incident changes.**
The 12-sample sweep in EXP2 could not have produced any other answer.

**5. Hidden assumptions.** `edge_delta` is a symmetric difference, so an edge
appearing and an edge disappearing count identically. The headline `17` is a
**sum over twelve separate perturbations**, each against the same base — it is a
count of (perturbation, pair) incidents, not of relations in any one
configuration.

**6. Where the visualization could be mistaken for the computation.** The ring
places each node at `angle = state`, so adjacency looks like a 2-D geometric
property. The gate is a 1-D ring metric; chord length happens to be monotone in
ring distance, so the picture is faithful by luck, but it invites reading chord
crossing and Euclidean proximity as meaningful. They are not. Worse: two
substrates in the same state are drawn at the same point, and one hides the
other — the projection silently re-enacts the S0 collapse as though it were a
fact about the system. The ochre "changed" edges are changes against an
unperturbed base the viewer cannot see at the same time.

**7. Invariant, parameter-dependent, or artifact.** Stored → 0: **tautological**.
Non-incident = 0: **invariant**, and provable from gate arity. `17`:
**parameter-dependent** — **P6** over 4,000 random seeds gives range 15–21,
mean 17.5, with only **43.1%** of seeds yielding exactly 17. It is a typical
value, not a constant, and `FINDINGS.md` states it without that qualification.

**8. Smallest experiment.** Replace the 12-point sweep with the exhaustive check
(P3) and restate the result as a structural consequence of arity. Separately,
report the `17` as a distribution over seeds rather than a scalar.

---

## S3 — mediation

**1. What is measured.** Non-incident changed pairs under (a) a gate reading a
configuration-wide sum, and (b) a pairwise gate after *k* coupling steps.

**2. Primitive assumptions.** That the mediating term is a sum over all
substrates; that the radius it selects is a two-valued step function; that the
coupling graph is the chain `a→b→c→d`.

**3. What it actually demonstrates.** That a gate reading something beyond its
two endpoints can change relations excluding the perturbed substrate, and that
propagation through couplings reaches them too, from step 1.

**4. What it does NOT demonstrate.** That a configuration-wide term is the
*smallest* addition. **P4 falsifies this:** a gate reading its two endpoints plus
**one** designated third substrate — arity 3, not arity N — produces 6
non-incident changes. Reading the whole configuration is strictly more than
required. The correct statement is "arity greater than two", and the bench
claims something narrower and stronger than it tested.

**5. Hidden assumptions.** `total_load` is a *linear* functional, so every
substrate has identical leverage over the gate; nothing tests a selective or
nonlinear medium. Because the radius is a step function, the mediated gate
behaves **exactly pairwise everywhere except at one threshold crossing** — it is
not continuously more capable, it is pairwise plus one discontinuity. In `time`
mode the chain topology alone determines when `a` reaches `c` and `d`; the
coupling graph is never varied.

**6. Where the visualization could be mistaken for the computation.** The three
modes sit in one segmented control, implying three settings of one experiment.
They are two different systems (gates of different arity) and one different
*protocol* (with dynamics). Their tallies are rendered identically and are
incommensurable. Printing `load(base)` beside `radius` invites reading the load
as a physical quantity rather than an arbitrary summary statistic.

**7. Invariant, parameter-dependent, or artifact.** "A super-pairwise gate can
change non-incident relations": **invariant**. The count `8`: **artifact of the
threshold** — **P2** gives 0, 0, 8, 4, 0, 0 non-incident changes at thresholds
10, 16, 20, 24, 28, 40. The figure is the size of the half-space cut by an
arbitrary constant. "Vanishes by step 3": **artifact** of Z₁₂ wraparound with
`d+s`; it shows that this perturbation died, not that propagation generally
decays.

**8. Smallest experiment.** Already run (P4): swap the global sum for an arity-3
witness gate. To strengthen: sweep gate arity 2→N and report the minimum arity
at which non-incident change first appears. That would be an actual minimality
result, which the instrument currently asserts without one.

---

## S4 — universe

**1. What is measured.** Own-bound violations over 6 steps; count of distinct
universes; separability of a single-universe step; cross-influence as the number
of substrates differing after 6 steps under a seed perturbation.

**2. Primitive assumptions.** That a universe is a member set plus a modulus;
that collapse means re-bounding to the maximum modulus; that an interface is a
directed coupling carrying a translation.

**3. What it actually demonstrates.** That running with per-universe moduli keeps
states in range; that running everything at modulus 7 lets U1's members exceed
5; that influence is 0 with no interface, one-way with one, two-way with two.

**4. What it does NOT demonstrate.** Three failures, in increasing severity.

*Closure is tautological.* `step()` applies `mod modulus_of(sid)` as its last
operation, so under conjoined moduli a state cannot be out of range. The
"0 violations" result checks that `x % 5 < 5`.

*The violation test is one-sided.* `bound_violations` flags only states **above**
the bound. It structurally cannot detect a collapse that *shrinks* a state space.

*The collapse comparison is rigged.* "Collapse" is defined as re-bounding to the
**maximum** modulus while still judging U1 by `range(5)` — the dynamics is
changed and the old yardstick retained. **P5:** collapsing to 5 gives **0**
violations, to 7 gives **3**, to lcm 35 gives **31**. The instrument reports the
middle number as though it were a property of collapsing. Collapse-to-5 passes
the test while destroying U2's ability to reach states 5 and 6 — a real loss the
instrument is blind to, per the one-sidedness above.

*The translation is partly vacuous.* **P1:** the forward interface `a2→b0`,
`translate(s) = s % 7`, is the **identity map** on U1's entire space
`{0,1,2,3,4}`. The bench's headline structure — "a boundary link carrying a
translation" — is demonstrated by a link that translates nothing. Only the
reverse interface (`s % 5` on `range(7)`, mapping 5→0 and 6→1) does real work.

**5. Hidden assumptions.** Both universes use identical internal coupling
structure and the identical transducer `d+s+1`; they differ **only in modulus**,
so they are one system at two sizes rather than two systems. Influence is a
*count of differing substrates*, saturating at 3 — it cannot distinguish strong
from weak coupling, and 6 steps was chosen without justification.

**6. Where the visualization could be mistaken for the computation.** The two
universe panels are drawn with equal weight and no direction indicator, so
one-way influence appears only in the text. A cell flagged rose as
`outside range(5)` holds a value that is perfectly legal in the collapsed system
— it is being judged by the rule of the system that was abandoned, and the
colour presents that as a defect of the value.

**7. Invariant, parameter-dependent, or artifact.** 0 violations conjoined:
**tautological**. Influence `[0,0]` with no interface and separability: **invariant**,
provable from the coupling graph having no cross edge. `3` violations under
collapse: **artifact** of choosing max (P5). Influence `3` and `1`:
**parameter-dependent** saturation counts.

**8. Smallest experiment.** Two. (i) Report violations for collapse at min, max,
and lcm together, so the choice is visible (P5 is this). (ii) Replace
`translate(s) = s % 7` with the identity and confirm nothing changes, which
isolates how much of the S4 claim the translation is actually carrying.

---

# F9 — MEASUREMENT RECORD: gate-arity sweep, 2 → N

Run with `PYTHONPATH=. python3 audit/arity_sweep.py`; figures pinned by
`tests/test_arity.py`. This discharges audit item **E1** and replaces claim
**C9**, which v0.1 asserted and P4 falsified.

## Model measured

Each unordered pair `{x,y}` is assigned a **witness set** `W(x,y) ⊇ {x,y}` and
adjacency is `g(states of W(x,y))`. The gate's **arity** is `|W(x,y)|`.
Arity 2 means `W(x,y) = {x,y}` exactly — the v0.1 pairwise gate. A relation is
**non-incident** to `a` when `a ∉ {x,y}`.

## Result

**Minimum arity at which a non-incident change is possible: 3.**
**Arity 3 is not sufficient.** The operative condition is not the size of the
witness set but its membership:

> A relation `{x,y}` can change under a perturbation of `a`
> **if and only if `a ∈ W(x,y)`.**

For a non-incident relation this forces `|W| ≥ 3` *and* `a ∈ W`. Arity is a
consequence of the condition, not the condition.

## Arity 2 — impossibility

| M | gate space | coverage | checks | non-incident flips | gate input unchanged |
|---|---|---|---|---|---|
| 2 | 2⁴ = 16 | **exhaustive** | 768 | **0** | 768/768 |
| 3 | 2⁹ = 512 | **exhaustive** | 248,832 | **0** | 248,832/248,832 |
| 4 | 2¹⁶ | sampled 20,000 | 1,800,090 | 0 | — |
| 5 | 2²⁵ | sampled 20,000 | 1,918,785 | 0 | — |
| 12 | 2¹⁴⁴ | sampled 20,000 | 2,200,116 | 0 | — |

At M=2 and M=3 the search covers the **complete space of boolean arity-2
gates** — all 528 of them, symmetric and asymmetric alike — against every
configuration of four substrates, every perturbation, and every non-incident
pair. 249,600 exhaustive checks, zero flips.

The mechanism matters more than the count. In **249,600 of 249,600** exhaustive
cases the gate's *input tuple was identical* before and after. This is not a
case of differing inputs colliding on the same output — **the inputs never
differ**. That is why the search cannot be defeated by a cleverer gate, and why
it generalises past the moduli searched:

> For arity 2, `W(x,y) = {x,y}`. A perturbation changes only `s_a`. If
> `a ∉ {x,y}` then `(s_x, s_y)` is unchanged, so `g(s_x, s_y)` is unchanged, for
> every `g`. Holds for every M, every N, every gate, symmetric or not.

The exhaustive search verifies a theorem rather than sampling a contingency.

## Assumptions under which the impossibility holds

Each is load-bearing. Violating any one restores non-incident change at arity 2,
so the impossibility is exactly as strong as this list and no stronger.

| # | Assumption | If violated |
|---|---|---|
| I1 | The gate is a total, deterministic function of its witness set's states | A stochastic gate changes relations, but not *because of* `a` |
| I2 | Memoryless — no dependence on any earlier configuration | Restores change: history smuggles in other substrates' past states |
| I3 | `W(x,y) = {x,y}` exactly, and `W` is fixed, not itself state-dependent | A state-dependent `W` is a higher-arity function in disguise |
| I4 | The perturbation changes `s_a` only; no dynamics run between observations | **This is v0.1's EXP3B.** Let couplings run and arity 2 reaches non-incident relations from step 1 |
| I5 | Labels and the substrate set are fixed across the perturbation | Relabelling changes which pair is which |
| I6 | Arguments are **raw states**, not configuration-derived quantities | **Measured below** — a 2-argument gate over derived values gives 72 flips |

I4 is the important one: it is precisely the escape v0.1 already found and
reported as "pairwise + time". The impossibility is a statement about a
**single synchronous re-derivation**, not about pairwise gates in general.

## Apparent arity vs effective arity (I6)

| gate | signature | information set | flips |
|---|---|---|---|
| `(s_x + s_y) mod 2` | 2 arguments | `{x, y}` | **0** |
| `rank(x) == rank(y)`, rank taken against the configuration mean | 2 arguments | **all substrates** | **72** |

Both take two arguments. Only the first is arity 2 under this model. The
impossibility constrains the **information set**, not the number of formal
parameters — a gate whose arguments are configuration-derived is arity N wearing
an arity-2 signature. Any future gate must be classified by what it reads, not
by its signature.

## Arity 3 — possibility, and the witness condition

| arity | witness set | `a ∈ W`? | gates admitting a flip / total | max flips per gate |
|---|---|---|---|---|
| 2 | `(c, d)` | no | **0 / 16** | 0 |
| 3 | `(c, d, a)` | **yes** | **240 / 256** | 16 |
| 3 | `(c, d, b)` | no | **0 / 256** | 0 |
| 4 | `(c, d, a, b)` | **yes** | **65280 / 65536** | — |

`(c,d,b)` has the same arity as `(c,d,a)` and moves nothing, because `b`'s state
does not change when `a` is perturbed. The predicate `a ∈ W(x,y)` agrees with
observation in **4/4** witness sets.

The failure counts are an exact identity, not a residue. Gates that fail are
**precisely** the gates that ignore `a`'s argument, of which there are
`2^(M^(k-1))`:

| arity | total gates | admitted | failures | gates ignoring `a` | match |
|---|---|---|---|---|---|
| 3 | 256 | 240 | 16 | 2^(2²) = 16 | exact |
| 4 | 65,536 | 65,280 | 256 | 2^(2³) = 256 | exact |

A gate admits a non-incident flip **iff it actually depends on `a`'s state**.

## Capacity

| arity | witness rule | max simultaneous non-incident changes |
|---|---|---|
| 2 | `W(x,y) = (x,y)` | **0 of 3** |
| 3 | `W(x,y) = (x,y,a)` | **3 of 3** |
| 3 | `W(x,y) = (x,y,b)` | **0 of 3** |
| 4 | `W(x,y) = (x,y,a,b)` | **3 of 3** |

One witness is enough to move every non-incident relation at once. Arity 4 buys
no additional capacity over arity 3.

## Dependence on topology, gate function, and seed

**Topology (N).** Possibility is topology-independent; only the count scales.

| N | non-incident relations | arity-2 flips | arity-3 (witness `a`) flips |
|---|---|---|---|
| 3 | 1 | **0** | 1,024 |
| 4 | 3 | **0** | 6,144 |
| 5 | 6 | **0** | 24,576 |

Flip counts scale with `C(N-1, 2)` — 1 : 3 : 6 — so the number is an artifact of
system size, while the zero is not.

**Gate function.** Not a knife-edge: **240/256 (93.8%)** of all arity-3 gates at
M=2 admit a flip, and **4000/4000** sampled at M=3. The property is generic
among gates that read `a`, not a special construction.

**Seed.** For a fixed gate (parity of `c,d,a`), **16/16** configuration-and-
perturbation cases flip — seed-independent for that gate. The best gates reach
the maximum 16 of 16, so seed-dependence is a property of the gate chosen, not
of the phenomenon.

## What this settles, and what it does not

Settled: the minimum arity is 3; arity 2 is impossible under I1–I6; the real
condition is witness membership; the result is generic over gates, independent
of seeds and of topology except in count.

Not settled: this is S3's minimality only. **S4's minimality claim (C16) remains
untested** — no search has been done over conjoining structures. And the
impossibility says nothing about arity 2 *with dynamics*, which v0.1 already
measured and which I4 makes explicit.


---

# F13 — MEASUREMENT RECORD: S4 minimality search

Run with `PYTHONPATH=. python3 audit/s4_minimality.py`; figures pinned by
`tests/test_s4_minimality.py`. This discharges audit item **E2** and settles
**C16**.

## Two targets, kept separate

v0.1 entangles them. They are measured independently here and **they do not
coincide.**

- **T1 CONJUNCTION** — non-zero causal influence between two bounded state
  spaces, with closure, partition and separability intact.
- **T2 NONTRIVIAL TRANSLATION** — the interface map is not the identity on the
  source's reachable set.
- **T3 RELATIONAL CONJUNCTION** — cross-universe *relations* change, with no
  state crossing the boundary at all. (Not in v0.1; it emerged from the search.)

## Headline: "the smallest conjoining structure" is not well defined

**The claim as v0.1 states it is disproved.** There is no single smallest
conjoining structure, because the minimum depends entirely on which target
behaviour is named, and v0.1 names none:

| target | smallest structure found | cross-links needed |
|---|---|---|
| T1 state influence | one directed link carrying **≥ 1 bit** on the reachable set | **1** |
| T2 nontrivial translation | not required for T1 at all — see below | — |
| T3 relational influence | **no link whatsoever**; a gate whose witness set contains the perturbed substrate | **0** |

T1 and T3 have different minima, and neither is "one directed link carrying a
translation between the state spaces". The v0.1 claim is not merely unproven; it
names the wrong component.

## Coverage

| search | space | coverage |
|---|---|---|
| B | every map `τ : Z₅ → Z₇` | **exhaustive**, 7⁵ = 16,807 |
| C | every map `τ : Z₇ → Z₅` | **exhaustive**, 5⁷ = 78,125 |
| A | interface counts 0–2 × both directions | **exhaustive** |
| I | boundary pairs `(src, dst)` | **exhaustive**, 9 of 9 |
| E | modulus pairs | 7 chosen pairs spanning expand/shrink/equal |
| H | seeds | **sampled**, 1,000 |
| combined forward × reverse map pairs | 7⁵ × 5⁷ ≈ 1.3 × 10⁹ | **not attempted**; directions measured independently |

## The exact condition for T1

Influence occurs **iff the map takes at least two values on the source's
reachable set** — not iff it is non-identity, and not iff it is "a translation".

| values `τ` takes on R | maps | maps producing influence |
|---|---|---|
| 1 | 49 | **0** |
| 2 | 2,058 | **2,058** |
| 3 | 8,820 | **8,820** |
| 4 | 5,880 | **5,880** |

Predicate `|τ(R)| ≥ 2` agrees with observed influence in **16,807/16,807
(100.0%)** forward maps and **78,125/78,125 (100.0%)** reverse maps. Both
exhaustive.

`R`, the reachable set, is the right domain and not `Z₅`: a2 visits only
`{0,2,3,4}`, 4 of 5 states, across the reference and perturbed runs. A map
non-constant on `Z₅` but constant on `R` carries nothing.

## Smallest witnesses

| target | smallest witness | result |
|---|---|---|
| T1 | `τ = (0,0,0,0,1)` — two values on R, i.e. **one bit** | influence 9 cells, first at step 5 |
| T1 with T2 false | `τ = (0,0,2,3,4)` — the **identity on R** | influence 13 cells |
| T3 | mediated gate, **zero** cross-links | 2 non-incident cross-universe relations move |

The second row is the decisive one: a map that is the identity on everything the
source actually reaches still conjoins. **T2 is not necessary for T1.**

## The trap: interface count is syntax, not information

Exactly parallel to F9's arity trap.

| structure | interfaces | values carried on R | influence |
|---|---|---|---|
| two interfaces, both constant | **2** | 1 / 1 | **0 and 0** |
| one interface, one bit | **1** | 2 | **11** |
| one interface, full inclusion | **1** | 4 | 13 |

Two interfaces carrying zero bits conjoin nothing. Counting interfaces measures
syntax. The unit is carried information on the reachable set.

## Why v0.1's forward translation was vacuous

Not a poor choice — **forced**. For `m_src ≤ m_dst` the canonical map `s mod
m_dst` *is* the identity, necessarily, and no alternative canonical map exists.

| m_src | m_dst | relation | canonical map | identity? |
|---|---|---|---|---|
| 5 | 7 | expanding | `[0,1,2,3,4]` | **yes** |
| 7 | 5 | shrinking | `[0,1,2,3,4,0,1]` | no |
| 5 | 5 | equal | `[0,1,2,3,4]` | **yes** |
| 4 | 8 | expanding | `[0,1,2,3]` | **yes** |
| 11 | 3 | shrinking | `[0,1,2,0,1,2,0,1,2,0,1]` | no |

Every expanding or equal direction gives the identity. P1's finding generalises:
a translation can only do work when it **shrinks**.

## The measurement, tested against itself

v0.1's `bound_violations` counts states *above* a bound and is therefore blind to
contraction. The replacement reports reached-state count against the modulus in
both directions, and is applied identically to collapse and conjunction.

| regime | universe | reached/modulus | escape | contraction | v0.1 metric |
|---|---|---|---|---|---|
| conjoined | U1 | 5/5 | no | no | 0 |
| conjoined | U2 | 7/7 | no | no | 0 |
| collapse to max 7 | U1 | 6/5 | **yes** | no | 4 |
| collapse to min 5 | U2 | 6/7 | no | **yes** | **0** |
| collapse to lcm 35 | U1 | 19/5 | **yes** | no | 20 |

The `collapse to min 5` row is the test of the test: real contraction, **0** from
the old metric, detected by the new one. The new metric flags conjunction as
neither escaping nor contracting — but it reaches that verdict by the same
criterion it applies to every collapse, so the verdict is earned rather than
assumed.

One further result, found by a crash rather than by design: under **collapse to
lcm 35** the source leaves the interface map's domain **9 times**, so the map is
no longer total and must be extended. Collapse does not merely re-bound states —
**it destroys the well-typedness of any interface defined over the original
spaces.**

## What a "universe" needs

Closure, partition and separability hold across every internal structure tried,
**including no internal couplings at all**:

| internal structure | influence | closure | partition | separable |
|---|---|---|---|---|
| v0.1 chain, `d+s+1` | 13 | yes | yes | yes |
| chain, `d+2s` | 8 | yes | yes | yes |
| cycle | 14 | yes | yes | yes |
| U1 chain / U2 star | 14 | yes | yes | yes |
| **no internal couplings** | **0** | yes | yes | yes |

A universe requires nothing beyond a **bound and a membership map**. Closure,
partition and separability follow from those two alone. Influence requires
internal dynamics only because with none, the boundary substrate never varies and
so carries nothing.

## Seed dependence

| structure | seeds showing influence |
|---|---|
| no interface | **0 / 1000** |
| one interface, constant map | **0 / 1000** |
| one interface, inclusion map | **1000 / 1000** |

Seed-independent over 1,000 seeds (the v0.1 seed plus 999 random).

## Component verdicts

| component | verdict | evidence |
|---|---|---|
| a cross-link exists | **NECESSARY** for T1 | 0 links → 0 influence; 1 link → 13 |
| `τ` non-constant on the reachable set | **NECESSARY** for T1 | 0 of 49 constant maps produce influence |
| `τ` is *not* the identity (T2) | **NEITHER** | identity-on-R gives influence 13 |
| `τ` carries the full source state | **NEITHER** | 1 bit gives 11 vs full 13 |
| a second, reverse link | **NEITHER** for T1, **NECESSARY** for mutual | one link → reverse influence 0; two → 11 |
| the specific boundary pair `a2→b0` | **NEITHER** | 9 of 9 `(src,dst)` pairs produce influence |
| a cross-link at all, for **T3** | **NEITHER** | mediated gate moves 2 cross-universe relations with 0 links |

**Sufficient set for T1:** one directed cross-link whose map takes ≥ 2 values on
the source's reachable set. **Minimal:** removing the link, or reducing the map
to one value, destroys the behaviour; no smaller component set was found.

## Assumptions under which the T1 minimality holds

| # | Assumption | If violated |
|---|---|---|
| J1 | The target is **state** influence between universes | T3 needs no link at all |
| J2 | Influence is measured over a fixed horizon (T = 8 steps) | A shorter horizon can miss a slow channel — the 1-bit witness first shows at step 5 |
| J3 | The source substrate varies, i.e. the universe has internal dynamics | With none, the link carries nothing regardless of `τ` |
| J4 | Information is judged on the **reachable** set, not the full state space | Judging on `Z₅` misclassifies maps constant on R |
| J5 | Both universes' bounds are fixed across the measurement | Collapse breaks the map's domain (9 escapes at lcm 35) |
| J6 | Cross-links are the only channel considered | A shared gate is a second channel — this is J1 restated structurally |


---

# A. INSTRUMENT AUDIT

| # | Finding | Severity |
|---|---|---|
| A1 | **Minimality is the instrument's organising claim and no bench tested it.** Asserted at S0, S1, S3, S4 with no search performed. **Discharged for S3** (F9: minimum arity 3, condition is witness membership) **and S4** (F13: no unique minimum exists; C16 disproved). Both searches found the stated component was the wrong one. **S0 and S1 remain unsearched**, and on the record so far the prior should be that their minimality claims are also wrong. | **Critical → High** |
| A2 | **Two of five benches rest on tautologies.** S2's stored-topology control reads a constant function; S4's conjoined closure re-checks an invariant `step()` enforces. Both are reported in the same register as results that could have failed. | **High** |
| A3 | **S2's non-incidence is a theorem presented as a measurement.** P3: 0 failures in 248,832 exhaustive cases. A 12-point sample of a provable statement adds nothing and implies contingency where there is none. | **High** |
| A4 | **Seed drift between notebook and artifact.** `FINDINGS.md` fixes seeds `{a:0,b:2,c:5,d:9}`; the published bench seeds from live commits. The artifact therefore cannot reproduce 17, 8, or 3, and says nothing about this. Two authorities disagree and neither declares precedence. | **High** |
| A5 | **Three headline numbers are parameter artifacts** — `12/12` (P8, the transducer), `8` (P2, the threshold), `3` (P5, the collapse modulus) — and `17` is a typical value, not a constant (P6: 43.1% of seeds). All four are stated as findings without their dependence. | **High** |
| A6 | **Sweep sums are presented as scalars.** 17 and 8 are sums over 12 independent perturbations against one base — counts of (perturbation, pair) incidents, not relations in any configuration. | Medium |
| A7 | **No bench reports a distribution.** Every result compares one perturbed configuration to one base. Nothing establishes whether any result is typical or special; P6 had to be run to find out. | Medium |
| A8 | **Live and counterfactual values share one visual register.** The S1 tile row places `12/12 reachable` (hypothetical sweep) beside `population` (live), identically styled. | Medium |
| A9 | **Semantic colour editorialises.** Rose marks violation; it is applied to legal states (S0 equal states, S4 collapsed cells judged by the abandoned rule). | Medium |
| A10 | **The S3 control implies commensurability it does not have.** Three segmented options span two gate systems and one protocol change; their tallies are rendered identically. | Medium |
| A11 | **The ring projection can hide substrates.** Equal states draw at one point, one node occluding the other — the display reproduces S0's collapse as an apparent property of the system. | Medium |

# B. CLAIM REGISTER

| ID | Claim as made by v0.1 | Status | Evidence |
|---|---|---|---|
| C1 | A label is the smallest primitive resisting collapse | **Falsified as necessity** | P7: 144/144 recovered from dynamics alone, 12/12 at equal states |
| C2 | State alone collapses two substrates into one | Survives, **vacuously** | set cardinality; holds for all values |
| C3 | Coupling preserves population and labels; source untouched | **Survives** (structural) | EXP1; unaffected across all transducers in P8 |
| C4 | 12/12 destination states reachable ⇒ state genuinely crosses | **Artifact** | P8: 12, 3, 3, 1 across transducers |
| C5 | Coupling is the smallest non-merging interaction | **Untested** | no minimality search exists |
| C6 | Stored edges never respond to state | Survives, **tautologically** | `edge_set` ignores its argument |
| C7 | A pairwise gate changes only incident relations | **Survives, promoted to theorem** | P3: 0/248,832 |
| C8 | 17 changed relations | **Weakened to typical** | P6: 15–21, mean 17.5, 43.1% exactly 17 |
| C9 | A configuration-wide term is the smallest addition reaching non-incident relations | **Falsified, now replaced** | P4; superseded by C17/C18 (F9) |
| C17 | Minimum arity for non-incident change is 3, and a relation moves iff `a` is in its witness set | **Measured** | F9: 4/4 witness sets; failures = gates ignoring `a`, exactly |
| C18 | No arity-2 gate can move a non-incident relation under I1–I6 | **Measured + proved** | F9: 249,600 exhaustive checks, 0 flips, inputs identical in 100% |
| C10 | 8 non-incident changes under mediation | **Artifact** | P2: 0/0/8/4/0/0 across thresholds |
| C11 | Propagation reaches non-incident relations but decays by step 3 | Survives; **decay is an artifact** | Z₁₂ wraparound with `d+s` |
| C12 | Conjoining keeps each universe inside its own space | Survives, **tautologically** | `step()` applies the modulus |
| C13 | Collapsing breaks the smaller state space | **Falsified as general** | P5: 0 at mod 5, 3 at mod 7, 31 at lcm |
| C14 | The interface carries a translation between state spaces | **Falsified as the operative component** | P1; F13 shows expanding directions force the identity, and 1 bit suffices |
| C15 | No interface ⇒ no influence; one ⇒ one-way | **Survives** (structural) | no cross edge in the coupling graph |
| C16 | One directed translating link is the smallest conjoining structure | **Disproved as stated** | F13: no unique minimum exists — T1 needs 1 link, T3 needs 0; and the operative component is carried information, not translation |
| C19 | T1 occurs iff the interface map takes ≥2 values on the source's reachable set | **Measured** | F13: 16,807/16,807 and 78,125/78,125 exhaustive, 100% agreement |
| C20 | A nontrivial translation (T2) is not necessary for conjunction (T1) | **Measured** | F13: identity-on-R map gives influence 13 |
| C21 | A universe requires nothing beyond a bound and a membership map | **Measured** | F13: closure, partition, separability hold with no internal couplings |

Survives as stated: **C3, C7, C15**. Survives vacuously: **C2, C6, C12**.
Falsified or materially weakened: **C1, C9, C13, C14**. Artifacts: **C4, C8, C10**.
Untested: **C5, C16**.

# C. ASSUMPTION REGISTER

| ID | Assumption | Where | Load-bearing for | Tested? |
|---|---|---|---|---|
| X1 | `sid` differs in kind from `state` | S0 | C1, C2 | No — it is a naming convention |
| X2 | Identity is declared, not earned by behaviour | S0 | C1 | **Falsified** by P7 |
| X3 | Directedness is a property of the operation | S1 | C3 | No — declared by dataclass fields |
| X4 | `(d+s) mod 12` is representative of transducers | S1 | C4 | **Falsified** by P8 |
| X5 | The gate is symmetric, memoryless, arity 2 | S2 | C7 | Arity is the load-bearing part (P3) |
| X6 | Symmetric difference is the right change metric | S2, S3 | C8, C10 | No — appearance and disappearance are conflated |
| X7 | One base configuration is representative | S2, S3, S4 | C8, C10, C13 | **Falsified** by P6 |
| X8 | The mediating term must read the whole configuration | S3 | C9 | **Falsified** by P4; replaced by F9's witness condition |
| X17 | Arity can be read off a gate's signature | F9 | C18 | **Falsified** — derived arguments give 72 flips at 2 parameters (I6) |
| X18 | The arity-2 impossibility holds without qualification | F9 | C18 | **Bounded** — holds only under I1–I6; I4 (no dynamics) is the live escape |
| X9 | A linear sum is a neutral choice of medium | S3 | C9, C10 | No — gives every substrate equal leverage |
| X10 | The chain `a→b→c→d` is a neutral coupling graph | S3 | C11 | No — never varied |
| X11 | Collapse means re-bounding to the maximum modulus | S4 | C13 | **Falsified as neutral** by P5 |
| X12 | Exceeding a bound is the only way to break a space | S4 | C13 | **Falsified** by F13 — replacement metric detects contraction the old one scored 0 |
| X19 | Interface count measures conjoining capacity | S4 | C16 | **Falsified** by F13 — 2 constant interfaces give 0, 1 one-bit interface conjoins |
| X20 | "Smallest conjoining structure" is well defined without naming a target | S4 | C16 | **Falsified** by F13 — T1 and T3 have different minima |
| X13 | The two universes are independent systems | S4 | C13, C15 | No — identical structure, differing only in modulus |
| X14 | Differing-substrate count measures influence | S4 | C15 | No — saturates at 3 |
| X15 | 6 steps is a sufficient horizon | S4 | C13, C15 | No — unjustified |
| X16 | Live seeds and notebook seeds are interchangeable | artifact | all displayed figures | No — see A4 |

# D. FALSIFICATION TESTS

Tests already run, with outcomes, are in `audit/probes.py`. Ordered by what they
would cost to make standing parts of the notebook.

| ID | Test | Target | Outcome |
|---|---|---|---|
| F1 | Recover identity from unlabelled state multisets under distinct update rules | C1, X2 | **Ran — C1 falsified** (P7) |
| F2 | Sweep transducers bijective → constant, holding structure fixed | C4, X4 | **Ran — C4 is an artifact** (P8) |
| F3 | Exhaustive non-incidence over Z₁₂⁴ × 12 | C7 | **Ran — C7 promoted to theorem** (P3) |
| F4 | Arity-3 witness gate in place of the global sum | C9, X8 | **Ran — C9 falsified** (P4) |
| F5 | Collapse at min / max / lcm modulus | C13, X11 | **Ran — C13 falsified as general** (P5) |
| F6 | Distribution of the EXP2 sweep total over random seeds | C8, X7 | **Ran — C8 weakened** (P6) |
| F7 | Threshold sweep of the mediated non-incident count | C10 | **Ran — C10 is an artifact** (P2) |
| F8 | Identity-vs-`s%7` substitution on the forward interface | C14 | **Ran — C14 weakened** (P1) |
| F9 | Minimum gate arity at which non-incident change appears (sweep 2→N) | C9, C16 | **Ran — minimum arity 3; arity 2 impossible under I1–I6; condition is witness membership, not size.** C16 still untested |
| F10 | Per-universe *reachable state count* against its modulus, under each collapse | X12 | **Ran inside F13** — metric is two-sided; collapse-to-min contraction scored 0 by the old metric |
| F13 | S4 minimality search: interfaces 0–2, all maps both directions, moduli, collapse regimes | C16, C14, X12 | **Ran — C16 disproved as stated.** No unique minimum; T1 needs one link carrying ≥1 bit, T3 needs none |
| F11 | Vary the coupling graph (chain, star, cycle, disconnected) and re-measure propagation | C11, X10 | Not run |
| F12 | Replay the notebook's fixed seeds through the artifact and diff every figure | A4, X16 | Not run — required before the artifact can cite `FINDINGS.md` |

# E. NEXT EXPERIMENTS

Ordered by how much of the audit each one discharges. None are redesigns; each
is a measurement the instrument currently asserts without.

1. ~~**Minimality sweep (F9).**~~ **Done** — see the F9 measurement record above.
   Minimum arity 3; arity 2 impossible under six stated assumptions; the
   operative condition is witness membership, not witness size. A1 is discharged
   for S3 only. **S4's minimality (C16) is now the outstanding instance** and is
   promoted to item 2.
2. ~~**Minimality search over conjoining structures (C16, A1).**~~ **Done** — see
   the F13 measurement record above. C16 is disproved as stated: the minimum
   depends on the target behaviour, and v0.1 names none. A1 is now discharged for
   S3 and S4; **S0 and S1 remain unsearched** and are the last outstanding
   instances.
3. **Seed-distribution reporting (F6, generalised).** Replace every scalar
   headline with a distribution over seeds, and state which figures are
   invariant, which are typical, and which are artifacts. Discharges A5, A6, A7
   and X7 across all benches.
4. **Reconcile notebook and artifact (F12).** Either pin the artifact to the
   notebook's seeds and treat live commits as an additional condition, or state
   on the page that live seeding makes `FINDINGS.md`'s figures
   non-reproducible there. Discharges A4 and X16. Required before the bench can
   honestly point at the repo.
5. **Two-sided space test (F10).** Measure reachable states per universe against
   its modulus, under collapse to min, max and lcm. Discharges X12 and replaces
   C13 with a claim that survives P5.
6. **Coupling-graph variation (F11).** Chain, star, cycle, disconnected.
   Discharges X10 and establishes whether C11's step-1 reach is structural or an
   artifact of the chain.
7. **Genuinely distinct universes (X13).** Give U1 and U2 different internal
   coupling structures and different transducers, not only different moduli, and
   re-run the conjunction measurements. Until this is done, S4 measures one
   system at two sizes.
8. **Replace the saturating influence metric (X14).** Count differing steps, or
   time-to-first-difference, instead of differing substrates. The current metric
   cannot distinguish strong from weak coupling.

Not yet in scope, and deliberately so: any change to the published bench. v0.1
stands as audited until items 2–4 are measured.
