# Learn the Project from Zero

## 1. What question are we answering?

Imagine an investor with a limited amount of money and many possible startup projects. Buying every project is impossible. **Capital budgeting** means choosing where to allocate limited capital. A **portfolio** is the collection of chosen projects. Our project asks how an explicit mathematical rule selects a portfolio, and how the answer changes when preferences change.

This is an academic historical-data exercise. It does not tell someone which old company to buy today. Every cost and score has a clearly stated meaning and limitation.

## 2. What is the Crunchbase dataset?

The dataset contains historical information about companies, people, organizations, financing and events. It is spread across several CSV tables. The main `objects.csv` contains entities: not every row is a startup. Company attributes include sector, funding received, funding rounds, dates and status. Separate acquisition and IPO tables record events.

The project brief reports **462,651 raw entities** and **11,259 candidates after filtering**. Those are previously reported counts, not numbers independently reverified in this checkout. Only `funds.csv` and `ipos.csv` are available locally; the main objects, funding-round and acquisition tables are missing, and the notebook has no retained outputs establishing those counts. The filtering code is available, and the final 100-project file is available. Say this honestly in the viva.

## 3. How do many entities become candidate companies?

Read the pipeline as a series of filters:

```text
462,651 raw entities (previously reported; not locally reverified)
-> keep Company entities
-> keep positive total funding and at least one funding round
-> first funding year in 2010-2013 inclusive
-> keep the ten selected sectors
-> total historical funding no more than $100M
-> 11,259 candidates (previously reported; not locally reverified)
-> split by sector and funding band
-> sample 2 Low + 3 Medium + 3 High + 2 Very High per sector
-> 10 sectors x 10 companies = 100 verified modelling projects
```

The year restriction concerns **first funding**, not founding date. The $100M cap concerns total funding and limits the candidate universe; it is not a Year-1 budget or the cost of the entire sample. No intermediate row counts are invented.

## 4. Why use 100 instead of all 11,259?

One hundred is manageable for an undergraduate demonstration: we can inspect individual records, explain scores and compare chosen portfolios. It also permits ten examples per sector. It is not a statement that a solver can only handle 100 companies. A larger study could optimize all candidates if the complete data were available and scores were recalibrated for that universe. It could produce different conclusions.

The sample is not automatically representative of all startups. Equal representation by sector is a design choice, not the actual industry distribution.

## 5. What is stratified sampling?

Suppose a bag contains many red balls and few blue balls. A simple random handful may contain almost no blue balls. Splitting by colour and sampling from each group ensures representation. **Stratified sampling** does the analogous thing using sector and funding band.

Our ten sectors are software, biotech, web, mobile, ecommerce, enterprise, games_video, advertising, hardware and medical. Within each sector, historical funding defines four bands:

| Band | Historical funding | Number sampled in each sector |
|---|---|---:|
| Low | Up to $1,500,000 (positive funding only) | 2 |
| Medium | More than $1,500,000 and up to $6,141,490 | 3 |
| High | More than $6,141,490 and up to $20,000,000 | 3 |
| Very High | More than $20,000,000 and up to $100,000,000 | 2 |

The 2/3/3/2 design gives a little more representation to the middle bands while retaining both ends. Do not say that research proved this allocation optimal: it is an existing modelling choice. The notebook uses seed 42 and samples without replacement within each stratum. The final selected dataset is now frozen; no random score is assigned later. The exact origin of the unusual middle cutoff is not recoverable from the available outputs.

## 6. What does the final dataset look like?

Each row represents one company treated as one indivisible project. `project_id` is a study label such as P004; `company_id` retains the original entity identity. The final scored file has 100 rows and 25 columns, including the original data and three scores. There are ten companies per sector. This is the **candidate sample**, not the optimized portfolio: a solver may select only some of those 100.

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

## 7. What is feature engineering?

It means calculating useful variables from existing information. For example, we extract the calendar year from a funding date. Funding duration is last funding year minus first funding year, with missing differences set to zero and negatives clipped to zero. Funding in December 2011 and January 2012 gives one calendar-year difference even though only about a month passed. Two rounds in the same calendar year give zero. It is not company age.

A **funding round** is one recorded financing event. It is not automatically proof of success: repeated funding can indicate confidence or continued capital needs. The model chooses a transparent interpretation, not a universal business truth.

## 8. What does investment cost mean here?

We need a cost in order to apply a budget. The data has total historical funding, but no current price for an ownership stake or future project cash requirements. Therefore the model sets `investment_cost = funding_total_usd`.

If a company's historical total is $4M, the academic model treats selecting it as consuming $4M of the budget. That does **not** mean it can be purchased today for $4M. Always say **Investment Cost Proxy**. It is neither valuation nor expected return.

## 9. What are acquisition, IPO and closed status?

An acquisition is a recorded purchase of a company by another entity. An IPO is an initial public offering, associated with becoming publicly traded. The model flags whether a company's ID occurs in each historical event table. A recorded event does not establish whether every investor made money, and a missing event does not prove it never happened.

Closed status means the dataset records the company as closed. Such a company can still be included as a historical modelling case, and the model does not impose a hard ban on selecting it. This would be inappropriate to interpret as a present-day investment recommendation. The existing IPS gives closed status a low component value; it does not remove the row.

## 10. How do we calculate IPS?

The **Investment Potential Score** combines four components. First, min-max normalization puts rounds and calendar duration on a common 0-100 scale:

`N(value)=100*(value-sample_min)/(sample_max-sample_min)`.

For rounds, the observed minimum is 1 and maximum is 5. A hypothetical company with 3 rounds therefore gets `100*(3-1)/(5-1)=50`. For duration, bounds are 0 and 3 years; a two-year history gives about 66.6667. These are arithmetic illustrations, not newly created data records. The original IPS implementation maps a constant component to 100, although neither of these sample components is constant.

The exact formula is:

`IPS = round(0.30*rounds_score + 0.25*duration_score + 0.25*status_score + 0.20*outcome_score, 2)`.

Status scores are IPO 100, acquired 90, operating 70, closed 20, otherwise 50. Outcome score is `50*(acquisition+ipo)`. One recorded event yields 50 in this component, not 100. The assumptions are the weights, directions and status rubric. IPS is not a percentage return or a probability.

An actual row in the frozen file illustrates all three scores:

P004 (ToutApp) has 3 funding rounds, 2 calendar funding years, status operating, acquisition=0, IPO=0. Its normalized rounds and duration scores are 50.000000 and 66.666667; status score 70, outcome score 0. Thus IPS = 49.17, Funding-History Risk Proxy = 41.666667, Strategic Alignment Score = 100, and investment cost proxy = $4,620,000.

Because IPS uses historical status/outcomes, it is retrospective. Do not call it a prediction of future returns or claim acquisition/IPO guarantees success. Outcome flags and status can overlap in the scoring.

## 11. What is the Funding-History Risk Proxy?

We do not have a reliable measured financial-risk variable. The model uses available history to construct a limited uncertainty proxy:

`R = round(0.50*(100-N(rounds)) + 0.50*(100-N(duration)), 6)`.

More observed rounds/history lowers this score under the chosen interpretation. Higher score means greater modelled uncertainty according to this proxy. It is **not a probability of failure and not direct financial risk**. A value of 80 does not mean an 80% chance of failure. No random risk values or company-by-company guesses were used.

It shares history inputs with IPS, so their correlation is **-0.9600**. IPS increases with funding history while the proxy decreases. This is an important limitation, not evidence that we have independently predicted risk. At portfolio level, the model adds the scores of chosen companies. Ten selected companies can have a higher total than five even if their average scores are lower.

## 12. What is strategic alignment?

Imagine an investor whose mandate focuses on enterprise software. A biotechnology company can be excellent but outside that investor's strategy. Alignment measures fit to a preference, not objective quality.

Our **Decision-maker supplied strategic preference** is a hypothetical enterprise-software investor with this exact mapping:

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

The source supplies the sector; the decision-maker scenario supplies its score. Every company in a sector gets the same score. We cannot infer detailed firm-level fit from a coarse sector label.

## 13. What is Integer Programming?

Optimization searches for the best feasible decision under a stated objective. Integer Programming requires some decision variables to be integers. Here every decision is binary: `x_i=1` selects project i, `x_i=0` skips it. We cannot buy 0.4 of a project in this model.

The baseline asks:

```text
Choose x to maximize sum(IPS_i*x_i)
while sum(C_i*x_i) <= budget
and every x_i is either 0 or 1.
```

A small hypothetical illustration: A costs 6 units and has score 10; B and C each cost 5 and score 8. With budget 10, selecting the highest-scoring individual A gives 10 points, while selecting B and C gives 16. This shows why portfolio selection is about combinations. The illustration does not add companies to the real dataset.

## 14. What are hard constraints and logical scenarios?

A hard constraint may never be violated. Budget is hard; spending beyond it is infeasible. Binary selection is also hard. Baseline has no sector quota, minimum investment or minimum project count.

In a separate assumed scenario, `x_A<=x_B` means selecting A requires B; selecting B does not require A. `x_A+x_B<=1` means choose at most one, including the possibility of neither.

The actual assumed pairs are P005 requires P004, and P003 excludes P004. These are **Scenario-based modelling assumptions**, not Crunchbase observations. We include them to demonstrate how decision-maker-supplied business relationships can constrain a capital-budgeting model.

## 15. What did IP find?

| Budget | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | IP | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125.00 |
| $50M | IP | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625.00 |
| $75M | IP | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900.00 |

All three baseline results are Optimal. This means best attainable IPS under this fixed sample, proxy coefficients and constraints, not best possible real-world investment. Spending need not equal budget exactly because projects are indivisible and no full-spending constraint exists.

## 16. Why use Goal Programming after IP?

IP already answers a clear question: maximize IPS. A decision-maker might also want low total proxy exposure and strong strategic fit. **Goal Programming** expresses desired levels for several measures, then minimizes weighted undesirable deviations. It does not prove one decision philosophy superior.

GP uses the same projects, costs and hard constraints. The three goals are to avoid potential below its target, total Funding-History Risk Proxy above its target, and strategy below its target.

## 17. What is a deviation variable?

A deviation records the gap between an achieved total and a target. The equation is `achieved + d_minus - d_plus = target`, with both deviations nonnegative.

If a hypothetical potential target is 100 and achievement is 80, set `dP_minus=20`, `dP_plus=0`: `80+20-0=100`. If achievement is 110, set the shortfall to zero and overachievement to 10: `110+0-10=100`. These are teaching examples, not the project's actual targets.

| Deviation | Meaning | Undesirable? |
|---|---|---|
| dP- | Potential shortfall | Yes |
| dP+ | Potential overachievement | No |
| dR- | Amount below risk-proxy target | No |
| dR+ | Amount exceeding risk-proxy target | Yes |
| dS- | Strategic shortfall | Yes |
| dS+ | Strategic overachievement | No |

Budget is never relaxed by these variables. Only goal deviations are permitted.

## 18. Where do the targets come from?

For each budget and logical configuration, solve three individual-objective problems: maximize IPS, minimize total Funding-History Risk Proxy and maximize strategy. Each uses the same budget, binary and configured logical constraints. These optima give the ideal targets. A payoff table also records the other achieved measures at each solution. Among tied potential/strategy optima, the implementation minimizes risk proxy.

The best minimum-risk solution selects **nothing**, since every project's risk proxy is positive and investment is optional. Its target is zero. This is a mathematical consequence, not a solver failure. The three ideal goals may be impossible to achieve together. GP provides a compromise, not a promise to achieve all ideals.

| Budget | Logic | P target / scale | R target | S target / scale | R payoff scale |
| --- | --- | --- | --- | --- | --- |
| $25M | baseline | 706.67 | 0.00 | 1,475.00 | 1,887.500000 |
| $50M | baseline | 968.34 | 0.00 | 2,000.00 | 2,745.833334 |
| $75M | baseline | 1,184.18 | 0.00 | 2,375.00 | 3,141.666668 |
| $25M | assumed_logic | 706.67 | 0.00 | 1,475.00 | 1,933.333333 |
| $50M | assumed_logic | 958.34 | 0.00 | 1,975.00 | 2,633.333334 |
| $75M | assumed_logic | 1,168.34 | 0.00 | 2,325.00 | 3,170.833334 |

## 19. Why normalize, and what do weights mean?

The implemented objective is:

`wP*dP_minus/P_scale + wR*dR_plus/R_scale + wS*dS_minus/S_scale`, minimized.

Potential and strategy scales are their target totals. The risk target is zero, so dividing by it would be invalid. Its scale is the largest risk-proxy total in the payoff table minus the minimum-risk target. This is a reference range, not a cap. All penalties are positive: we do not reward excess proxy exposure by subtracting its penalty.

Normalization makes differently sized goals comparable in relative terms. A 10-point shortfall on a target of 100 is 10%; the same shortfall on 1,000 is 1%. Weights then express preference over these relative deviations, not budget allocations.

| Priority scenario | Potential | Risk proxy | Strategy |
| --- | --- | --- | --- |
| balanced | 1/3 | 1/3 | 1/3 |
| potential_focused | 0.60 | 0.20 | 0.20 |
| risk_focused | 0.20 | 0.60 | 0.20 |
| strategy_focused | 0.20 | 0.20 | 0.60 |

Balanced does not mean equal money in each sector. Risk-focused means a greater penalty on normalized risk-proxy excess. It may select fewer projects because total proxy exposure is additive. No weighting is universally best.

## 20. What did GP find?

The main balanced baseline results are:

| Budget | Model | Projects | Investment proxy (USD) | Utilization | IPS points | Funding-History Risk Proxy points | Strategy points |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $25M | GP balanced | 18 | $24,833,829 | 99.34% | 570.01 | 1,337.50 | 1,225.00 |
| $50M | GP balanced | 25 | $49,897,820 | 99.80% | 819.18 | 1,804.17 | 1,725.00 |
| $75M | GP balanced | 30 | $74,862,396 | 99.82% | 1,025.02 | 2,087.50 | 2,000.00 |

At $25M, balanced GP achieves P=570.01, R=1337.500001, S=1225. Targets are P=706.67, R=0, S=1475; the risk scale is 1887.500000. Undesirable deviations are dP-=136.66, dR+=1337.500000, dS-=250. The normalized weighted objective is 0.357162. Other deviations are zero. Small residuals reflect solver output precision.

All 24 main GP outcomes, including the other priorities and the assumed-logic case, are in [final_results_summary.md](final_results_summary.md). Risk-focused baseline selects 7/10/12 projects as budgets rise. These are nonempty portfolios, although choosing none is feasible and is the risk-only anchor.

## 21. How do IP and GP differ in the actual results?

Changes below mean balanced GP minus baseline IP:

| Budget | Change in projects | Change in USD proxy | Change in IPS | Change in risk proxy | Change in strategy |
| --- | --- | --- | --- | --- | --- |
| $25M | -6 | -95,481.00 | -136.66 | -541.67 | +100.00 |
| $50M | -9 | -83,014.00 | -149.16 | -941.67 | +100.00 |
| $75M | -10 | -126,895.00 | -159.16 | -1,054.17 | +100.00 |

GP selects fewer projects, sacrifices IPS, lowers total Funding-History Risk Proxy and improves strategic points. These are the observed trade-offs under the stated weights. The lower proxy total is not proof of lower financial losses, and GP is not automatically better.

## 22. What is sensitivity analysis?

Sensitivity asks whether decisions change when inputs or assumptions change. We compare three budgets, four preference scenarios and a logical-constraint scenario. We track not just total score but which projects enter/leave and which sectors receive investment.

Larger budgets expand the feasible set, so optimal IP IPS cannot decrease. Actual project sets need not be nested. GP changes targets/scales by budget, so its objective cannot be compared across budgets as if its meaning were identical. At $50M/$75M the baseline IP selects P003 and P004 together, so the exclusion scenario changes the portfolio. At $25M it does not. P005 is unselected in these IP results, so the prerequisite is nonbinding there.

## 23. Why was multi-period budgeting omitted?

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

A historical funding date does not tell us how much must be spent in each future year. We did not invent those amounts.

## 24. How do we know the calculations are correct?

The existing checks recompute selected costs, scores, binary decisions, constraints and GP equations from exported decisions. Independent HiGHS models cross-check CBC objectives. Six tests include small cases where every possible portfolio can be enumerated, and deliberately corrupted solutions to check rejection. The rerun has 1586/1586 artifact checks passing across 60 portfolios. The submission also checks hashes so the frozen model/results cannot silently change.

Correct implementation does not validate the economic assumptions. Remember the distinction: observed historical fields; calculated features/scores; assumed cost interpretation and score direction; decision-maker strategy, budgets, logic and weights.

## 25. A short viva answer to practise

"I used a fixed stratified sample of 100 historical startups and treated funding as a cost proxy. IP maximizes the unchanged Investment Potential Score under a hard budget. GP uses the same decisions and budget but balances normalized potential shortfall, Funding-History Risk Proxy excess and strategic shortfall. Targets come from individual-objective optimization, including a zero-risk empty-portfolio ideal. Priorities and logical pairs are explicit scenarios. The results demonstrate trade-offs, not current investment recommendations, and were checked with two solvers and automated validation."
