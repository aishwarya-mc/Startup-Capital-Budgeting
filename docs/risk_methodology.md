# Funding-History Risk Proxy

The report term is **Funding-History Risk Proxy** (code column `risk_score`).
It is **not direct financial risk**. This derived 0-100 index is not an estimated probability of
failure, volatility, loss or financial due diligence. No observed risk label or
validated predictive model is available. Higher scores mean less funding-history
evidence under an explicit maturity/uncertainty interpretation.

## Alternatives assessed before selection
| Alternative | Reason not selected |
|---|---|
| Status/acquisition/IPO penalties | Retrospective outcomes can leak future information; exits are not guaranteed successes. |
| Historical funding size as exposure | Largely duplicates the investment-cost proxy; size alone is not failure risk. |
| Missing founded date/country | Measures record completeness rather than startup financial risk; missingness is not failure. |
| Funding rounds alone | Simple but ignores whether repeated observations span any time. |
| Rounds and calendar funding duration | Selected: two observable history dimensions, no outcome or IPS inputs, equal weights. |

For sample min-max normalization `N(z)=100*(z-min(z))/(max(z)-min(z))`:

`R_i = round(0.5*(100-N(funding_rounds_i)) + 0.5*(100-N(funding_duration_years_i)), 6)`.

| Source column | Transformation/normalization | Weight | Interpretation | Limitation |
|---|---|---:|---|---|
| funding_rounds | Reverse min-max; sample bounds 1 and 5 | 0.50 | Fewer observed rounds imply less repeated financing evidence | Many rounds can indicate capital dependence; direction is an assumption. |
| funding_duration_years | Reverse min-max; sample bounds 0 and 3 | 0.50 | Shorter history implies less time over which financing was observed | Calendar-year difference, not exact age; same-year rounds yield zero; right-censoring near 2013. |

Equal weights are a transparent modelling choice, not estimated coefficients.
Bounds are fitted once to the **same full 100-project sample**, never separately
to a selected portfolio or budget. A constant/invalid component fails explicitly
rather than silently assigning arbitrary values. No random or manual firm-level
scores. Both components range 0-100, so the convex combination does too.

The score does not depend on IPS, selection, optimization outcomes, status,
acquisition or IPO. It shares two source variables with IPS, so correlation and
partial redundancy are expected and reported in score_correlations.csv; do not
describe the goals as statistically independent. This is a retrospective sample
exercise, not a train/test prediction task. Prospective use would require a fixed
decision date, only then-available features and external validation. Existing IPS
itself contains outcomes and is retained, not relabelled as a predictive measure.

Portfolio risk is `sum(R_i*x_i)`, a linear cumulative index with units of
score-points. It tends to rise with portfolio size. It is not variance, expected
loss, a diversified-risk estimate or an average. No correlations are modelled.

Reproduction: `python src/score_projects.py --risk-only` (risk phase), then
`python src/score_projects.py` after strategy configuration. Statistics, bounds,
range/finiteness, monotonicity, identical-input and preservation checks are saved
under results/optimization/score* and scores_by_sector.csv.

Observed sample Pearson correlation between risk and IPS is **-0.9600**. This
strong redundancy is a material limitation: the proxy provides a different
portfolio aggregation/goal preference, not independent evidence of financial risk.
