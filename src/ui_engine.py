"""Solver layer for the Streamlit UI.

Re-uses the validated formulation (budget knapsack + optional logic, linear weighted GP)
but accepts user-chosen data, budget, logic pairs, strategy scores, weights and targets.
The frozen model files are not modified; this module only calls the shared solver helpers.
"""
import numpy as np
import pandas as pd
import pulp

from portfolio_model import ROOT, SCORED, solve, config

METRICS = {"potential": "investment_potential_score", "risk": "risk_score", "strategic": "strategic_score"}
REQUIRED_RAW = ["project_id", "startup_name", "sector", "investment_cost"]
STATUS_SCORES = {"ipo": 100, "acquired": 90, "operating": 70, "closed": 20}


def default_data():
    return pd.read_csv(SCORED)


def _minmax(s):
    lo, hi = s.min(), s.max()
    return pd.Series(100.0, index=s.index) if hi == lo else (s - lo) / (hi - lo) * 100


def prepare(df, sector_scores=None):
    """Validate an uploaded/default table and add any missing score columns.

    Uses the project's own formulas: IPS = .30 rounds + .25 duration + .25 status + .20 outcome,
    risk = .5(100-N(rounds)) + .5(100-N(duration)); strategic score comes from sector_scores.
    Returns (frame, notes).
    """
    df = df.copy()
    notes = []
    missing = [c for c in REQUIRED_RAW if c not in df]
    if missing:
        raise ValueError(f"Missing required column(s): {missing}")
    if not df.project_id.is_unique:
        raise ValueError("project_id must be unique")
    df["investment_cost"] = pd.to_numeric(df.investment_cost, errors="coerce")
    if df.investment_cost.isna().any() or (df.investment_cost <= 0).any():
        raise ValueError("investment_cost must be positive and non-missing for every project")
    history = {"funding_rounds", "funding_duration_years"} <= set(df)
    if "investment_potential_score" not in df:
        need = history and "status" in df
        if not need:
            raise ValueError("Need investment_potential_score, or funding_rounds + funding_duration_years + status to compute it")
        acq = df["acquisition"] if "acquisition" in df else 0
        ipo = df["ipo"] if "ipo" in df else 0
        df["investment_potential_score"] = (
            .30 * _minmax(df.funding_rounds) + .25 * _minmax(df.funding_duration_years)
            + .25 * df.status.map(STATUS_SCORES).fillna(50) + .20 * ((acq + ipo) / 2 * 100)).round(2)
        notes.append("investment_potential_score computed from funding history, status and outcomes")
    if "risk_score" not in df:
        if not history:
            raise ValueError("Need risk_score, or funding_rounds + funding_duration_years to compute it")
        df["risk_score"] = (.5 * (100 - _minmax(df.funding_rounds)) + .5 * (100 - _minmax(df.funding_duration_years))).round(6)
        notes.append("risk_score (Funding-History Risk Proxy) computed from funding history")
    if sector_scores is not None:
        df["strategic_score"] = df.sector.map(sector_scores).fillna(0).astype(float)
    elif "strategic_score" not in df:
        raise ValueError("Need strategic_score or sector strategy scores")
    for c in METRICS.values():
        if not np.isfinite(df[c].to_numpy(dtype=float)).all():
            raise ValueError(f"{c} contains missing/non-finite values")
    return df, notes


def _build(df, budget, prerequisites=(), exclusions=(), sense=pulp.LpMaximize):
    model = pulp.LpProblem("UI_Portfolio", sense)
    x = {p: pulp.LpVariable(f"x_{i}", cat="Binary") for i, p in enumerate(df.project_id)}
    model += pulp.lpSum(c / 1e6 * x[p] for p, c in zip(df.project_id, df.investment_cost)) <= budget / 1e6, "Budget"
    for a, b in prerequisites:
        model += x[a] <= x[b], f"requires_{a}_{b}"
    for a, b in exclusions:
        model += x[a] + x[b] <= 1, f"excludes_{a}_{b}"
    totals = {k: pulp.lpSum(float(v) * x[p] for p, v in zip(df.project_id, df[col])) for k, col in METRICS.items()}
    return model, x, totals


def _summarise(df, x, budget, label, model):
    chosen = np.array([pulp.value(x[p]) for p in df.project_id]) > .5
    sel = df.loc[chosen].copy()
    out = {"model": label, "budget": budget, "projects": int(chosen.sum()),
           "investment": float(sel.investment_cost.sum()),
           "utilization_pct": 100 * float(sel.investment_cost.sum()) / budget,
           "potential": float(sel.investment_potential_score.sum()),
           "risk": float(sel.risk_score.sum()),
           "strategic": float(sel.strategic_score.sum()),
           "status": pulp.LpStatus[model.status]}
    return out, sel


def logic_ok(df, sel, prerequisites, exclusions):
    ids = set(sel.project_id)
    bad = [f"{a} requires {b}" for a, b in prerequisites if a in ids and b not in ids]
    bad += [f"{a} excludes {b}" for a, b in exclusions if a in ids and b in ids]
    return bad


def run_ip(df, budget, prerequisites=(), exclusions=(), objective="potential"):
    """Integer program: maximise the chosen score total subject to the budget (+ logic)."""
    sense = pulp.LpMinimize if objective == "risk" else pulp.LpMaximize
    model, x, totals = _build(df, budget, prerequisites, exclusions, sense)
    model += totals[objective]
    solve(model)
    out, sel = _summarise(df, x, budget, "Integer Programming", model)
    out["objective_value"] = float(pulp.value(model.objective))
    return out, sel


def payoff_targets(df, budget, prerequisites=(), exclusions=()):
    """Ideal value of each goal alone (risk ideal = empty portfolio = 0) and unit scales."""
    targets = {}
    worst_risk = 0.0
    for k in METRICS:
        sense = pulp.LpMinimize if k == "risk" else pulp.LpMaximize
        model, x, totals = _build(df, budget, prerequisites, exclusions, sense)
        model += totals[k]
        solve(model)
        targets[k] = float(pulp.value(totals[k]))
        if k != "risk":
            worst_risk = max(worst_risk, sum(float(df.loc[df.project_id == p, "risk_score"].iloc[0])
                                             for p in df.project_id if pulp.value(x[p]) > .5))
    scales = {"potential": targets["potential"], "strategic": targets["strategic"],
              "risk": worst_risk - targets["risk"]}
    for k, v in scales.items():
        if not v > 0:
            scales[k] = 1.0  # degenerate goal: keep model well-defined
    return targets, scales


def run_gp(df, budget, weights, prerequisites=(), exclusions=(), targets=None, scales=None):
    """Linear weighted goal program (minimise normalised undesirable deviations)."""
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("At least one GP weight must be positive")
    weights = {k: v / total for k, v in weights.items()}
    if targets is None or scales is None:
        targets, scales = payoff_targets(df, budget, prerequisites, exclusions)
    model, x, totals = _build(df, budget, prerequisites, exclusions, pulp.LpMinimize)
    dev = {}
    for k in METRICS:
        m, p = pulp.LpVariable(f"d_{k}_minus", lowBound=0), pulp.LpVariable(f"d_{k}_plus", lowBound=0)
        model += totals[k] + m - p == targets[k], f"Goal_{k}"
        dev[k] = (m, p)
    model += pulp.lpSum(weights[k] * dev[k][1 if k == "risk" else 0] / scales[k] for k in METRICS)
    solve(model)
    out, sel = _summarise(df, x, budget, "Goal Programming", model)
    out["objective_value"] = float(pulp.value(model.objective))
    out["weights"] = weights
    goals = []
    for k in METRICS:
        bad = float(pulp.value(dev[k][1 if k == "risk" else 0]))
        goals.append({"goal": k, "target": targets[k], "achieved": out[k], "undesirable_deviation": bad,
                      "achievement_pct": 100 * (1 - bad / scales[k]), "weight": weights[k]})
    return out, sel, pd.DataFrame(goals)


def budget_sweep(df, budgets, prerequisites=(), exclusions=()):
    rows = []
    for b in budgets:
        ip, _ = run_ip(df, b, prerequisites, exclusions)
        rows.append({"budget": b, "model": "IP", "potential": ip["potential"], "projects": ip["projects"],
                     "risk": ip["risk"], "strategic": ip["strategic"], "investment": ip["investment"]})
    return pd.DataFrame(rows)
