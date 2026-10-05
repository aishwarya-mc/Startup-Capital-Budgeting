# Sensitivity analysis

All changes are destination minus source. Project identities, additions/removals,
Jaccard overlap, aggregate measures and sector counts/costs are exported in the CSVs.
Sector tables include zero-selection sectors. Weights/strategic tiers and logical pairs are scenario inputs.

## Budget sensitivity (baseline, $25M to $75M)

- GP/balanced: projects +12, potential +455.01, risk +750.00, strategy +775; 12 added/0 removed; overlap 0.600.
- GP/potential_focused: projects +13, potential +440.84, risk +908.33, strategy +950; 13 added/0 removed; overlap 0.649.
- GP/risk_focused: projects +5, potential +255.01, risk +187.50, strategy +400; 5 added/0 removed; overlap 0.583.
- GP/strategy_focused: projects +14, potential +437.51, risk +1025.00, strategy +900; 14 added/0 removed; overlap 0.600.
- IP/single_objective: projects +16, potential +477.51, risk +1262.50, strategy +775; 16 added/0 removed; overlap 0.600.

## Priority sensitivity (baseline, $50M; relative to balanced)

- potential_focused: potential +119.16, risk +441.67, strategy -50; 6 added/1 removed.
- risk_focused: potential -305.83, risk -1395.83, strategy -950; 2 added/17 removed.
- strategy_focused: potential -11.67, risk +420.83, strategy +200; 6 added/3 removed.

## Logical constraints

Original commented relationships are assumptions; baseline leaves them disabled.
Recalibrated comparisons recompute payoff references after adding constraints. Fixed-target comparisons
retain baseline targets/scales and weights, isolating changes in feasibility. Both are reported.

- $25M, balanced, fixed targets: potential -0.00, risk +0.00, strategy -25; 2 added/2 removed.
- $50M, balanced, fixed targets: potential -17.49, risk -100.00, strategy -150; 3 added/4 removed.
- $75M, balanced, fixed targets: potential -22.50, risk +12.50, strategy -75; 2 added/2 removed.

## Interpretation limits

Budget expansion cannot reduce the optimal IP objective; GP goals/scales change with budget.
Risk-focused portfolios are smaller because total risk is additive. Strategy-focused portfolios
favor the assumed software/digital mandate, not observed superior sectors. Membership can change
under ties without meaningful objective changes. No claim of unique optimal portfolios is made.
Sector composition and all sector deltas appear in sector_composition.csv and sensitivity_sector_changes.csv.
