# Phase 0: audit before implementation

> Historical phase-0 audit, retained for provenance. Statements about missing work below describe the pre-extension state. Current status: [final model audit](final_model_audit.md).

Inspected every source script, notebook cell, documentation file, CSV schema and
dataset contents, existing result tables and the repository file inventory.
Original implementation and documentation are retained in `docs/archive/`;
the pre-extension SHA256 manifest records all original artifacts.

## Completed
- 100 distinct companies/projects; ten sectors, ten projects each.
- Stratified sample: each sector has 2 Low, 3 Medium, 3 High, 2 Very High funding
  projects, sampled with random_state=42. This existing sampling is preserved.
- Exploration and statistical notebooks; five existing exploratory charts.
- IPS and budget-only binary IP, using PuLP/CBC.
- All original scored values recompute correctly; original selected rows
  reproduce the saved summary totals.

## Partially completed
- Logical constraints appear only in comments: P005 requires P004;
  P003/P004 are mutually exclusive. Both are modelling assumptions, not observed.
- Raw reconstruction: only funds.csv (1,564 rows) and ipos.csv (1,259 rows) are
  present. objects.csv, funding_rounds.csv, acquisitions.csv and other files
  referenced by the exploration notebook are absent (listed in .gitignore).
  The processed dataset exists, but full raw provenance cannot be re-executed here.
- No automated solver/constraint validation. PuLP was absent from the environment.

## Missing
Risk and strategic scores, GP, payoff targets, priority scenarios, comparison,
sensitivity, optimization-specific figures and validation reports.
No sector constraints or multi-period budgets exist.

## Existing formulation and assumptions
`N(z)=100*(z-min(z))/(max(z)-min(z))`, or 100 if constant.
`IPS=round(.30*N(rounds)+.25*N(duration)+.25*status_score+.20*outcome_score,2)`.
Status mapping: ipo=100, acquired=90, operating=70, closed=20, unknown=50.
`outcome_score=50*(acquisition+ipo)`.
Maximize `sum(IPS_i*x_i)` subject to `sum(cost_i*x_i)<=B`, binary x.
Cost is total historical funding, not a prospective investment quote.
Duration is **difference in calendar funding years**, not exact elapsed years;
missing differences were filled with zero and negative differences clipped.
IPS weights/status mapping are assumptions. IPS is retrospective and includes
historical outcomes; it is not a leakage-free future-return predictor.

| Budget | Status | Projects | Cost USD | IPS | Utilization % |
|---:|---|---:|---:|---:|---:|
|25000000|Optimal|24|24929310|706.67|99.71724|
|50000000|Optimal|33|49926434|958.34|99.852868|
|75000000|Optimal|40|74589291|1168.34|99.452388|

Original scored CSV columns (23): project_id, company_id, startup_name, sector,
country_code, status, founded_at, first_funding_at, last_funding_at,
first_funding_year, last_funding_year, funding_duration_years, funding_rounds,
funding_total_usd, investment_cost, acquisition, ipo, funding_band, rounds_score,
duration_score, status_score, outcome_score, investment_potential_score.
No missing optimization inputs; country_code has 9 missing values and founded_at
has 20. Original scored base columns match startup_projects.csv exactly.

## Phase 1 verification finding
Fresh budget-only CBC solves give IPS 706.67, 968.34, 1184.18; the latter two
exceed the saved 958.34 and 1168.34. Thus the saved results do not represent
optima of the currently active source formulation. Fresh assumed-logic solves
give the original objective values at all budgets. This suggests a historical
configuration mismatch, but its cause cannot be established from this checkout.
Original results are retained; authoritative new results are in
`results/optimization/ip_summary.csv`, explicitly labelled by logical scenario.
