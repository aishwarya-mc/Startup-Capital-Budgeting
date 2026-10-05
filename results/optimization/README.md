# Authoritative frozen optimization outputs

Use `ip_summary.csv`, `gp_summary.csv`, `payoff_summary.csv`, `goal_targets.csv` and `ip_vs_gp_comparison.csv` as the numerical sources of truth. The three `comparison_*m.csv` files are budget-specific views of that canonical comparison, not alternative results.

Terminology in all machine-readable files and earlier reports:

- `total_risk` / `risk_score` means **Funding-History Risk Proxy**, measured in additive points, not direct financial risk or probability of failure.
- `total_investment` / `investment_cost` means the **Investment Cost Proxy**, historical funding measured in USD, not a current deal price.
- `total_strategic` / `strategic_score` applies a **Decision-maker supplied strategic preference**, not an objective industry ranking.
- `assumed_logic` means **Scenario-based modelling assumptions**; baseline has no logical pairs.

`gp_summary.csv` contains 24 main runs; `gp_fixed_targets_summary.csv` contains 12 additional logical comparisons with baseline targets held fixed. The 18 payoff rows include empty minimum-risk portfolios. Their `primary_optimum` is the target; for P/S anchors, `objective` is the secondary risk-minimization value, not the primary score.

Decision files contain all 100 project variables per run; selected files contain only selected rows. Scores and totals retain solver/data precision. Academic tables round for readability without modifying these files.

Start with [final results summary](../../docs/final_results_summary.md), [methodology](../../docs/methodology.md), [validation](validation_report.md) and [submission consistency](../submission/consistency_report.md). Seven publication figure pairs are under [charts/](charts/).
