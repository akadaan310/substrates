"""Run every experiment in order and print a one-line summary of each."""
import exp0_identity, exp1_interaction, exp2_static_vs_gated
import exp3_nonincident, exp4_conjoin_vs_collapse

for mod in (exp0_identity, exp1_interaction, exp2_static_vs_gated,
            exp3_nonincident, exp4_conjoin_vs_collapse):
    mod.main()
    print()
