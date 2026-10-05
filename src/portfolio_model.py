"""Shared linear model construction, input checks and solution validation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pulp

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "optimization"
SCORED = ROOT / "data/processed/startup_projects_scored.csv"
METRICS = {"potential": "investment_potential_score", "risk": "risk_score", "strategic": "strategic_score"}


def config():
    return json.loads((ROOT / "config/model_config.json").read_text())


def load_data(require_goals=False):
    df = pd.read_csv(SCORED)
    base = pd.read_csv(ROOT / "data/processed/startup_projects.csv")
    pd.testing.assert_frame_equal(df[base.columns], base)
    if len(df) != 100 or not df.project_id.is_unique or not df.company_id.is_unique:
        raise ValueError("Expected the original 100 distinct projects and companies")
    columns = ["investment_cost", "investment_potential_score"]
    if require_goals:
        columns += ["risk_score", "strategic_score"]
    if not np.isfinite(df[columns].to_numpy()).all():
        raise ValueError("Optimization inputs must be finite and nonmissing")
    if (df.investment_cost <= 0).any():
        raise ValueError("Costs must be positive")
    for col in columns[1:]:
        if not df[col].between(0, 100).all():
            raise ValueError(f"Out of range: {col}")
    return df


def build_model(df, budget, logical_scenario="baseline", sense=pulp.LpMaximize):
    if not np.isfinite(budget) or budget <= 0:
        raise ValueError("Budget must be finite and positive")
    model = pulp.LpProblem("Startup_Portfolio", sense)
    x = {p: pulp.LpVariable(f"x_{p}", cat="Binary") for p in df.project_id}
    # Dollars scaled to millions to improve numerical conditioning; no rounding.
    model += pulp.lpSum(c / 1e6 * x[p] for p, c in zip(df.project_id, df.investment_cost)) <= budget / 1e6, "Budget"
    logic = config()["logical_scenarios"][logical_scenario]
    for kind in ["prerequisites", "mutual_exclusions"]:
        for a, b in logic[kind]:
            if a not in x or b not in x or a == b:
                raise ValueError(f"Invalid {kind} pair: {a}, {b}")
            if kind == "prerequisites":
                model += x[a] <= x[b], f"requires_{a}_{b}"
            else:
                model += x[a] + x[b] <= 1, f"excludes_{a}_{b}"
    totals = {k: pulp.lpSum(float(v) * x[p] for p, v in zip(df.project_id, df[col]))
              for k, col in METRICS.items() if col in df}
    return model, x, totals


def solve(model):
    model.solve(pulp.PULP_CBC_CMD(msg=False, gapRel=0, gapAbs=0, timeLimit=120))
    status = pulp.LpStatus[model.status]
    if status != "Optimal" or model.sol_status != pulp.LpSolutionOptimal:
        raise RuntimeError(f"Solver did not prove optimality: {status}")
    return status


def extract(df, model, x, budget, logical_scenario, label):
    values = np.array([pulp.value(x[p]) for p in df.project_id], dtype=float)
    selected = df.loc[values > .5].copy()
    row = {"budget": budget, "model": label, "logical_scenario": logical_scenario,
           "solver_status": pulp.LpStatus[model.status], "solver_solution_status": model.sol_status,
           "projects_selected": len(selected),
           "total_investment": float(selected.investment_cost.sum())}
    row["budget_utilization_percent"] = 100 * row["total_investment"] / budget
    for metric, col in METRICS.items():
        if col in df:
            row[f"total_{metric}"] = float(selected[col].sum())
    row["objective"] = float(pulp.value(model.objective))
    decisions = pd.DataFrame({"project_id": df.project_id, "x": values})
    return {"summary": row, "decisions": decisions, "selected": selected}


def validate(df, result):
    """Recompute from all 100 raw solver decisions, not just selected exports."""
    s, decisions = result["summary"], result["decisions"]
    x = decisions.set_index("project_id").x.reindex(df.project_id).to_numpy()
    checks = {"status_optimal": s["solver_status"] == "Optimal",
              "solution_proven_optimal": s["solver_solution_status"] == pulp.LpSolutionOptimal,
              "decision_ids": len(decisions) == len(df) and decisions.project_id.is_unique and set(decisions.project_id) == set(df.project_id),
              "binary": bool(np.isfinite(x).all() and np.all(np.minimum(abs(x), abs(x - 1)) <= 1e-6)),
              "budget": float(df.investment_cost @ x) <= s["budget"] + .01,
              "cost_recomputed": bool(np.isclose(df.investment_cost @ x, s["total_investment"], rtol=0, atol=.01)),
              "count_recomputed": abs(x.sum() - s["projects_selected"]) <= 1e-6,
              "utilization_recomputed": abs(100 * (df.investment_cost @ x) / s["budget"] - s["budget_utilization_percent"]) <= 1e-6}
    lookup = dict(zip(df.project_id, x))
    logic = config()["logical_scenarios"][s["logical_scenario"]]
    checks["prerequisites"] = all(lookup[a] <= lookup[b] + 1e-6 for a, b in logic["prerequisites"])
    checks["mutual_exclusions"] = all(lookup[a] + lookup[b] <= 1 + 1e-6 for a, b in logic["mutual_exclusions"])
    for metric, col in METRICS.items():
        if col not in df:
            continue
        total = float(df[col] @ x)
        checks[f"{metric}_recomputed"] = abs(total - s[f"total_{metric}"]) <= 1e-5
        if f"target_{metric}" in s:
            minus, plus = s[f"d_{metric}_minus"], s[f"d_{metric}_plus"]
            checks[f"{metric}_equation"] = abs(total + minus - plus - s[f"target_{metric}"]) <= 1e-3
            checks[f"{metric}_deviations_nonnegative"] = min(minus, plus) >= -1e-6
            expected_bad = max(0, total - s[f"target_{metric}"] if metric == "risk" else s[f"target_{metric}"] - total)
            checks[f"{metric}_undesirable_recomputed"] = abs(expected_bad - s[f"undesirable_{metric}"]) <= 1e-3
            checks[f"{metric}_normalized_deviation"] = abs(expected_bad / s[f"scale_{metric}"] - s[f"normalized_deviation_{metric}"]) <= 1e-6
            checks[f"{metric}_normalized_achievement"] = abs(1 - expected_bad / s[f"scale_{metric}"] - s[f"normalized_achievement_{metric}"]) <= 1e-6
    if s["model"] == "IP":
        checks["objective_recomputed"] = abs(s["objective"] - s["total_potential"]) <= 1e-5
    elif s["model"] == "GP":
        objective = sum(s[f"weight_{k}"] * s[f"d_{k}_{'plus' if k == 'risk' else 'minus'}"] / s[f"scale_{k}"] for k in METRICS)
        checks["objective_recomputed"] = abs(objective - s["objective"]) <= 1e-6
    return [{"budget": s["budget"], "model": s["model"], "logical_scenario": s["logical_scenario"],
             "priority": s.get("priority", "single_objective"), "check": k, "passed": bool(v)} for k, v in checks.items()]


def save_results(results, prefix):
    RESULTS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r["summary"] for r in results]).to_csv(RESULTS / f"{prefix}_summary.csv", index=False)
    for key in ["selected", "decisions"]:
        frames = []
        for r in results:
            f = r[key].copy()
            for col in ["budget", "model", "logical_scenario", "priority"]:
                if col in r["summary"]:
                    f[col] = r["summary"][col]
            frames.append(f)
        pd.concat(frames, ignore_index=True).to_csv(RESULTS / f"{prefix}_{key}.csv", index=False)
