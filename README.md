# Startup Capital Budgeting

Which startups should an investor fund when the budget is limited?

This project answers that question with two optimisation techniques from Operations Research, applied to a sample of 100 startups from the public Crunchbase dataset, and wraps both in an interactive web app.

## What it does

An investor has a fixed budget (for example $50M) and 100 candidate startups, each with a cost and three scores: investment potential, risk, and strategic fit. Funding everyone would cost about $1.38 billion, so the investor has to choose.

| Technique | Approach |
|---|---|
| **Integer Programming** | Picks the set of startups with the highest total potential within the budget |
| **Goal Programming** | Balances potential, risk and strategic fit together, using priorities the user sets |

## The app

An interactive interface built with Streamlit lets you:

- **Load data:** use the bundled sample or upload your own CSV
- **Explore:** generate statistics and charts on demand
- **Optimise:** choose Integer or Goal Programming, set the budget, weights, sector preferences and logic rules
- **Compare:** see both techniques side by side, sweep the budget, and trace trade-off curves

## Quick start

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at http://localhost:8501.

## Project structure

```
app.py          Streamlit interface
src/            Optimisation models, scoring and validation
config/         Budgets, logic scenarios and preference settings
data/           Raw and processed datasets
results/        Saved results, charts and validation outputs
notebooks/      Dataset exploration
tests/          Unit tests
docs/           Full documentation
```

## Documentation

Everything about the method, results and how to present the project is in [`docs/`](docs/). Start with the **[Project Report](docs/project_report.md)**, which covers the problem, data, models, results, a step-by-step guide to the app, and a presentation guide.

## Tech stack

Python · PuLP (CBC solver) · pandas · NumPy · Streamlit · Plotly

## Notes

The Funding-History Risk Proxy is a score derived from funding history, not a probability of failure. Raw-data counts quoted in the documentation (462,651 entities, 11,259 candidates) are previously reported figures that cannot be re-derived from the files in this repository.
