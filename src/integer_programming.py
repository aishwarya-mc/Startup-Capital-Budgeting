"""Original IPS and budget-only IP, with optional scenario logical constraints.
The original complete script is preserved in docs/archive/integer_programming_original.py.
"""
import pandas as pd
from portfolio_model import (ROOT, RESULTS, config, load_data, build_model, solve,
                             extract, validate, save_results)

def normalize(series):
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(100.0, index=series.index)

    return (
        (series - min_value)
        / (max_value - min_value)
        * 100
    )


def calculate_ips(df):
    df = df.copy()
    df["rounds_score"] = normalize(
        df["funding_rounds"]
    )
    
    df["duration_score"] = normalize(
        df["funding_duration_years"]
    )
    
    
    status_scores = {
        "ipo": 100,
        "acquired": 90,
        "operating": 70,
        "closed": 20
    }
    
    df["status_score"] = (
        df["status"]
        .map(status_scores)
        .fillna(50)
    )
    
    
    df["outcome_score"] = (
        (df["acquisition"] + df["ipo"]) / 2
    ) * 100
    
    
    df["investment_potential_score"] = (
        0.30 * df["rounds_score"]
        + 0.25 * df["duration_score"]
        + 0.25 * df["status_score"]
        + 0.20 * df["outcome_score"]
    )
    
    df["investment_potential_score"] = (
        df["investment_potential_score"].round(2)
    )
    
    return df


def solve_portfolio(budget, logical_scenario="baseline", df=None):
    df = load_data() if df is None else df
    model, x, totals = build_model(df, budget, logical_scenario)
    model += totals["potential"]
    solve(model)
    result = extract(df, model, x, budget, logical_scenario, "IP")
    checks = validate(df, result)
    if not all(c["passed"] for c in checks):
        raise AssertionError(checks)
    return result


def main():
    df = load_data()
    expected = calculate_ips(df)
    pd.testing.assert_series_equal(expected.investment_potential_score, df.investment_potential_score)
    results = [solve_portfolio(b, scenario, df) for scenario in config()["logical_scenarios"] for b in config()["budgets"]]
    save_results(results, "ip")
    report = pd.DataFrame([c for r in results for c in validate(df, r)])
    report.to_csv(RESULTS / "ip_validation.csv", index=False)
    print(pd.DataFrame([r["summary"] for r in results]).to_string(index=False))
    print(f"Validation: {report.passed.sum()}/{len(report)} passed")


if __name__ == "__main__":
    main()
