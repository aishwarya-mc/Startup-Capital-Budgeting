"""Publication/export-friendly optimization charts; existing EDA is untouched."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import hashlib
import json
from portfolio_model import RESULTS

LABELS = {"single_objective": "IP", "balanced": "GP balanced", "potential_focused": "GP potential-focused",
          "risk_focused": "GP risk-focused", "strategy_focused": "GP strategy-focused"}


def main():
    out = RESULTS / "charts"
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 12, "figure.facecolor": "white"})
    summary = pd.read_csv(RESULTS / "ip_vs_gp_comparison.csv")
    baseline = summary[summary.logical_scenario == "baseline"]
    sectors = pd.read_csv(RESULTS / "sector_composition.csv")
    sectors = sectors[(sectors.logical_scenario == "baseline") & (sectors.target_policy == "recalibrated")]
    budgets = sorted(baseline.budget.unique())
    def save(fig, name):
        fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight")
        fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
        plt.close(fig)
    for metric, ylabel, name in [("total_potential", "Total Investment Potential Score (points)", "01_budget_potential"),
                                  ("projects_selected", "Number of selected projects", "02_budget_project_count")]:
        fig, ax = plt.subplots(figsize=(9, 5))
        for priority, label in LABELS.items():
            group = baseline[baseline.priority == priority].sort_values("budget")
            ax.plot(group.budget/1e6, group[metric], marker="o", label=label)
        title = "Budget vs total investment potential" if metric == "total_potential" else "Budget vs number of selected projects"
        ax.set(title=title + "\nBaseline logical configuration", xlabel="Budget (USD millions)", ylabel=ylabel, xticks=[25,50,75])
        ax.grid(alpha=.2)
        ax.legend(fontsize=9)
        fig.tight_layout()
        save(fig, name)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, metric, title in zip(axes, ["total_potential", "total_risk", "total_strategic"],
                                ["Investment potential\n(higher preferred)", "Total Funding-History Risk Proxy\n(lower preferred)", "Strategic alignment\n(higher preferred)"]):
        for offset, priority in [(-.18, "single_objective"), (.18, "balanced")]:
            values = baseline[baseline.priority == priority].sort_values("budget")[metric]
            ax.bar(np.arange(3)+offset, values, width=.36, label=LABELS[priority])
        ax.set(title=title, xticks=np.arange(3), xticklabels=["$25M","$50M","$75M"], xlabel="Budget", ylabel="Additive score-points")
        ax.legend(fontsize=9)
    fig.suptitle("IP versus balanced GP — same 100 projects and baseline constraints", y=1.02)
    fig.tight_layout()
    save(fig, "03_ip_vs_gp_performance")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)
    for ax, budget in zip(axes, budgets):
        table = sectors[(sectors.budget == budget) & sectors.priority.isin(["single_objective", "balanced"])].pivot(index="sector", columns="priority", values="projects_selected")
        table = table[["single_objective", "balanced"]].rename(columns=LABELS)
        table.plot.bar(ax=ax)
        ax.set(title=f"${budget/1e6:g}M", xlabel="Sector", ylabel="Selected projects")
        ax.tick_params(axis="x", rotation=65)
        ax.legend(fontsize=8)
    fig.suptitle("Selected projects by sector — IP versus balanced GP")
    fig.tight_layout()
    save(fig, "04_selected_sectors")
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for ax, budget in zip(axes, budgets):
        group = baseline[(baseline.budget == budget) & (baseline.model == "GP")].set_index("priority")
        table = group[[f"normalized_deviation_{k}" for k in ["potential", "risk", "strategic"]]]
        table.columns = ["Potential shortfall / target", "Risk proxy excess / payoff range", "Strategy shortfall / target"]
        table.index = [p.replace("_focused", "").replace("_", " ") for p in table.index]
        table.plot.bar(ax=ax)
        ax.set(title=f"${budget/1e6:g}M", xlabel="GP weight scenario", ylabel="Normalized undesirable deviation\n(dimensionless; lower preferred)")
        ax.tick_params(axis="x", rotation=25)
        ax.get_legend().remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("GP goal deviations — baseline; total risk proxy target is zero")
    fig.tight_layout(rect=[0,.1,1,1])
    save(fig, "05_gp_goal_deviations")
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for ax, budget in zip(axes, budgets):
        group = sectors[(sectors.budget == budget) & (sectors.model == "GP")]
        table = group.pivot(index="priority", columns="sector", values="projects_selected")
        table.index = [p.replace("_focused", "") for p in table.index]
        table.plot.bar(stacked=True, ax=ax, colormap="tab20")
        ax.set(title=f"${budget/1e6:g}M", xlabel="GP weight scenario", ylabel="Selected projects")
        ax.tick_params(axis="x", rotation=25)
        ax.get_legend().remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=9)
    fig.suptitle("Portfolio sector composition under GP priorities — baseline")
    fig.tight_layout(rect=[0,.15,1,1])
    save(fig, "06_gp_priority_composition")
    delta = pd.read_csv(RESULTS / "sensitivity_changes.csv")
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for row, (dimension, model, priority, label, color) in enumerate([
            ("logic_recalibrated", "IP", "single_objective", "IP: assumed logic minus baseline", "#1f77b4"),
            ("logic_fixed_targets", "GP", "balanced", "Balanced GP: assumed logic minus baseline, fixed targets", "#ff7f0e")]):
        d = delta[(delta.dimension == dimension) & (delta.from_model == model) & (delta.from_priority == priority)].sort_values("from_budget")
        for ax, metric, title in zip(axes[row], ["potential", "risk", "strategic"], ["Investment potential", "Total Funding-History Risk Proxy", "Strategic alignment"]):
            ax.bar(["$25M", "$50M", "$75M"], d[f"delta_total_{metric}"], color=color, label=label)
            ax.axhline(0, color="black", linewidth=.7)
            ax.set(title=title, ylabel="Change in score-points", xlabel="Budget")
    handles = [axes[i, 0].get_legend_handles_labels()[0][0] for i in range(2)]
    labels = [axes[i, 0].get_legend_handles_labels()[1][0] for i in range(2)]
    fig.legend(handles, labels, loc="lower center", ncol=1, fontsize=10)
    fig.suptitle("Logical-constraint sensitivity — scenario-based modelling assumptions")
    fig.tight_layout(rect=[0, .09, 1, 1])
    save(fig, "07_logical_constraint_sensitivity")
    (out / "README.md").write_text("# Final optimization figures\n\nSeven analytical figures in 300-dpi PNG and vector PDF formats.\nBaseline means no logical constraints. Risk denotes Funding-History Risk Proxy, not direct financial risk or failure probability. Strategy is a Decision-maker supplied strategic preference.\nPotential, proxy and strategy use separate axes and additive score-points.\nRisk deviation normalization uses its payoff range because its ideal target is zero.\nFigure 7 compares assumed logic with baseline: IP in the upper row, balanced GP with fixed baseline targets in the lower row.\nFigure 6 shows priority-dependent sector composition; figure 4 compares IP and balanced GP.\nExisting exploratory charts are preserved as historical sample context.\nSee ../../../docs/final_figures_review.md for captions and source definitions.\n", encoding="utf-8")
    source_names = ["ip_vs_gp_comparison.csv", "sector_composition.csv", "sensitivity_changes.csv"]
    manifest = {"purpose": "Publication figures derived solely from frozen numerical outputs",
                "sources": {name: hashlib.sha256((RESULTS / name).read_bytes()).hexdigest() for name in source_names},
                "figures": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.suffix in [".png", ".pdf"]}}
    (out / "chart_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved 7 PNG and 7 PDF charts to {out}")


if __name__ == "__main__":
    main()
