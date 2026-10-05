"""Budget, preference and logical-scenario sensitivity with selection overlap."""
import itertools
import pandas as pd
from portfolio_model import RESULTS, config, load_data, validate, save_results
from goal_programming import solve_goal_portfolio

KEY = ["budget", "model", "logical_scenario", "priority"]
MEASURES = ["projects_selected", "total_investment", "budget_utilization_percent",
            "total_potential", "total_risk", "total_strategic"]


def main():
    df, cfg = load_data(True), config()
    references = pd.read_csv(RESULTS / "goal_targets.csv")
    fixed = []
    for _, row in references[references.logical_scenario == "baseline"].iterrows():
        for priority, weights in cfg["gp_priorities"].items():
            fixed.append(solve_goal_portfolio(df, row.budget,
                {k: row[f"target_{k}"] for k in ["potential", "risk", "strategic"]},
                {k: row[f"scale_{k}"] for k in ["potential", "risk", "strategic"]},
                weights, "assumed_logic", priority))
    save_results(fixed, "gp_fixed_targets")
    pd.DataFrame([c for r in fixed for c in validate(df, r)]).to_csv(RESULTS / "fixed_targets_validation.csv", index=False)
    frames, selections = [], []
    for prefix in ["ip", "gp", "gp_fixed_targets"]:
        s = pd.read_csv(RESULTS / f"{prefix}_summary.csv")
        selected = pd.read_csv(RESULTS / f"{prefix}_selected.csv")
        if prefix == "ip":
            s["priority"] = "single_objective"
            selected["priority"] = "single_objective"
        s["target_policy"] = "fixed_baseline" if prefix == "gp_fixed_targets" else "recalibrated"
        selected["target_policy"] = s.target_policy.iloc[0]
        frames.append(s)
        selections.append(selected)
    summary = pd.concat(frames, ignore_index=True)
    chosen = pd.concat(selections, ignore_index=True)
    keys = KEY + ["target_policy"]
    def subset(row):
        mask = pd.Series(True, index=chosen.index)
        for key in keys:
            mask &= chosen[key] == row[key]
        return chosen[mask]
    differences, sector_changes, composition = [], [], []
    sectors = sorted(df.sector.unique())
    for _, row in summary.iterrows():
        selected = subset(row)
        for sector in sectors:
            group = selected[selected.sector == sector]
            composition.append({**{k: row[k] for k in keys}, "sector": sector,
                "projects_selected": len(group), "total_investment": group.investment_cost.sum(),
                "project_share": len(group) / len(selected) if len(selected) else 0,
                "investment_share": group.investment_cost.sum() / row.total_investment if row.total_investment else 0})

    def compare(a, b, dimension):
        sa, sb = subset(a), subset(b)
        ia, ib = set(sa.project_id), set(sb.project_id)
        name = f"{dimension}_{len(differences)+1:03}"
        differences.append({"comparison_id": name, "dimension": dimension,
            **{f"from_{k}": a[k] for k in keys}, **{f"to_{k}": b[k] for k in keys},
            "retained": len(ia & ib), "added_count": len(ib-ia), "removed_count": len(ia-ib),
            "jaccard_similarity": len(ia & ib)/len(ia | ib) if ia | ib else 1,
            "added_projects": ";".join(sorted(ib-ia)), "removed_projects": ";".join(sorted(ia-ib)),
            **{f"delta_{m}": b[m]-a[m] for m in MEASURES}})
        for sector in sectors:
            aa, bb = sa[sa.sector == sector], sb[sb.sector == sector]
            sector_changes.append({"comparison_id": name, "dimension": dimension, "sector": sector,
                "from_count": len(aa), "to_count": len(bb), "delta_count": len(bb)-len(aa),
                "delta_investment": bb.investment_cost.sum()-aa.investment_cost.sum()})

    regular = summary[summary.target_policy == "recalibrated"]
    for _, group in regular.groupby(["model", "logical_scenario", "priority"]):
        for (_, a), (_, b) in itertools.combinations(list(group.sort_values("budget").iterrows()), 2):
            compare(a, b, "budget")
    for _, group in regular[regular.model == "GP"].groupby(["budget", "logical_scenario"]):
        a = group[group.priority == "balanced"].iloc[0]
        for _, b in group[group.priority != "balanced"].iterrows():
            compare(a, b, "priority")
    for _, group in regular.groupby(["budget", "model", "priority"]):
        compare(group[group.logical_scenario == "baseline"].iloc[0],
                group[group.logical_scenario == "assumed_logic"].iloc[0], "logic_recalibrated")
    for _, b in summary[summary.target_policy == "fixed_baseline"].iterrows():
        a = regular[(regular.model == "GP") & (regular.logical_scenario == "baseline") &
                    (regular.budget == b.budget) & (regular.priority == b.priority)].iloc[0]
        compare(a, b, "logic_fixed_targets")
    delta = pd.DataFrame(differences)
    delta.to_csv(RESULTS / "sensitivity_changes.csv", index=False)
    pd.DataFrame(sector_changes).to_csv(RESULTS / "sensitivity_sector_changes.csv", index=False)
    pd.DataFrame(composition).to_csv(RESULTS / "sector_composition.csv", index=False)
    lines = ["# Sensitivity analysis", "", "All changes are destination minus source. Project identities, additions/removals,",
             "Jaccard overlap, aggregate measures and sector counts/costs are exported in the CSVs.",
             "Sector tables include zero-selection sectors. Weights/strategic tiers and logical pairs are scenario inputs.",
             "", "## Budget sensitivity (baseline, $25M to $75M)", ""]
    for _, r in delta[(delta.dimension == "budget") & (delta.from_logical_scenario == "baseline") & (delta.from_budget == 25000000) & (delta.to_budget == 75000000)].iterrows():
        lines.append(f"- {r.from_model}/{r.from_priority}: projects {r.delta_projects_selected:+.0f}, potential {r.delta_total_potential:+.2f}, risk {r.delta_total_risk:+.2f}, strategy {r.delta_total_strategic:+.0f}; {r.added_count} added/{r.removed_count} removed; overlap {r.jaccard_similarity:.3f}.")
    lines += ["", "## Priority sensitivity (baseline, $50M; relative to balanced)", ""]
    for _, r in delta[(delta.dimension == "priority") & (delta.from_logical_scenario == "baseline") & (delta.from_budget == 50000000)].iterrows():
        lines.append(f"- {r.to_priority}: potential {r.delta_total_potential:+.2f}, risk {r.delta_total_risk:+.2f}, strategy {r.delta_total_strategic:+.0f}; {r.added_count} added/{r.removed_count} removed.")
    lines += ["", "## Logical constraints", "", "Original commented relationships are assumptions; baseline leaves them disabled.",
              "Recalibrated comparisons recompute payoff references after adding constraints. Fixed-target comparisons",
              "retain baseline targets/scales and weights, isolating changes in feasibility. Both are reported.", ""]
    for _, r in delta[(delta.dimension == "logic_fixed_targets") & (delta.from_priority == "balanced")].iterrows():
        lines.append(f"- ${r.from_budget/1e6:g}M, balanced, fixed targets: potential {r.delta_total_potential:+.2f}, risk {r.delta_total_risk:+.2f}, strategy {r.delta_total_strategic:+.0f}; {r.added_count} added/{r.removed_count} removed.")
    lines += ["", "## Interpretation limits", "", "Budget expansion cannot reduce the optimal IP objective; GP goals/scales change with budget.",
              "Risk-focused portfolios are smaller because total risk is additive. Strategy-focused portfolios",
              "favor the assumed software/digital mandate, not observed superior sectors. Membership can change",
              "under ties without meaningful objective changes. No claim of unique optimal portfolios is made.",
              "Sector composition and all sector deltas appear in sector_composition.csv and sensitivity_sector_changes.csv."]
    (RESULTS / "sensitivity_report.md").write_text("\n".join(lines)+"\n")
    print(delta.groupby("dimension").size().to_string())
    print("Fixed-target GP solutions:",len(fixed),"; sector composition rows:",len(composition))


if __name__ == "__main__":
    main()
