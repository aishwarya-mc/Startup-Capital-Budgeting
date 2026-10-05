# Final Results Summary

All tables below are generated from the frozen CSVs in `results/optimization/`; they are not transcribed from old results. Display rounding is for readability only. USD values denote the **Investment Cost Proxy**. IPS, Funding-History Risk Proxy and strategy totals are additive score-points. Every exported main/anchor/fixed-target solution has status **Optimal**.

## 1. Final Integer Programming results

The authoritative baseline has budget and binary constraints only. It maximizes total IPS.

{{IP_TABLE}}

Source: [ip_summary.csv](../results/optimization/ip_summary.csv), `logical_scenario=baseline`. Root-level historical IP result files are superseded for baseline reporting. Their old $50M/$75M totals describe neither the authoritative baseline nor a newly discovered error in this finalization.

## 2. Final Goal Programming results

GP minimizes weighted normalized potential/strategic shortfall and total risk-proxy excess. `baseline` has no logical pairs; `assumed_logic` adds the explicitly hypothetical prerequisite and exclusion. All 24 validated main GP scenarios are retained:

{{GP_ALL_TABLE}}

Source: [gp_summary.csv](../results/optimization/gp_summary.csv). Target values are documented in [methodology, section 14](methodology.md#14-gp-target-generation); all six goal deviations and objectives remain in that CSV. For the balanced baseline, they are:

{{BALANCED_DEVIATIONS}}

Achievement equals `1-undesirable_deviation/scale`, not a probability. P/S scales equal their targets; R uses the payoff risk range because its target is zero. Six decimal places expose the numerical reporting precision.

## 3. Authoritative IP vs GP comparison

This is the submission's main comparison table: baseline IP against baseline **balanced GP**, with the same 100 projects and budget. It is a view of the existing [ip_vs_gp_comparison.csv](../results/optimization/ip_vs_gp_comparison.csv), not a separately calculated optimization result.

{{COMPARISON_TABLE}}

For IP, deviations are evaluated after optimization against the corresponding GP targets; they are not part of the IP objective. P shortfall is undesirable potential deviation, R excess is undesirable total Funding-History Risk Proxy deviation, S shortfall is undesirable strategic deviation.

Changes below are **balanced GP minus IP**:

{{TRADEOFF_TABLE}}

IP maximizes one primary objective subject to hard constraints. GP balances several potentially conflicting aspiration levels. Here balanced GP sacrifices IPS and selects fewer projects, lowers total Funding-History Risk Proxy and improves strategic alignment. Some proxy reduction comes from fewer projects, not evidence of lower actual failure risk. GP is not inherently better than IP.

## 4. Budget sensitivity

The preceding tables give actual cost, utilization and scores at every budget. The following differences show both adjacent budget increases and the full $25M-to-$75M comparison:

{{BUDGET_DELTAS}}

For baseline IP and balanced GP, increasing budget increases selected project count, expenditure proxy, IPS, total Funding-History Risk Proxy and strategic points in these observed runs. More available capital permits a larger portfolio, but each additional selected project contributes proxy exposure. IP optimal IPS is mathematically nondecreasing as the feasible set expands; selection counts or nested membership are not guaranteed in general. GP reference targets are recalibrated with budget, so its objective values across budgets are not a common quality score.

## 5. GP priority sensitivity

Verified decision-maker preference scenarios:

{{WEIGHT_TABLE}}

Within each budget/configuration, all priorities use the same target values and scales. Baseline differences relative to balanced GP are:

{{PRIORITY_DELTAS}}

Potential-focused GP generally preserves more IPS at greater total proxy exposure. Risk-focused GP selects **{{RISK_COUNTS}} projects at $25M/$50M/$75M**, respectively, trading potential and alignment for lower additive exposure. Strategy-focused GP sacrifices some potential and permits more proxy exposure to favor the assumed mandate. These are observed preference trade-offs, not a ranking of investors.

For a concrete composition comparison, these are selected sector counts at $50M, baseline:

{{PRIORITY_SECTORS}}

Zero entries mean no selected projects in that sector, not that the sector is inherently undesirable. Full 420-row sector composition and 750 sector-change rows are in [sector_composition.csv](../results/optimization/sector_composition.csv) and [sensitivity_sector_changes.csv](../results/optimization/sensitivity_sector_changes.csv).

## 6. Logical-constraint scenario

The exact **Scenario-based modelling assumptions** are P005 requires P004 (`x_P005<=x_P004`) and P003/P004 are mutually exclusive (`x_P003+x_P004<=1`). No Crunchbase source establishes these relationships. They illustrate how decision-maker-supplied business interdependencies could be imposed.

{{IP_LOGIC_TABLE}}

Changes below are **assumed-logic IP minus baseline IP**:

{{LOGIC_DELTAS}}

{{LOGIC_MEMBERSHIP}}

At $25M the baseline already satisfies both relationships; its selected portfolio is unchanged. At $50M and $75M baseline selects both P003 and P004, violating the scenario exclusion. The constrained optimum removes P004 and adjusts other selections, reducing IPS. P005 is unselected in all six reported IP runs, so the prerequisite is nonbinding in these portfolios; the two-constraint experiment does not isolate every possible prerequisite effect. The scenario cannot improve the maximum attainable IPS because it restricts the feasible set.

GP logical comparisons include recalibrated payoff targets and 12 additional runs with baseline targets held fixed. The fixed-target runs distinguish feasibility effects from target/scale changes; their outputs remain in `gp_fixed_targets_*`. The seven-figure chart set includes this fixed-target GP sensitivity, while the tables above give the required IP comparison.

## 7. Major findings

1. The frozen single-objective baseline attains: **{{IP_BRIEF}}**.
2. Balanced GP attains: **{{GP_BRIEF}}**. Its potential sacrifice accompanies lower total proxy exposure and stronger mandate fit.
3. Selection responds to budgets, preferences and business-rule scenarios. The complete sensitivity output contains 75 comparisons with additions/removals and selection overlap.
4. The Funding-History Risk Proxy correlates **{{CORRELATION}}** with IPS. Shared history variables explain this strong inverse relationship; it is not independent financial-risk evidence.
5. Minimum total proxy exposure is zero at the empty portfolio. The GP target preserves that fact, normalizing risk excess with a positive payoff range.
6. Numerical validation passed **{{VALIDATION_PASSED}}/{{VALIDATION_COUNT}} checks**, independently cross-checking **{{PORTFOLIOS}}** portfolios; all six existing tests passed when rerun for submission.

## 8. Limitations and interpretation

The model is a historical academic demonstration. Cost is historical funding, not an actual investment quote. The sample is deliberately stratified; source coverage ends around 2013. Acquisitions/IPOs are events, not guarantees of profitable exits. Closed companies remain historical records rather than current investment candidates. IPS is retrospective, the Funding-History Risk Proxy is neither direct financial risk nor a failure probability, and strategic alignment is a Decision-maker supplied strategic preference. Logical pairs and GP weights are explicit assumptions. Selection identity may vary among tied optima.

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

Missing raw tables prevent verification of the previously reported 462,651 raw entities and 11,259 candidates, and prevent raw reconstruction here. No missing counts or costs have been invented. The scored-data-to-results pipeline and frozen outputs are independently checkable. See [final audit](final_model_audit.md) and [consistency report](../results/submission/consistency_report.md).
