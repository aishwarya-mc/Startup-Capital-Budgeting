"""Fair comparisons: attach the same goal references to IP and GP portfolios."""
import pandas as pd
from portfolio_model import RESULTS, METRICS


def comparison():
    ip = pd.read_csv(RESULTS / "ip_summary.csv")
    gp = pd.read_csv(RESULTS / "gp_summary.csv")
    targets = pd.read_csv(RESULTS / "goal_targets.csv")
    ip["priority"] = "single_objective"
    ip = ip.merge(targets, on=["budget", "logical_scenario"], validate="one_to_one")
    for k in METRICS:
        difference = ip[f"total_{k}"] - ip[f"target_{k}"]
        ip[f"undesirable_{k}"] = (difference if k == "risk" else -difference).clip(lower=0)
        ip[f"normalized_deviation_{k}"] = ip[f"undesirable_{k}"] / ip[f"scale_{k}"]
        ip[f"normalized_achievement_{k}"] = 1 - ip[f"normalized_deviation_{k}"]
    columns = ["budget", "model", "logical_scenario", "priority", "solver_status",
               "projects_selected", "total_investment", "budget_utilization_percent"]
    columns += [f"{prefix}_{k}" for prefix in ["total", "target", "scale", "undesirable", "normalized_deviation", "normalized_achievement"] for k in METRICS]
    result = pd.concat([ip[columns], gp[columns]], ignore_index=True).sort_values(["logical_scenario", "budget", "model", "priority"])
    result.to_csv(RESULTS / "ip_vs_gp_comparison.csv", index=False)
    for budget, group in result.groupby("budget"):
        group.to_csv(RESULTS / f"comparison_{int(budget/1e6)}m.csv", index=False)
    lines = ["# IP versus GP: observed results", "",
             "Both models use identical project data and hard constraints within each named logical scenario.",
             "IP maximizes IPS; GP minimizes weighted normalized goal shortfalls/excess.",
             "IP deviations are evaluated after solving against the same GP targets; they are not IP constraints.",
             "Neither formulation is intrinsically better. Risk and strategic points retain their documented limitations.", "",
             "## Baseline: balanced GP versus IP", "",
             "| Budget | Model | Projects | Cost USD | Utilization % | Potential | Risk points | Strategy points |",
             "|---:|---|---:|---:|---:|---:|---:|---:|"]
    base = result[(result.logical_scenario == "baseline") & result.priority.isin(["single_objective", "balanced"])]
    for _, row in base.sort_values(["budget", "model"], ascending=[True, False]).iterrows():
        lines.append(f"|${row.budget/1e6:g}M|{row.model}|{row.projects_selected}|{row.total_investment:,.0f}|{row.budget_utilization_percent:.2f}|{row.total_potential:.2f}|{row.total_risk:.2f}|{row.total_strategic:.0f}|")
    lines += ["", "## Trade-offs", ""]
    for budget, group in base.groupby("budget"):
        a = group[group.model == "IP"].iloc[0]
        b = group[group.model == "GP"].iloc[0]
        lines.append(f"- ${budget/1e6:g}M: balanced GP selects {a.projects_selected-b.projects_selected} fewer projects; potential changes by {b.total_potential-a.total_potential:+.2f}, total risk by {b.total_risk-a.total_risk:+.2f}, strategy by {b.total_strategic-a.total_strategic:+.0f} versus IP.")
    lines += ["", "Lower total risk partly reflects smaller portfolios, not proven safer startups or lower loss probabilities.",
              "A larger budget expands the feasible set, but portfolios need not be nested. GP targets and normalization",
              "are recalibrated at each budget, so GP objective values across budgets are not a common welfare scale.",
              "The CSV tables include targets, all undesirable deviations and normalized achievement for every priority.",
              "Solver-selected portfolios may differ among tied optima; changes in identities need not imply a unique recommendation."]
    (RESULTS / "comparison_report.md").write_text("\n".join(lines)+"\n")
    print(base[["budget", "model", "projects_selected", "total_potential", "total_risk", "total_strategic"]].to_string(index=False))
    return result


if __name__ == "__main__":
    comparison()
