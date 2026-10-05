# Validation report

1586/1586 checks passed across 60 exported portfolios.

Checks reload all 100 decisions per run; verify binary values, solver status, budget, logical pairs, totals, selected-row exports, goals, nonnegative deviations, normalized reporting and objectives.

An independently constructed SciPy/HiGHS model cross-checks all 60 CBC portfolio objectives (including payoff tie-breaks and fixed-target GP). Identical project sets are not required for tied optima.

Score formulas, preserved IPS, original raw/base/notebook/result artifacts, payoff targets, configuration snapshot and IP budget monotonicity are also checked.

See validation_report.csv for individual checks, independent_solver_validation.csv for solver objective differences and run_metadata.json for versions, tolerances and input hash.
