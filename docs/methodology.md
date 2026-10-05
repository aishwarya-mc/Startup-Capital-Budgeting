# Methodology: Startup Capital Budgeting: Portfolio Optimization

This final methodology describes the frozen implementation, not a redesigned model. Tables are rendered from the validated outputs by `src/build_submission_docs.py`. See [final audit](final_model_audit.md) and [final results](final_results_summary.md).

## 1. Problem Definition

Capital budgeting allocates limited capital among competing projects. Here each historical startup is treated as an indivisible modelling project. The decision is which subset to include at a budget of $25M, $50M or $75M. IP maximizes one primary score. GP balances shortfalls/excess against three aspiration levels. These are historical modelling experiments, not recommendations to invest in those companies today.

The implemented pipeline is:

```text
Raw Crunchbase Dataset -> Filtering / preprocessing
-> 100-project stratified dataset -> Feature engineering
-> Investment Potential Score -> Funding-History Risk Proxy
-> Strategic Alignment Score -> Integer Programming -> Goal Programming
-> Budget scenarios -> Priority scenarios -> Logical-constraint scenarios
-> IP vs GP comparison -> Sensitivity analysis -> Validation
```

The notebooks document the raw-to-sample stages. This checkout can reproduce the stages from the existing processed sample onward; missing source tables prevent complete raw reconstruction.

## 2. Dataset

Crunchbase historical tables record companies and other entities, financing activity and company events. An entity is not necessarily a startup: the main entity table also includes other entity types. `objects.csv` supplies company attributes; `acquisitions.csv` and `ipos.csv` identify recorded events. `funding_rounds.csv` supports exploration of individual financing events. A funding round is a recorded financing event, not a year of expenditure.

Only `funds.csv` and `ipos.csv` are present under `data/raw/`. The main objects, funding-round and acquisition files referenced by the notebook are absent. **462,651 raw entities** and **11,259 candidate companies** are previously reported counts supplied in the project brief; they cannot be independently verified from the supplied files or notebook outputs. Intermediate filtering counts are not invented. The final 100 rows, identities, fields and sample allocation are directly verifiable.

The historical coverage ends around 2013. The final sample includes operating, acquired, IPO and closed statuses. A closed company remains a historical modelling record; there is no hard eligibility rule excluding it from optimization. It must not be presented as currently investable.

## 3. Dataset Filtering

`notebooks/01_dataset_exploration.ipynb` specifies these steps in order:

1. Select `entity_type == "Company"` with `funding_total_usd > 0` and `funding_rounds > 0`.
2. Parse first and last funding dates using coercion for invalid dates.
3. Retain companies whose **first funding year** is 2010 through 2013 inclusive. This is not a founding-year filter or merely any activity in those years.
4. Map missing category codes to `unknown`, then retain the ten named sectors below.
5. Apply `funding_total_usd <= 100_000_000`.
6. Assign funding bands and sample within sector-band groups.

The $100M cap is a modelling filter on historical funding, distinct from each optimization budget. A sampled company costing more than a scenario budget can remain in the dataset; its binary variable must be zero in that scenario.

## 4. Why 100 Projects Were Selected

One hundred projects provide a manageable, inspectable undergraduate demonstration with deliberate representation of sectors and funding scales. Ten sectors times ten companies produces 100 binary decisions. This is a study-design choice, not a statistically calculated sample-size requirement or a solver limit.

Optimizing all 11,259 previously reported candidates would be a different empirical scope, not mathematically forbidden. It would require the complete source data, score calibration on that universe and an assessment of solver performance. Conclusions here apply to this fixed sample; no population-wide optimality is claimed.

## 5. Stratified Sampling

Stratification divides the candidate pool into groups before sampling. The notebook uses sector and historical funding band as the strata. It samples without replacement within each group using `random_state=42`; randomness occurs in this original sample selection, not in the final scoring rules. The sample is now frozen.

| Band | Historical funding interval (USD) | Per sector | Across 10 sectors |
|---|---|---:|---:|
| Low | Positive, up to 1,500,000 | 2 | 20 |
| Medium | Over 1,500,000, up to 6,141,490 | 3 | 30 |
| High | Over 6,141,490, up to 20,000,000 | 3 | 30 |
| Very High | Over 20,000,000, up to 100,000,000 | 2 | 20 |

`pandas.cut` uses right-closed intervals. The unusual $6,141,490 threshold is an existing fixed preprocessing cutoff; its statistical derivation is not established by the available notebook outputs. The 2/3/3/2 allocation gives slightly more representation to middle funding scales while retaining both extremes; this describes its effect, not an empirically proven optimal allocation. Equal sector counts are not proportional to the original population.

| Sector | Low | Medium | High | Very High |
| --- | --- | --- | --- | --- |
| advertising | 2 | 3 | 3 | 2 |
| biotech | 2 | 3 | 3 | 2 |
| ecommerce | 2 | 3 | 3 | 2 |
| enterprise | 2 | 3 | 3 | 2 |
| games_video | 2 | 3 | 3 | 2 |
| hardware | 2 | 3 | 3 | 2 |
| medical | 2 | 3 | 3 | 2 |
| mobile | 2 | 3 | 3 | 2 |
| software | 2 | 3 | 3 | 2 |
| web | 2 | 3 | 3 | 2 |

## 6. Feature Engineering

Project IDs P001-P100 identify sample rows; company IDs retain historical identity. Name/category columns are renamed to `startup_name`/`sector`. First/last funding years are extracted from dates. `funding_duration_years = last_funding_year - first_funding_year`, with missing differences filled with zero and negatives clipped to zero. This is a difference in calendar years, not exact elapsed time or company age.

Acquisition and IPO flags are company-ID membership indicators in event tables. One means a recorded event; zero does not prove that no event ever occurred. Neither indicator establishes profitable investor returns. Original missing country/founding-date values are retained because the optimization scores do not require them. The final dictionary covers all 25 columns: [data_dictionary.csv](data_dictionary.csv).

| Measure | Verified value |
| --- | --- |
| Projects / sectors | 100 / 10 |
| Investment proxy: minimum / median / mean / maximum | $7,208 / $5,950,000 / $13,795,944 / $100,000,000 |
| Total historical funding | $1,379,594,386 |
| Mean funding rounds / calendar funding duration | 1.88 / 0.89 years |
| IPS range / mean | 5.00-65.00 / 32.2417 |
| Funding-History Risk Proxy range / mean | 12.50-100.00 / 74.1667 |
| Strategy range / mean | 0-100 / 50.00 |
| Statuses | operating: 92; acquired: 3; ipo: 3; closed: 2 |
| Recorded acquisition / IPO indicators | 3 / 3 |
| Missing country / founded date | 9 / 20 |

## 7. Investment Cost Proxy

`C_i = investment_cost_i = funding_total_usd_i` in USD. The equality is verified in the sample. Historical funding supplies a reproducible size-related cost proxy because a current investment price or future capital requirement is unavailable. It is **not a current purchase price, valuation, expected cash flow or new financing requirement**. The model purchases a whole hypothetical project at this proxy cost; partial investment and ownership fractions are not modelled.

## 8. Investment Potential Score

Let `N(z_i)=100*(z_i-min(z))/(max(z)-min(z))`, calibrated on all 100 projects. The original IPS normalizer returns 100 for a constant column. Existing bounds are rounds 1-5 and duration 0-3.

`IPS_i = round(0.30*N(funding_rounds_i) + 0.25*N(funding_duration_years_i) + 0.25*status_score_i + 0.20*outcome_score_i, 2)`.

| Component / variable | Source | Transformation / normalization | Weight | Interpretation under the model |
|---|---|---|---:|---|
| `rounds_score` | Historical `funding_rounds`, originally objects table | Sample min-max to 0-100 | 0.30 | Repeated financing evidence contributes positively. |
| `duration_score` | Derived `funding_duration_years` from funding dates | Sample min-max to 0-100 | 0.25 | Longer observed financing history contributes positively. |
| `status_score` | Historical status | IPO 100, acquired 90, operating 70, closed 20; unknown 50 | 0.25 | Assumed historical-status preference; no further normalization. |
| `outcome_score` | Acquisition/IPO membership flags from event tables | `50*(acquisition+ipo)`, possible values 0, 50, 100 | 0.20 | Recorded events contribute positively under an assumed rubric. |

Weights and status values are modelling assumptions, not coefficients fitted to returns. Outcomes/status may duplicate information. Historical outcomes in IPS prevent claiming this is a prospective prediction free from leakage. IPS is a relative heuristic score, not NPV, ROI, money or success probability. The exact original formula and two-decimal rounding are preserved.

P004 (ToutApp) has 3 funding rounds, 2 calendar funding years, status operating, acquisition=0, IPO=0. Its normalized rounds and duration scores are 50.000000 and 66.666667; status score 70, outcome score 0. Thus IPS = 49.17, Funding-History Risk Proxy = 41.666667, Strategic Alignment Score = 100, and investment cost proxy = $4,620,000.

## 9. Funding-History Risk Proxy

The code column remains `risk_score`. Its report name is **Funding-History Risk Proxy**:

`R_i = round(0.50*(100-N(funding_rounds_i)) + 0.50*(100-N(funding_duration_years_i)), 6)`.

Each source uses reverse full-sample min-max normalization; weights are 0.50 and 0.50. Fewer rounds and shorter funding history represent less observed financing evidence and hence greater modelled uncertainty under the chosen interpretation. Equal weights and these directions are assumptions. Unlike the original IPS normalizer, the risk scorer explicitly rejects constant or invalid calibration components.

This is **not a probability of failure and not direct financial risk**. It is a proxy based only on available historical funding information. It does not estimate losses, cash-flow uncertainty, volatility or inter-company covariance. Long history can reflect persistence but also financing dependence; recent firms have shorter observation windows. Calendar duration is coarse.

The observed Pearson correlation with IPS is **-0.9600**. Both depend on related funding-history variables, in opposite directions. Risk is not calculated from IPS itself, so the definition is not circular, but the two scores are strongly redundant. They do not provide independent evidence of attractiveness and financial risk. See [risk_methodology.md](risk_methodology.md) for alternatives considered.

Portfolio risk proxy is `R(x)=sum(R_i*x_i)`, an additive total in score-points. Selecting fewer projects can lower this total even without improving average startup quality. No nonlinear average-risk expression is used.

## 10. Strategic Alignment Score

This is a **Decision-maker supplied strategic preference**, not an objective industry ranking or a historical Crunchbase measurement. The implemented profile is a hypothetical enterprise-software investor. Core software/enterprise receives the highest preference, adjacent digital markets partial preference and specialist life-science sectors zero mandate fit. Zero is not a claim of poor economic quality.

`S_i = config["strategy"]["sector_scores"][sector_i]`.

| Sector | Strategic Alignment Score |
| --- | --- |
| software | 100 |
| enterprise | 100 |
| web | 75 |
| mobile | 75 |
| ecommerce | 50 |
| hardware | 50 |
| advertising | 25 |
| games_video | 25 |
| biotech | 0 |
| medical | 0 |

There is no extra normalization or company-specific override. All firms in a sector receive the same score. The numeric spacing and additive treatment are preference assumptions, not estimated utility. Missing/unmapped sectors fail explicitly. The verified configuration is frozen for submission.

## 11. Integer Programming Formulation

For startup `i=1,...,100`, `x_i=1` if selected, and `x_i=0` otherwise.

```text
Maximize    sum(IPS_i * x_i)
subject to  sum(C_i * x_i) <= B
            x_i in {0,1} for every i
```

This is a 0-1 knapsack formulation. Baseline has no sector quotas, logical pairs, minimum number selected or minimum budget utilization. Unspent budget is allowed. Coefficients are fixed before solving; CBC sees dollar costs divided by one million for numerical conditioning, without changing the inequality. Binary variables prevent fractional project selection.

Authoritative baseline results from `ip_summary.csv`:

| Budget | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 |
| $50M | IP | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625.00 |
| $75M | IP | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900.00 |

## 12. Logical Constraint Scenario

**Scenario-based modelling assumptions** are separate from baseline. In general, `x_A <= x_B` means A can be selected only if B is also selected; it does not force A when B is selected. `x_A+x_B<=1` means both cannot be selected simultaneously; choosing neither is permitted.

The exact configured pairs are:

- Prerequisite: **P005 (Imimtek) requires P004 (ToutApp)**: `x_P005 <= x_P004`.
- Mutual exclusion: **P003 (BestVendor) and P004 (ToutApp)**: `x_P003+x_P004 <= 1`.

These were commented illustrative examples, not Crunchbase-derived business relationships. Their purpose is to demonstrate how a decision-maker's supplied interdependencies can be represented in capital-budgeting IP. `baseline` leaves both disabled; `assumed_logic` enables them. Both IP and GP share the configured hard constraints. Their exact effects are reported in [final results](final_results_summary.md).

## 13. Goal Programming Formulation

GP adds aspirations rather than replacing the hard budget. Define `P_i=IPS_i`, `R_i=Funding-History Risk Proxy_i`, `S_i=Strategic Alignment Score_i`, and `C_i=Investment Cost Proxy_i`. Let `P(x),R(x),S(x)` denote the corresponding selected sums.

```text
P(x) + dP_minus - dP_plus = P_target
R(x) + dR_minus - dR_plus = R_target
S(x) + dS_minus - dS_plus = S_target
all six deviations >= 0
```

| Variable | Meaning | Penalized? |
|---|---|---|
| dP_minus | Potential shortfall below target | Yes |
| dP_plus | Potential overachievement above target | No |
| dR_minus | Amount below the total risk-proxy target | No |
| dR_plus | Total risk-proxy excess above target | Yes |
| dS_minus | Strategic shortfall below target | Yes |
| dS_plus | Strategic overachievement above target | No |

The implemented objective is:

`Minimize wP*(dP_minus/P_scale) + wR*(dR_plus/R_scale) + wS*(dS_minus/S_scale)`.

All terms are added with positive weights. Normalization makes deviations dimensionless relative to goal references because the three portfolio totals have different numerical scales. Equal raw deviations do not imply equal relative shortfalls. The budget, binary restrictions and enabled logical pairs remain hard; aspiration equations permit deviations rather than making every target compulsory. Weights are compensatory, not lexicographic.

All expressions are linear: score coefficients, targets, scales and weights are constants during a solve. GP remains a mixed-integer linear model with binary project variables and continuous deviations. The achievement index is `1-undesirable_deviation/scale`; it is not a probability and can be negative beyond the payoff reference range.

## 14. GP Target Generation

Targets are generated independently for every budget and logical configuration by `payoff_targets` in `src/goal_programming.py`.

| Target | Optimization | Hard constraints | Reason for using the result |
|---|---|---|---|
| P_target | Maximize total IPS | Same budget, binary variables and enabled logical pairs | Best feasible potential defines an attainable individual aspiration. |
| R_target | Minimize total Funding-History Risk Proxy | Same constraints; no investment/size floor | Best feasible total proxy defines the individual low-risk ideal. |
| S_target | Maximize total Strategic Alignment Score | Same constraints | Best feasible alignment defines the individual strategy aspiration. |

For P and S anchors, a second solve minimizes total risk proxy while preserving the primary optimum within `1e-7` score-points. This tie-break affects the anchor composition and risk normalization, not the primary ideal target. The payoff table records all three measures achieved at each anchor. In `payoff_summary.csv`, `primary_optimum` contains the target; `objective` for P/S rows contains the second-stage risk-proxy objective, so it must not be mistaken for P or S.

All sample risk-proxy scores are positive, so the minimum-risk anchor selects **zero projects**, spends zero and gives `R_target=0`. There is no minimum investment constraint. This is mathematically valid, but means the ideal asks to avoid all additive risk exposure. Strong risk preference can therefore favor small or empty portfolios. The observed main risk-focused scenarios are nonempty; no floor was inserted to force that outcome.

Set `P_scale=P_target`, `S_scale=S_target`. Dividing by `R_target=0` is invalid, so the implementation uses:

`R_scale = max(total risk proxy across the three payoff anchors) - R_target`.

This is a payoff-table range, not a maximum over every feasible portfolio and not a hard risk cap. Nonpositive scales raise an error. Ideal targets need not be jointly achievable; GP measures their compromise. The ideal-point policy is a modelling choice; the numerical targets are calculated, not manually invented.

| Budget | Logic | P target / scale | R target | S target / scale | R payoff scale |
| --- | --- | --- | --- | --- | --- |
| $25M | baseline | 706.67 | 0.00 | 1,475.00 | 1,887.500000 |
| $50M | baseline | 968.34 | 0.00 | 2,000.00 | 2,745.833334 |
| $75M | baseline | 1,184.18 | 0.00 | 2,375.00 | 3,141.666668 |
| $25M | assumed_logic | 706.67 | 0.00 | 1,475.00 | 1,933.333333 |
| $50M | assumed_logic | 958.34 | 0.00 | 1,975.00 | 2,633.333334 |
| $75M | assumed_logic | 1,168.34 | 0.00 | 2,325.00 | 3,170.833334 |

The four priorities share targets/scales within each budget/configuration. Assumed-logic runs normally recalibrate them. Additional `gp_fixed_targets_*` runs retain baseline targets/scales while adding logic to isolate feasibility effects.

At $25M, balanced GP achieves P=570.01, R=1337.500001, S=1225. Targets are P=706.67, R=0, S=1475; the risk scale is 1887.500000. Undesirable deviations are dP-=136.66, dR+=1337.500000, dS-=250. The normalized weighted objective is 0.357162. Other deviations are zero. Small residuals reflect solver output precision.

## 15. GP Priority Scenarios

Exact values from the frozen configuration:

| Priority scenario | Potential | Risk proxy | Strategy |
| --- | --- | --- | --- |
| balanced | 1/3 | 1/3 | 1/3 |
| potential_focused | 0.60 | 0.20 | 0.20 |
| risk_focused | 0.20 | 0.60 | 0.20 |
| strategy_focused | 0.20 | 0.20 | 0.60 |

These are decision-maker preference scenarios, not universally optimal weights. A 0.60 weight applies to normalized deviation, not to a percentage allocation of budget or project count. The weights sum to one, but multiplying all by the same positive constant would not change the minimizing portfolios. Solver-selected members may differ under ties.

## 16. Sensitivity Analysis

Budget sensitivity compares $25M/$50M/$75M on the same 100 projects. Priority sensitivity changes GP weights while holding a budget/configuration's targets fixed. Logical sensitivity compares baseline to the assumed pairs, with both recalibrated and fixed-target GP comparisons. Reported measures include selections, cost, utilization, IPS, risk proxy, strategy, sector counts/costs and Jaccard selection overlap.

Increasing the budget expands IP's feasible set, so its optimal IPS cannot fall; the actual selected set need not be nested. GP targets/scales change by budget, so its objective values cannot be read as a single common welfare scale. Compare achieved measures and deviations explicitly. Full results and sector changes are in [final_results_summary.md](final_results_summary.md).

## 17. Model Validation

Existing tests and artifact validation are rerun without changing model outputs. Checks cover binary selections, solver status, budget, logical constraints, recomputed counts/cost/scores, all GP equations, nonnegative deviations, normalized reporting and recomputed objectives. The full set gives **1586/1586 passed checks across 60 portfolios**. Six existing tests cover exhaustive small instances, invalid inputs and corrupted solutions.

CBC must report both an optimal problem status and optimal solution status. Independent SciPy/HiGHS formulations cross-check the exported objectives, including payoff risk tie-breaks and fixed-target GP. The baseline potential anchors additionally match IP optima. Validation checks numerical implementation, not real-world accuracy of the proxy assumptions. Submission hashes verify frozen data, configuration, mathematical source and numerical results. [Validation report](../results/optimization/validation_report.md).

## 18. Assumptions

| Category | What it contains |
|---|---|
| Dataset-derived information | Historical identity, sector, status, funding rounds/totals/dates and recorded events. |
| Derived/calculated | Project IDs, calendar years/duration, funding bands, event indicators, cost proxy, normalized components, scores and optimized portfolio totals. |
| Modelling assumptions | Sample/filter design, cost interpretation, indivisibility, additive scores, IPS weights/status values, risk directions/equal weights, single-period budgets, payoff ideal policy and normalization. |
| Decision-maker inputs | Budget scenarios, hypothetical sector preference map, GP weights, and separately supplied scenario logical relationships. |

A quantity can be reproducibly calculated yet still depend on an assumption: `investment_cost` and `strategic_score` are examples. Reproducibility does not make them observed market prices or objective preferences.

## 19. Limitations

- Historical funding is a proxy, not a current investment price; cash flows and time value are not available for an NPV model.
- The dataset ends around 2013; closed or exited firms are historical cases, not current investment opportunities.
- A deliberately stratified 100-company sample is not representative of the population. Candidate and raw counts remain previously reported, not reverified.
- IPS uses retrospective outcomes and assumed weights; exits do not prove profitable returns. Status and outcomes can overlap.
- Funding-History Risk Proxy is unvalidated, strongly inversely related to IPS and affected by observation windows. It is not failure probability or direct financial risk.
- Total proxy exposure depends on portfolio size; no covariance, diversification or average-risk metric is modelled.
- Strategic alignment is a hypothetical investor's supplied preference. Sector groups and numeric utility spacing are coarse assumptions.
- Logical pairs are scenario assumptions; their existence is not established by Crunchbase.
- Targets and normalized weights influence the GP compromise; no single preference is universally best.
- Missing source files prevent raw-to-sample reconstruction here. Processed-data-to-results reproduction is available.

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

No UI or Nonlinear Programming is part of this submission. These omissions are explicit scope decisions, not implemented features.
