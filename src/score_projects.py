"""Append reproducible risk/strategy scores without modifying existing IPS/data."""
import json
import numpy as np
import pandas as pd
from portfolio_model import ROOT, SCORED, RESULTS, load_data, config


def funding_history_risk(df):
    components = {}
    for col in ["funding_rounds", "funding_duration_years"]:
        v = df[col]
        if not np.isfinite(v).all() or (v < 0).any() or v.max() == v.min():
            raise ValueError(f"Cannot calibrate risk from {col}: missing/invalid/constant values")
        components[col] = 100 * (v.max() - v) / (v.max() - v.min())
    return .5 * components["funding_rounds"] + .5 * components["funding_duration_years"]


def strategic_alignment(df, strategy):
    mapping = strategy["sector_scores"]
    unknown = set(df.sector) - set(mapping)
    if unknown:
        raise ValueError(f"Specify strategic priorities for sectors: {sorted(unknown)}")
    if not all(np.isfinite(v) and 0 <= v <= 100 for v in mapping.values()):
        raise ValueError("Strategic values must be finite and within 0-100")
    return df.sector.map(mapping).astype(float)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk-only", action="store_true")
    args = parser.parse_args()
    df = load_data()
    original = df.copy()
    df["risk_score"] = funding_history_risk(df).round(6)
    if not args.risk_only:
        df["strategic_score"] = strategic_alignment(df, config()["strategy"])
    # Existing base fields and IPS must remain identical.
    unchanged = [c for c in original if c not in ["risk_score", "strategic_score"]]
    pd.testing.assert_frame_equal(original[unchanged], df[unchanged])
    scores = [c for c in ["risk_score", "strategic_score"] if c in df]
    assert np.isfinite(df[scores].to_numpy()).all()
    assert df[scores].ge(0).all().all() and df[scores].le(100).all().all()
    assert df.groupby(["funding_rounds", "funding_duration_years"]).risk_score.nunique().max() == 1
    # More rounds or longer history can never increase risk, holding the other fixed.
    for fixed, varied in [("funding_rounds", "funding_duration_years"), ("funding_duration_years", "funding_rounds")]:
        for _, group in df.groupby(fixed):
            assert (group.sort_values(varied).risk_score.diff().dropna() <= 1e-6).all()
    df.to_csv(SCORED, index=False)
    RESULTS.mkdir(parents=True, exist_ok=True)
    df[scores].describe().T.to_csv(RESULTS / "score_summary.csv")
    df[["funding_rounds", "funding_duration_years", "investment_potential_score"] + scores].corr().to_csv(RESULTS / "score_correlations.csv")
    df.groupby("sector")[scores].agg(["min", "mean", "max"]).to_csv(RESULTS / "scores_by_sector.csv")
    checks = {"rows": len(df), "original_columns_unchanged": True,
              "scores_finite_and_in_range": True, "equal_inputs_equal_risk": True,
              "risk_monotone_in_each_component": True,
              "risk_rounds_bounds": [float(df.funding_rounds.min()), float(df.funding_rounds.max())],
              "risk_duration_bounds": [float(df.funding_duration_years.min()), float(df.funding_duration_years.max())]}
    (RESULTS / "score_validation.json").write_text(json.dumps(checks, indent=2))
    print(df[scores].describe().to_string())
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
