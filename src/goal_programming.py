"""Linear weighted goal programming on the unchanged 100-project universe."""
import json
import numpy as np
import pandas as pd
import pulp
from portfolio_model import (ROOT, RESULTS, METRICS, config, load_data, build_model,
                             solve, extract, validate, save_results)


def payoff_targets(df, budget, logical_scenario="baseline"):
    """Individual optima; risk-minimizing tie-break for P/S optimal portfolios."""
    anchors = []
    for metric in METRICS:
        sense = pulp.LpMinimize if metric == "risk" else pulp.LpMaximize
        model, x, totals = build_model(df, budget, logical_scenario, sense)
        model += totals[metric]
        solve(model)
        primary_optimum = float(pulp.value(totals[metric]))
        if metric != "risk":
            model += totals[metric] >= primary_optimum - 1e-7, "Preserve_primary_optimum"
            model.sense = pulp.LpMinimize
            model.setObjective(totals["risk"])
            solve(model)
        result = extract(df, model, x, budget, logical_scenario, "Payoff")
        result["summary"].update(anchor=metric, primary_optimum=primary_optimum,
                                 priority=f"payoff_{metric}")
        if abs(result["summary"][f"total_{metric}"] - primary_optimum) > 1e-4:
            raise AssertionError("Payoff tie-break changed the primary optimum")
        if not all(c["passed"] for c in validate(df, result)):
            raise AssertionError("Invalid payoff solution")
        anchors.append(result)
    targets = {r["summary"]["anchor"]: r["summary"]["primary_optimum"] for r in anchors}
    # Zero risk ideal is valid; the risk payoff range supplies a positive unit scale.
    scales = {"potential": targets["potential"], "strategic": targets["strategic"],
              "risk": max(r["summary"]["total_risk"] for r in anchors) - targets["risk"]}
    if not all(np.isfinite(v) and v > 0 for v in scales.values()):
        raise ValueError("Degenerate payoff scales: revise/disable the uninformative goal explicitly")
    return targets, scales, anchors


def solve_goal_portfolio(df, budget, targets, scales, weights, logical_scenario="baseline", priority="balanced"):
    if set(weights) != set(METRICS) or not all(np.isfinite(w) and w > 0 for w in weights.values()) or not np.isclose(sum(weights.values()), 1):
        raise ValueError("All three GP weights must be positive and sum to one")
    if set(targets) != set(METRICS) or set(scales) != set(METRICS):
        raise ValueError("Provide all three goal targets and scales")
    if not all(np.isfinite(v) and v >= 0 for v in targets.values()) or not all(np.isfinite(v) and v > 0 for v in scales.values()):
        raise ValueError("Targets must be finite/nonnegative, scales finite/positive")
    model, x, totals = build_model(df, budget, logical_scenario, pulp.LpMinimize)
    deviations = {}
    for k in METRICS:
        minus = pulp.LpVariable(f"d_{k}_minus", lowBound=0)
        plus = pulp.LpVariable(f"d_{k}_plus", lowBound=0)
        model += totals[k] + minus - plus == targets[k], f"Goal_{k}"
        deviations[k] = (minus, plus)
    model += pulp.lpSum(weights[k] * deviations[k][1 if k == "risk" else 0] / scales[k] for k in METRICS)
    solve(model)
    result = extract(df, model, x, budget, logical_scenario, "GP")
    s = result["summary"]
    s["priority"] = priority
    for k, (minus, plus) in deviations.items():
        s[f"target_{k}"] = targets[k]
        s[f"scale_{k}"] = scales[k]
        s[f"weight_{k}"] = weights[k]
        s[f"d_{k}_minus"] = float(pulp.value(minus))
        s[f"d_{k}_plus"] = float(pulp.value(plus))
        bad = s[f"d_{k}_{'plus' if k == 'risk' else 'minus'}"]
        s[f"undesirable_{k}"] = bad
        s[f"normalized_deviation_{k}"] = bad / scales[k]
        # Achievement is a satisfaction index; risk uses its range, not a zero denominator.
        s[f"normalized_achievement_{k}"] = 1 - bad / scales[k]
    checks = validate(df, result)
    if not all(c["passed"] for c in checks):
        raise AssertionError(checks)
    return result


def main():
    df, cfg = load_data(require_goals=True), config()
    results, anchors, target_rows = [], [], []
    for scenario in cfg["logical_scenarios"]:
        for budget in cfg["budgets"]:
            targets, scales, payoff = payoff_targets(df, budget, scenario)
            anchors.extend(payoff)
            target_rows.append({"budget": budget, "logical_scenario": scenario,
                                **{f"target_{k}": v for k, v in targets.items()},
                                **{f"scale_{k}": v for k, v in scales.items()}})
            for priority, weights in cfg["gp_priorities"].items():
                results.append(solve_goal_portfolio(df, budget, targets, scales, weights, scenario, priority))
            print(f"Solved GP: {scenario}, ${budget/1e6:g}M", flush=True)
    save_results(results, "gp")
    save_results(anchors, "payoff")
    pd.DataFrame(target_rows).to_csv(RESULTS / "goal_targets.csv", index=False)
    checks = pd.DataFrame([c for r in results + anchors for c in validate(df, r)])
    checks.to_csv(RESULTS / "gp_validation.csv", index=False)
    (RESULTS / "scenario_config_snapshot.json").write_text(json.dumps(cfg, indent=2))
    print(pd.DataFrame([r["summary"] for r in results])[["budget", "logical_scenario", "priority", "projects_selected", "total_investment", "total_potential", "total_risk", "total_strategic", "objective"]].to_string(index=False))
    print(f"Validation: {checks.passed.sum()}/{len(checks)} passed")


if __name__ == "__main__":
    main()
