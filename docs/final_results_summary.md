# Final Results Summary

All tables below are generated from the frozen CSVs in `results/optimization/`; they are not transcribed from old results. Display rounding is for readability only. USD values denote the **Investment Cost Proxy**. IPS, Funding-History Risk Proxy and strategy totals are additive score-points. Every exported main/anchor/fixed-target solution has status **Optimal**.

## 1. Final Integer Programming results

The authoritative baseline has budget and binary constraints only. It maximizes total IPS.

| Budget | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 |
| $50M | IP | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625.00 |
| $75M | IP | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900.00 |

Source: [ip_summary.csv](../results/optimization/ip_summary.csv), `logical_scenario=baseline`. Root-level historical IP result files are superseded for baseline reporting. Their old $50M/$75M totals describe neither the authoritative baseline nor a newly discovered error in this finalization.

## 2. Final Goal Programming results

GP minimizes weighted normalized potential/strategic shortfall and total risk-proxy excess. `baseline` has no logical pairs; `assumed_logic` adds the explicitly hypothetical prerequisite and exclusion. All 24 validated main GP scenarios are retained:

| Budget | Logic | Priority | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points | P shortfall | R excess | S shortfall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | assumed_logic | balanced | 18 | $24,779,429 | 99.12% | 570.01 | 1,337.50 | 1,200.00 | 136.66 | 1,337.50 | 275.00 |
| $25M | assumed_logic | potential_focused | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 | 0.00 | 1,879.17 | 350.00 |
| $25M | assumed_logic | risk_focused | 7 | $23,434,328 | 93.74% | 374.18 | 266.67 | 425.00 | 332.49 | 266.67 | 1,050.00 |
| $25M | assumed_logic | strategy_focused | 22 | $24,515,477 | 98.06% | 576.67 | 1,854.17 | 1,425.00 | 130.00 | 1,854.17 | 50.00 |
| $50M | assumed_logic | balanced | 24 | $49,826,951 | 99.65% | 801.69 | 1,704.17 | 1,575.00 | 156.65 | 1,704.17 | 400.00 |
| $50M | assumed_logic | potential_focused | 32 | $49,864,510 | 99.73% | 941.68 | 2,504.17 | 1,700.00 | 16.66 | 2,504.17 | 275.00 |
| $50M | assumed_logic | risk_focused | 9 | $49,025,561 | 98.05% | 480.85 | 333.33 | 600.00 | 477.49 | 333.33 | 1,375.00 |
| $50M | assumed_logic | strategy_focused | 28 | $49,876,722 | 99.75% | 753.34 | 2,295.83 | 1,925.00 | 205.00 | 2,295.83 | 50.00 |
| $75M | assumed_logic | balanced | 30 | $74,488,149 | 99.32% | 1,002.52 | 2,100.00 | 1,925.00 | 165.82 | 2,100.00 | 400.00 |
| $75M | assumed_logic | potential_focused | 37 | $74,984,233 | 99.98% | 1,124.18 | 2,829.17 | 2,000.00 | 44.16 | 2,829.17 | 325.00 |
| $75M | assumed_logic | risk_focused | 10 | $74,376,161 | 99.17% | 546.68 | 379.17 | 800.00 | 621.66 | 379.17 | 1,525.00 |
| $75M | assumed_logic | strategy_focused | 33 | $74,729,068 | 99.64% | 935.85 | 2,620.83 | 2,250.00 | 232.49 | 2,620.83 | 75.00 |
| $25M | baseline | balanced | 18 | $24,833,829 | 99.34% | 570.01 | 1,337.50 | 1,225.00 | 136.66 | 1,337.50 | 250.00 |
| $25M | baseline | potential_focused | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 | 0.00 | 1,879.17 | 350.00 |
| $25M | baseline | risk_focused | 7 | $23,665,331 | 94.66% | 365.84 | 283.33 | 525.00 | 340.83 | 283.33 | 950.00 |
| $25M | baseline | strategy_focused | 21 | $24,635,477 | 98.54% | 566.67 | 1,741.67 | 1,425.00 | 140.00 | 1,741.67 | 50.00 |
| $50M | baseline | balanced | 25 | $49,897,820 | 99.80% | 819.18 | 1,804.17 | 1,725.00 | 149.16 | 1,804.17 | 275.00 |
| $50M | baseline | potential_focused | 30 | $49,991,331 | 99.98% | 938.34 | 2,245.83 | 1,675.00 | 30.00 | 2,245.83 | 325.00 |
| $50M | baseline | risk_focused | 10 | $49,304,928 | 98.61% | 513.35 | 408.33 | 775.00 | 454.99 | 408.33 | 1,225.00 |
| $50M | baseline | strategy_focused | 28 | $49,914,274 | 99.83% | 807.51 | 2,225.00 | 1,925.00 | 160.83 | 2,225.00 | 75.00 |
| $75M | baseline | balanced | 30 | $74,862,396 | 99.82% | 1,025.02 | 2,087.50 | 2,000.00 | 159.16 | 2,087.50 | 375.00 |
| $75M | baseline | potential_focused | 37 | $74,756,125 | 99.67% | 1,147.51 | 2,787.50 | 2,075.00 | 36.67 | 2,787.50 | 300.00 |
| $75M | baseline | risk_focused | 12 | $73,820,558 | 98.43% | 620.85 | 470.83 | 925.00 | 563.33 | 470.83 | 1,450.00 |
| $75M | baseline | strategy_focused | 35 | $74,879,068 | 99.84% | 1,004.18 | 2,766.67 | 2,325.00 | 180.00 | 2,766.67 | 50.00 |

Source: [gp_summary.csv](../results/optimization/gp_summary.csv). Target values are documented in [methodology, section 14](methodology.md#14-gp-target-generation); all six goal deviations and objectives remain in that CSV. For the balanced baseline, they are:

| Budget | dP- | dP+ | dR- | dR+ | dS- | dS+ | P achievement | R achievement | S achievement | GP objective |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | 136.660000 | 0.000000 | 0.000000 | 1337.500000 | 250.000000 | 0.000000 | 0.806614 | 0.291391 | 0.830508 | 0.357162 |
| $50M | 149.160000 | 0.000000 | 0.000000 | 1804.166700 | 275.000000 | 0.000000 | 0.845963 | 0.342944 | 0.862500 | 0.316198 |
| $75M | 159.160000 | 0.000000 | 0.000000 | 2087.500000 | 375.000000 | 0.000000 | 0.865595 | 0.335544 | 0.842105 | 0.318919 |

Achievement equals `1-undesirable_deviation/scale`, not a probability. P/S scales equal their targets; R uses the payoff risk range because its target is zero. Six decimal places expose the numerical reporting precision.

## 3. Authoritative IP vs GP comparison

This is the submission's main comparison table: baseline IP against baseline **balanced GP**, with the same 100 projects and budget. It is a view of the existing [ip_vs_gp_comparison.csv](../results/optimization/ip_vs_gp_comparison.csv), not a separately calculated optimization result.

| Budget | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points | P shortfall | R excess | S shortfall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 | 0.00 | 1,879.17 | 350.00 |
| $25M | GP balanced | 18 | $24,833,829 | 99.34% | 570.01 | 1,337.50 | 1,225.00 | 136.66 | 1,337.50 | 250.00 |
| $50M | IP | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625.00 | -0.00 | 2,745.83 | 375.00 |
| $50M | GP balanced | 25 | $49,897,820 | 99.80% | 819.18 | 1,804.17 | 1,725.00 | 149.16 | 1,804.17 | 275.00 |
| $75M | IP | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900.00 | -0.00 | 3,141.67 | 475.00 |
| $75M | GP balanced | 30 | $74,862,396 | 99.82% | 1,025.02 | 2,087.50 | 2,000.00 | 159.16 | 2,087.50 | 375.00 |

For IP, deviations are evaluated after optimization against the corresponding GP targets; they are not part of the IP objective. P shortfall is undesirable potential deviation, R excess is undesirable total Funding-History Risk Proxy deviation, S shortfall is undesirable strategic deviation.

Changes below are **balanced GP minus IP**:

| Budget | Change in projects | Change in USD proxy | Change in IPS | Change in risk proxy | Change in strategy |
| --- | --- | --- | --- | --- | --- |
| $25M | -6 | -95,481.00 | -136.66 | -541.67 | +100.00 |
| $50M | -9 | -83,014.00 | -149.16 | -941.67 | +100.00 |
| $75M | -10 | -126,895.00 | -159.16 | -1,054.17 | +100.00 |

IP maximizes one primary objective subject to hard constraints. GP balances several potentially conflicting aspiration levels. Here balanced GP sacrifices IPS and selects fewer projects, lowers total Funding-History Risk Proxy and improves strategic alignment. Some proxy reduction comes from fewer projects, not evidence of lower actual failure risk. GP is not inherently better than IP.

## 4. Budget sensitivity

The preceding tables give actual cost, utilization and scores at every budget. The following differences show both adjacent budget increases and the full $25M-to-$75M comparison:

| Budget change | Model / priority | Projects change | USD proxy change | IPS change | Risk proxy change | Strategy change | Added / removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M to $50M | GP / balanced | +7 | +25,063,991.00 | +249.17 | +466.67 | +500.00 | 7 / 0 |
| $25M to $75M | GP / balanced | +12 | +50,028,567.00 | +455.01 | +750.00 | +775.00 | 12 / 0 |
| $50M to $75M | GP / balanced | +5 | +24,964,576.00 | +205.84 | +283.33 | +275.00 | 5 / 0 |
| $25M to $50M | IP / single_objective | +10 | +25,051,524.00 | +261.67 | +866.67 | +500.00 | 10 / 0 |
| $25M to $75M | IP / single_objective | +16 | +50,059,981.00 | +477.51 | +1,262.50 | +775.00 | 16 / 0 |
| $50M to $75M | IP / single_objective | +6 | +25,008,457.00 | +215.84 | +395.83 | +275.00 | 6 / 0 |

For baseline IP and balanced GP, increasing budget increases selected project count, expenditure proxy, IPS, total Funding-History Risk Proxy and strategic points in these observed runs. More available capital permits a larger portfolio, but each additional selected project contributes proxy exposure. IP optimal IPS is mathematically nondecreasing as the feasible set expands; selection counts or nested membership are not guaranteed in general. GP reference targets are recalibrated with budget, so its objective values across budgets are not a common quality score.

## 5. GP priority sensitivity

Verified decision-maker preference scenarios:

| Priority scenario | Potential | Risk proxy | Strategy |
| --- | --- | --- | --- |
| balanced | 1/3 | 1/3 | 1/3 |
| potential_focused | 0.60 | 0.20 | 0.20 |
| risk_focused | 0.20 | 0.60 | 0.20 |
| strategy_focused | 0.20 | 0.20 | 0.60 |

Within each budget/configuration, all priorities use the same target values and scales. Baseline differences relative to balanced GP are:

| Budget change | Model / priority | Projects change | USD proxy change | IPS change | Risk proxy change | Strategy change | Added / removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M to $25M | GP / potential_focused | +6 | +95,481.00 | +136.66 | +541.67 | -100.00 | 9 / 3 |
| $25M to $25M | GP / risk_focused | -11 | -1,168,498.00 | -204.17 | -1,054.17 | -700.00 | 2 / 13 |
| $25M to $25M | GP / strategy_focused | +3 | -198,352.00 | -3.34 | +404.17 | +200.00 | 5 / 2 |
| $50M to $50M | GP / potential_focused | +5 | +93,511.00 | +119.16 | +441.67 | -50.00 | 6 / 1 |
| $50M to $50M | GP / risk_focused | -15 | -592,892.00 | -305.83 | -1,395.83 | -950.00 | 2 / 17 |
| $50M to $50M | GP / strategy_focused | +3 | +16,454.00 | -11.67 | +420.83 | +200.00 | 6 / 3 |
| $75M to $75M | GP / potential_focused | +7 | -106,271.00 | +122.49 | +700.00 | +75.00 | 9 / 2 |
| $75M to $75M | GP / risk_focused | -18 | -1,041,838.00 | -404.17 | -1,616.67 | -1,075.00 | 2 / 20 |
| $75M to $75M | GP / strategy_focused | +5 | +16,672.00 | -20.84 | +679.17 | +325.00 | 9 / 4 |

Potential-focused GP generally preserves more IPS at greater total proxy exposure. Risk-focused GP selects **7/10/12 projects at $25M/$50M/$75M**, respectively, trading potential and alignment for lower additive exposure. Strategy-focused GP sacrifices some potential and permits more proxy exposure to favor the assumed mandate. These are observed preference trade-offs, not a ranking of investors.

For a concrete composition comparison, these are selected sector counts at $50M, baseline:

| Sector | balanced | potential_focused | risk_focused | strategy_focused |
| --- | --- | --- | --- | --- |
| advertising | 1 | 1 | 0 | 2 |
| biotech | 1 | 3 | 0 | 0 |
| ecommerce | 3 | 3 | 1 | 4 |
| enterprise | 5 | 4 | 2 | 5 |
| games_video | 0 | 2 | 0 | 2 |
| hardware | 2 | 2 | 0 | 2 |
| medical | 2 | 4 | 1 | 1 |
| mobile | 4 | 4 | 2 | 4 |
| software | 5 | 5 | 3 | 5 |
| web | 2 | 2 | 1 | 3 |

Zero entries mean no selected projects in that sector, not that the sector is inherently undesirable. Full 420-row sector composition and 750 sector-change rows are in [sector_composition.csv](../results/optimization/sector_composition.csv) and [sensitivity_sector_changes.csv](../results/optimization/sensitivity_sector_changes.csv).

## 6. Logical-constraint scenario

The exact **Scenario-based modelling assumptions** are P005 requires P004 (`x_P005<=x_P004`) and P003/P004 are mutually exclusive (`x_P003+x_P004<=1`). No Crunchbase source establishes these relationships. They illustrate how decision-maker-supplied business interdependencies could be imposed.

| Budget | Logic | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | assumed_logic | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 |
| $25M | baseline | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 |
| $50M | assumed_logic | IP | 33 | $49,926,434 | 99.85% | 958.34 | 2,633.33 | 1,475.00 |
| $50M | baseline | IP | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625.00 |
| $75M | assumed_logic | IP | 40 | $74,589,291 | 99.45% | 1,168.34 | 3,170.83 | 1,775.00 |
| $75M | baseline | IP | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900.00 |

Changes below are **assumed-logic IP minus baseline IP**:

| Budget change | Model / priority | Projects change | USD proxy change | IPS change | Risk proxy change | Strategy change | Added / removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M to $25M | IP / single_objective | +0 | +0.00 | +0.00 | +0.00 | +0.00 | 0 / 0 |
| $50M to $50M | IP / single_objective | -1 | -54,400.00 | -10.00 | -112.50 | -150.00 | 2 / 3 |
| $75M to $75M | IP / single_objective | +0 | -400,000.00 | -15.84 | +29.17 | -125.00 | 2 / 2 |

| Budget | Added projects | Removed projects | Jaccard overlap |
| --- | --- | --- | --- |
| $25M | None | None | 1.0000 |
| $50M | P053;P075 | P004;P033;P055 | 0.8611 |
| $75M | P014;P045 | P004;P025 | 0.9048 |

At $25M the baseline already satisfies both relationships; its selected portfolio is unchanged. At $50M and $75M baseline selects both P003 and P004, violating the scenario exclusion. The constrained optimum removes P004 and adjusts other selections, reducing IPS. P005 is unselected in all six reported IP runs, so the prerequisite is nonbinding in these portfolios; the two-constraint experiment does not isolate every possible prerequisite effect. The scenario cannot improve the maximum attainable IPS because it restricts the feasible set.

GP logical comparisons include recalibrated payoff targets and 12 additional runs with baseline targets held fixed. The fixed-target runs distinguish feasibility effects from target/scale changes; their outputs remain in `gp_fixed_targets_*`. The seven-figure chart set includes this fixed-target GP sensitivity, while the tables above give the required IP comparison.

## 7. Major findings

1. The frozen single-objective baseline attains: **$25M: 24 projects, IPS 706.67; $50M: 34 projects, IPS 968.34; $75M: 40 projects, IPS 1,184.18**.
2. Balanced GP attains: **$25M: 18 projects, IPS 570.01; $50M: 25 projects, IPS 819.18; $75M: 30 projects, IPS 1,025.02**. Its potential sacrifice accompanies lower total proxy exposure and stronger mandate fit.
3. Selection responds to budgets, preferences and business-rule scenarios. The complete sensitivity output contains 75 comparisons with additions/removals and selection overlap.
4. The Funding-History Risk Proxy correlates **-0.9600** with IPS. Shared history variables explain this strong inverse relationship; it is not independent financial-risk evidence.
5. Minimum total proxy exposure is zero at the empty portfolio. The GP target preserves that fact, normalizing risk excess with a positive payoff range.
6. Numerical validation passed **1586/1586 checks**, independently cross-checking **60** portfolios; all six existing tests passed when rerun for submission.

## 8. Limitations and interpretation

The model is a historical academic demonstration. Cost is historical funding, not an actual investment quote. The sample is deliberately stratified; source coverage ends around 2013. Acquisitions/IPOs are events, not guarantees of profitable exits. Closed companies remain historical records rather than current investment candidates. IPS is retrospective, the Funding-History Risk Proxy is neither direct financial risk nor a failure probability, and strategic alignment is a Decision-maker supplied strategic preference. Logical pairs and GP weights are explicit assumptions. Selection identity may vary among tied optima.

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

Missing raw tables prevent verification of the previously reported 462,651 raw entities and 11,259 candidates, and prevent raw reconstruction here. No missing counts or costs have been invented. The scored-data-to-results pipeline and frozen outputs are independently checkable. See [final audit](final_model_audit.md) and [consistency report](../results/submission/consistency_report.md).
