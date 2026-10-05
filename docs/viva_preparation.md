# Viva Preparation: Questions and Answers

These answers match the frozen implementation. Use **Funding-History Risk Proxy**, **Investment Cost Proxy**, **Decision-maker supplied strategic preference**, and **Scenario-based modelling assumptions** precisely. Detailed derivations are in [methodology](methodology.md); authoritative tables are in [final results](final_results_summary.md).

## Dataset and sampling

### 1. What is your project about?
Selecting a subset of 100 historical startup projects under limited capital, using IP to maximize IPS and GP to balance potential, funding-history uncertainty and strategic preferences.

### 2. Why is this an Operations Research problem?
It combines competing choices, scarce resources, an explicit objective and constraints. Mathematical optimization finds a feasible portfolio and exposes trade-offs.

### 3. What is capital budgeting?
Choosing projects to receive limited capital. Here the capital requirement is approximated by historical funding rather than measured future cash expenditure.

### 4. What is Crunchbase information in this study?
Historical company/entity attributes, financing totals/rounds/dates and event records. The underlying tables include objects, funding rounds, acquisitions and IPOs; not all are present locally.

### 5. Are all 462,651 entities startups?
No. That is a previously reported raw entity count, and entities can include non-company types. The notebook explicitly filters Company entities. The raw count cannot be independently reverified in this checkout.

### 6. Can you prove the 11,259 candidate count from the repository?
Not from the available files: the main raw tables and relevant saved outputs are absent. It is a previously reported count supplied in the project brief. The filtering code and final 100 records are available and inspected; I do not invent intermediate counts.

### 7. What filters were used?
Company type; positive total funding and funding rounds; first funding year 2010-2013 inclusive; ten named sectors; total funding at most $100M; then sector-band sampling.

### 8. Does 2010-2013 mean the companies were founded then?
No. It is the first funding year. Founded dates are separate and can be missing.

### 9. Why only 100 projects from the reported 11,259?
It is a manageable, inspectable academic demonstration with ten examples in each of ten sectors. It is not a statistically derived sample size or a solver capacity limit.

### 10. Why not optimize all 11,259?
That is possible in principle, but would require the complete candidate data, appropriate score calibration and a larger study. The current conclusions are explicitly limited to the fixed sample; I do not claim the solver could not handle more.

### 11. What is stratified sampling?
Dividing the population into groups and sampling within each. Here strata combine sector and funding band, so every selected sector and funding scale is represented.

### 12. Why 2 Low, 3 Medium, 3 High and 2 Very High?
It is an existing design allocation giving a little more representation to middle scales while retaining extremes. It is not proven optimal or proportional to the candidate population.

### 13. What are the exact funding-band thresholds?
Low: up to $1.5M; Medium: over $1.5M through $6.14149M; High: over $6.14149M through $20M; Very High: over $20M through $100M. Positive funding is already required. Intervals include their right endpoint.

### 14. Why is the threshold $6,141,490 so specific?
It is the fixed cutoff in the original notebook. Its statistical derivation cannot be established from available outputs, so I do not claim it is a verified quantile or estimated optimum.

### 15. Does stratification make the sample representative?
It ensures coverage of chosen strata, but equal sector counts and fixed band quotas are not population-proportional. Sampling bias and limited generalizability remain.

### 16. Was anything random?
The original within-stratum sample uses `random_state=42` without replacement. The final sample is frozen; IPS, Funding-History Risk Proxy and strategic scores are deterministic and contain no random startup-specific values.

### 17. What is a funding round?
A recorded financing event. Multiple rounds can indicate repeated financing access, but they are not necessarily evidence of profitability or guaranteed success.

### 18. What does funding duration measure?
The last funding calendar year minus the first, with missing differences filled with zero and negatives clipped. It is not exact elapsed years or company age.

## Proxies and score design

### 19. Why use historical funding as investment cost?
It supplies an available, reproducible size-related proxy when actual investment prices and future capital requirements are unavailable. Its economic interpretation is explicitly limited.

### 20. Is investment_cost a real investment price?
No. It equals historical total funding; it is not a current purchase price, valuation, stake price or quoted capital requirement.

### 21. How is IPS calculated?
`round(.30*N(rounds)+.25*N(duration)+.25*status_score+.20*outcome_score,2)`, where N is sample min-max to 0-100. Status scores are IPO100/acquired90/operating70/closed20/default50; outcome score is `50*(acquisition+ipo)`.

### 22. Why normalize rounds and duration?
They use different original units and ranges. Min-max normalization converts each to 0-100 before combining them with explicit weights.

### 23. What happens if a normalization column is constant?
The preserved IPS normalizer returns 100. The separate risk-proxy implementation rejects constant calibration components. Neither source component is constant in the final sample.

### 24. Why are acquisition and IPO included in IPS?
They are available historical milestones interpreted positively by the original heuristic. They do not guarantee profitable returns; retaining them makes IPS retrospective rather than a prospective predictor free from leakage.

### 25. Does one IPO flag give outcome_score 100?
No. One of the two flags gives 50; both would give 100. The outcome component's weight is then 0.20.

### 26. Were the IPS weights statistically estimated?
No. They are preserved modelling assumptions. No return-prediction training or empirical calibration of these weights is claimed.

### 27. What does a closed company mean?
The source status records it as closed. The model treats it as a historical case with a low status score, not a currently available deal.

### 28. Can a historical closed company be selected?
Yes. There is no hard exclusion by status; selection follows costs, scores and constraints. This is acceptable only as an explicitly retrospective modelling exercise, not as current investment advice.

### 29. Is IPS expected profit, NPV or ROI?
No. It is a heuristic additive score. The dataset does not supply the future cash-flow series required for a defensible NPV calculation.

### 30. How is the Funding-History Risk Proxy calculated?
`round(.50*(100-N(rounds))+.50*(100-N(duration)),6)`. Higher values indicate less observed financing history and greater modelled uncertainty under that assumption.

### 31. Is your Risk Score actual financial risk?
No. It is neither direct financial risk nor probability of failure. It does not measure volatility, expected losses or covariance; it is a limited funding-history proxy.

### 32. Why is risk strongly negatively correlated with IPS?
The measured correlation is **-0.9600**. Both use related rounds and duration variables: IPS rewards more history, while the proxy penalizes less history. That strong redundancy is a limitation.

### 33. Is that a circular definition?
The proxy is calculated from original history variables, not IPS or portfolio selection, so it is not directly circular. However, shared inputs make it strongly dependent on the same underlying information.

### 34. Why not use status to assign risk?
That would introduce retrospective outcome information into the proxy and could confuse observed outcomes with forward-looking risk. The selected proxy uses only funding history, while retaining its own limitations.

### 35. Is Strategic Alignment data-driven?
Only its sector input is dataset-derived. The score mapping is a **Decision-maker supplied strategic preference** for a hypothetical enterprise-software investor.

### 36. What is the exact strategic mapping?
Software/enterprise100; web/mobile75; ecommerce/hardware50; advertising/games_video25; biotech/medical0. Equal-sector firms receive equal scores. It is not an objective ranking of industries.

### 37. Does a zero strategic score mean a bad startup?
No. It means outside the assumed investor mandate. A different investor could prefer that sector, but the submitted mapping is frozen.

## Integer Programming and logical constraints

### 38. What is a binary decision variable?
A variable restricted to 0 or 1. `x_i=1` selects project i and `x_i=0` omits it; partial projects are not allowed.

### 39. Why Integer Programming?
Project inclusion is indivisible, and the objective and constraints are linear sums of fixed coefficients. Binary IP fits those assumptions directly.

### 40. What is the IP objective function?
Maximize `sum(IPS_i*x_i)` over the 100 sample companies.

### 41. What are the baseline hard constraints?
`sum(C_i*x_i)<=B` and binary variables. No sector quota, prerequisite, mutual exclusion, minimum project count or full-spending condition exists in baseline.

### 42. Why not simply select the highest IPS or highest IPS/cost ratios?
Those greedy rules can miss the best discrete combination. Binary IP optimizes the portfolio jointly rather than ranking companies independently.

### 43. Why is some budget left unused?
Projects are indivisible and the constraint is an upper bound. Remaining money may not accommodate an improving project combination; complete spending is not required.

### 44. What is a prerequisite constraint?
`x_A<=x_B`: A can be selected only if B is selected. B can still be selected alone.

### 45. What is mutual exclusion?
`x_A+x_B<=1`: at most one may be selected, so selecting neither is also allowed.

### 46. Are the logical relationships from Crunchbase?
No. They are **Scenario-based modelling assumptions**. P005 requires P004; P003 and P004 are mutually exclusive. They demonstrate how decision-maker-supplied interdependencies can be represented.

### 47. Does the logical scenario change the answer?
At $25M baseline already satisfies the pairs, so the IP portfolio is unchanged. At $50M/$75M baseline selects both P003/P004, and enforcing exclusion changes the portfolio and reduces maximum IPS. P005 is unselected in these IP solutions, so the prerequisite is nonbinding there.

### 48. What are the authoritative baseline IP results?
$25M: 24 projects, IPS 706.67; $50M: 34 projects, IPS 968.34; $75M: 40 projects, IPS 1,184.18. Exact costs, utilization and proxy totals are in the final results summary, sourced from `results/optimization/ip_summary.csv`.

### 49. Why do old CSV files have different IP totals?
They are marked historical/superseded. The earlier audit found a source/result configuration mismatch; their higher-budget values match assumed-logic objective values rather than the active baseline. This submission uses the frozen final outputs, not the old root-level files.

## Goal Programming

### 50. What is Goal Programming?
A method that expresses aspiration levels and minimizes weighted undesirable deviations from them while retaining hard constraints.

### 51. Why use GP after IP?
IP gives a single-objective benchmark. GP demonstrates how preference over potential, total Funding-History Risk Proxy and strategy changes the decision, using the same data and hard budget.

### 52. What is a deviation variable?
A nonnegative amount below or above a target, represented by `achieved+d_minus-d_plus=target`.

### 53. Why penalize only certain deviations?
The goal directions differ. Falling short of potential or alignment is undesirable, so penalize dP-/dS-. Exceeding the risk-proxy target is undesirable, so penalize dR+. Opposite-direction deviations are not penalized.

### 54. What is the exact GP objective?
Minimize `wP*dP_minus/P_scale + wR*dR_plus/R_scale + wS*dS_minus/S_scale`. All penalties have positive signs.

### 55. Why normalize GP deviations?
Portfolio scores have different numerical scales. Dividing by goal references makes deviations dimensionless and allows weights to express preferences over relative gaps rather than raw magnitudes.

### 56. How were GP targets generated?
For each budget/logic configuration, maximize total IPS, minimize total risk proxy and maximize strategy separately under the same constraints. Their individual optima define the three targets; P/S optimal ties are resolved by minimum risk proxy.

### 57. What is a payoff table?
It reports all three achieved measures for each individually optimized portfolio. It reveals conflict between individually best outcomes and provides normalization references.

### 58. Why does minimum risk select zero projects?
Every project has positive proxy exposure and there is no minimum investment/size constraint. Choosing nothing gives the minimum possible sum, zero. It is a valid ideal anchor, not a solver bug.

### 59. How do you avoid division by a zero risk target?
Use the largest risk-proxy total among the payoff anchors minus R_target as R_scale. P_scale and S_scale equal their positive targets. This range is not a hard cap or the global maximum feasible risk.

### 60. Are all three ideal targets jointly attainable?
Not generally. In this sample the zero-risk ideal requires selecting nothing, which cannot achieve positive maximum potential/strategy. GP quantifies the compromise.

### 61. What do GP weights represent?
Decision-maker preference over normalized undesirable deviations. Balanced uses 1/3 each; each focused scenario uses 0.60 on its named goal and 0.20 on each other. They are not sector budgets or universal optimal priorities.

### 62. Is the method lexicographic GP?
No. It is weighted, compensatory GP. A sufficiently large improvement in other weighted deviations can compensate for worsening one goal.

### 63. Why does GP sometimes select fewer projects?
Adding projects can improve potential and strategy but increases total proxy exposure. The weighted compromise can prefer a smaller portfolio.

### 64. Why can risk-focused GP select very few projects?
It heavily penalizes additive exposure relative to the zero-risk ideal. Baseline risk-focused portfolios select 7/10/12 projects at $25M/$50M/$75M. It is not evidence that all omitted startups would fail.

### 65. Is the risk measure an average?
No, it is `sum(R_i*x_i)`. It depends on portfolio size and uses no decision-variable denominator. Calling it an average or diversified risk would be incorrect.

### 66. What are the main balanced GP results?
$25M: 18 projects, IPS 570.01; $50M: 25 projects, IPS 819.18; $75M: 30 projects, IPS 1,025.02. The corresponding portfolio risk-proxy and strategic totals are in the generated final results summary.

### 67. Why is GP not automatically better than IP?
They optimize different criteria. IP maximizes IPS, whereas GP seeks a preference-dependent compromise. A lower GP IPS can be intentional; superiority cannot be claimed without specifying the decision-maker's objectives.

### 68. What does normalized goal achievement mean?
`1-undesirable_deviation/scale`. One means that goal is met; it is not a probability. For risk it uses the payoff range, not division by zero, and it can be negative beyond that range.

## Sensitivity, validation and limitations

### 69. What happens when budget increases?
The feasible set expands, so optimal baseline IP IPS cannot decrease. Observed portfolios grow here, but nested selections and higher counts are not general mathematical guarantees. GP targets also change with budget.

### 70. What happens when priorities change?
Targets stay fixed within a budget/logic case while weighted penalties change. Portfolios may shift in size and sector composition. Potential-, risk- and strategy-focused choices illustrate different preferences.

### 71. Why compare logical GP with fixed targets too?
Adding constraints normally recalibrates individual optima and normalization. Holding baseline references fixed isolates the effect of restricting feasibility from the effect of recalibration.

### 72. Why was multi-period budgeting removed?
Historical funding does not provide defensible future annual project expenditure. Year-1/2/3 constraints would require unsupported costs, so the final model uses single-period budget scenarios.

### 73. How was optimization validated?
Recompute selections, costs, scores, constraints, GP equations and deviations; require optimal solver status; independently cross-check objectives with HiGHS. The rerun passed 1586/1586 checks across 60 portfolios, plus six existing tests.

### 74. What is the difference between feasibility and optimality?
Feasibility means satisfying constraints. Optimality means no feasible solution improves the specified objective. A feasible solver incumbent alone is not accepted as a proven optimum here.

### 75. Why might two solvers choose different projects?
Multiple portfolios can have the same optimal objective. Validation compares objective values and feasibility; identical membership is not required for tied optima.

### 76. What are the main assumptions?
Funding-as-cost, indivisible projects, additive heuristic scores, sample/filter choices, IPS/risk rubrics, strategic sector preferences, scenario logical pairs, ideal-target normalization and GP priority weights.

### 77. What are the main limitations?
Old and partly missing raw data; a nonrepresentative fixed sample; no actual investment prices or future cash flows; retrospective IPS; strongly related history-based risk proxy; assumed strategy/logic; and no covariance or multi-period expenditures.

### 78. Does passing tests prove the model is economically true?
No. It supports implementation correctness and consistency under the assumptions. It does not validate the proxies as accurate real-world forecasts.

### 79. How can someone reproduce the submission without changing results?
Run the existing artifact validator and tests, then `python src/build_submission_docs.py --check` and `python src/check_submission.py`. Full re-solving is a separate existing pipeline; finalization reads the frozen result files.

### 80. What should you say if asked for the single most important conclusion?
Explicit objectives and preferences change which projects are selected under the same capital limit. The project demonstrates transparent, validated OR trade-offs, while keeping historical observations separate from proxies and assumptions.
