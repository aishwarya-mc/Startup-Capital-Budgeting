# Final Presentation Content

Sixteen slides; no PowerPoint file is created. Each slide has 3-6 main points, one recommended visual and approximately 30-60 seconds of spoken explanation. Use [final_results_summary.md](final_results_summary.md) for backup tables and [viva_preparation.md](viva_preparation.md) for questions. Values are rendered from frozen final outputs. Risk always means **Funding-History Risk Proxy**; costs always mean the historical funding-based **Investment Cost Proxy**.

## Slide 1. Startup Capital Budgeting: Portfolio Optimization

- An Operations Research study of limited-capital project selection.
- One fixed, stratified dataset of 100 historical startups.
- Integer Programming and weighted Goal Programming.
- Transparent assumptions and independently checked results.

**Recommended visual:** Title with a small project-selection diagram; no decorative chart.

**30-60 second explanation:**
This project studies how to choose a portfolio when there is not enough capital to select every project. I use 100 historical startup records as modelling projects. Integer Programming gives a single-objective benchmark, while Goal Programming introduces explicit preferences for potential, funding-history uncertainty and strategic fit. The purpose is to demonstrate a transparent Operations Research decision process, not to recommend investments in those companies today. I will distinguish observed data from calculated proxies and investor assumptions throughout the presentation.

## Slide 2. Problem Statement and Significance

- Capital is limited; startup projects compete for the same budget.
- Individually attractive projects may not form the best affordable combination.
- Potential, total proxy exposure and strategic fit can conflict.
- The decision must satisfy hard resource constraints.

**Recommended visual:** Small hypothetical three-project example from the beginner guide.

**30-60 second explanation:**
A ranking of individual startups does not necessarily identify the best portfolio. Selecting a high-scoring expensive project might prevent choosing several affordable projects with greater combined value. The problem therefore concerns combinations, not just rankings. We also distinguish the hard resource limit from preferences about what the portfolio should achieve. This matters because a decision-maker may accept some reduction in one score to improve another. The project makes those trade-offs explicit rather than hiding them inside an informal recommendation.

## Slide 3. Objectives and Research Questions

- Find maximum total IPS under each capital budget.
- Compare a multi-goal compromise with the IP benchmark.
- Assess sensitivity to budgets and decision-maker priorities.
- Demonstrate separately supplied logical interdependencies.
- Validate feasibility, objective values and reporting consistency.

**Recommended visual:** A compact objective-to-analysis table; no additional plot.

**30-60 second explanation:**
The first question is what the unchanged Investment Potential Score can achieve at each budget. The second is how the portfolio changes when other goals receive explicit weight. I then vary budgets, priority weights and a separately labelled logical scenario, tracking both aggregate measures and actual selected projects. Finally, I verify the model numerically and check that the documents report the same results as the output files. These objectives define the project's scope without adding unsupported future cash flows or new techniques.

## Slide 4. Raw Dataset and Provenance

- Historical Crunchbase entities, funding and company events.
- 462,651 entities: previously reported, not locally reverified.
- Company records are separated from other entity types.
- Only funds and IPO raw tables are present in this checkout.
- Missing main source tables limit raw reconstruction.

**Recommended visual:** Three-column source/provides/availability table from the audit.

**30-60 second explanation:**
The raw collection describes more than startups: its entities can include people and other organizations. The notebook filters company records and combines historical funding and event information. The project brief reports 462,651 raw entities, but I cannot independently verify that count from this checkout because the main objects table and saved counting outputs are missing. I therefore label it as previously reported. The final 100-project dataset is present and verifiable, and the optimization pipeline from that dataset is reproducible. This distinction is part of the project's provenance audit.

## Slide 5. Dataset Preparation Pipeline

- Company type, positive funding and positive funding rounds.
- First funding year between 2010 and 2013 inclusive.
- Ten sectors; total funding capped at $100M.
- 11,259 candidates: previously reported, not locally reverified.
- Stratify by sector and funding band; sample with seed 42.

**Recommended visual:** Filtering flow in the beginner guide, marking reported counts with an asterisk.

**30-60 second explanation:**
The year condition is based on first funding, not company founding. After company and funding filters, the notebook restricts the universe to ten sectors and a historical funding cap of one hundred million dollars. The reported candidate count is 11,259, but that count shares the raw-data verification limitation. The next stage divides candidates into sector and funding-band groups and samples within them. I preserve this preprocessing design and the final sample rather than redesigning the dataset to improve optimization results.

## Slide 6. Final 100-Project Dataset

- Ten sectors, ten companies in each.
- Per sector: 2 Low, 3 Medium, 3 High, 2 Very High.
- One hundred distinct projects; final scored dataset has 25 columns.
- Sample size chosen for an inspectable academic demonstration.
- Coverage of strata does not imply population representativeness.

**Recommended visual:** Sector-by-band table in the methodology; distinguish candidate sample from selected portfolio.

**30-60 second explanation:**
One hundred is a deliberate study size, not a solver limit. The allocation ensures that every chosen sector contains projects at several funding scales, with slightly more examples in the middle bands. This makes comparisons easier to inspect and explain. However, equal sector counts do not reproduce the real distribution of startups, so conclusions apply to this modelling sample. Also, these one hundred records are the candidates presented to the optimizer. A final portfolio contains only the projects selected from those candidates.

## Slide 7. Statistical Analysis

- Investment proxies vary widely across the sample.
- Compare distributions, sector totals and funding-round patterns.
- Distinguish recorded exits from guaranteed investment success.
- Funding-history measures underpin two related model scores.

**Recommended visual:** A small descriptive table from the verified statistics below; use the preserved funding-round scatter only if time allows.

{{SLIDE_STATS}}

**30-60 second explanation:**
The descriptive analysis helps explain the coefficients the optimizer receives. Historical funding ranges from very small amounts to the cap, so project costs are heterogeneous. Funding rounds and duration describe observed financing history, not future cash flows. Acquisition and IPO counts describe recorded events rather than proof of profitable returns. For the slide, I would display only the cost minimum, median and maximum plus the outcome counts, leaving the complete table as backup. The original exploratory plots are retained, but the submission focuses on visuals that directly support the optimization argument.

## Slide 8. Feature Engineering and Three Scores

- Cost proxy equals historical total funding.
- IPS: 30% rounds, 25% duration, 25% status, 20% outcomes.
- Funding-History Risk Proxy: equal-weight inverse normalized rounds/history.
- Strategy: Decision-maker supplied strategic preference by sector.
- Risk proxy and IPS correlation: **{{CORRELATION}}**, a shared-input limitation.

**Recommended visual:** Three-row score definition/source/limitation table; exact formula backup in methodology.

**30-60 second explanation:**
Each score has a different interpretation. IPS is the preserved historical heuristic; its weighted components include status and recorded outcomes, so it is not a future-return prediction. The Funding-History Risk Proxy reverses normalized rounds and duration, interpreting less history as greater uncertainty. It is not a failure probability or direct financial risk, and its strong inverse relation with IPS reflects shared inputs. Strategic alignment comes from a hypothetical enterprise-software investor's sector preferences, not an objective industry ranking. Historical funding is used only as a reproducible cost proxy.

## Slide 9. Integer Programming Formulation

- `x_i=1` selects startup i; `x_i=0` omits it.
- Maximize `sum(IPS_i*x_i)`.
- Hard budget: `sum(C_i*x_i)<=B`.
- All selections are binary; projects are indivisible.
- Baseline has no logical pairs or sector quotas.

**Recommended visual:** The three-line baseline IP formulation, with variable definitions.

**30-60 second explanation:**
The IP model chooses the combination with the highest total Investment Potential Score while respecting the available capital. Binary variables mean the model either includes a whole project or leaves it out. The budget is an upper bound, so the solution is allowed to leave money unused. The baseline contains only this budget and the binary restrictions. Logical relationships are introduced in a separate scenario, which prevents an assumed business dependency from being confused with a source-data fact or silently changing the baseline comparison.

## Slide 10. Authoritative IP Results

- All three baseline solver statuses are Optimal.
- Maximum total IPS increases with budget.
- Project counts and cost utilization are recomputed from decisions.
- Final outputs supersede root-level historical result tables.

**Recommended visual:** Use this generated table; chart 01 is optional if a table is too dense.

{{SLIDE_IP_TABLE}}

**30-60 second explanation:**
These are the authoritative baseline values read from the final result file. The larger budget expands the feasible set and allows a higher maximum total IPS. The model does not force full utilization, and the exact cost depends on indivisible selected projects. These optima are conditional on the fixed sample and proxy scores; they do not represent verified financial returns. Historical result files are preserved for audit but are marked superseded, so the presentation uses only the current validated baseline numbers shown in this table.

## Slide 11. Goal Programming Formulation and Targets

- Three linear goal equations: `achieved+d_minus-d_plus=target`.
- Penalize potential shortfall, risk-proxy excess and strategy shortfall.
- Minimize their positively weighted normalized sum.
- Individual-objective optima generate the aspiration targets.
- Risk-only ideal is zero projects; use payoff risk range for normalization.

**Recommended visual:** Three goal equations plus a compact deviation-direction table.

**30-60 second explanation:**
Goal Programming retains the hard budget and adds aspiration equations. A shortfall below potential or strategy is undesirable, while excess above the risk-proxy target is undesirable. We normalize their penalties because the portfolio totals have different scales. Targets come from maximizing potential, minimizing total proxy exposure and maximizing strategy separately. The risk-only minimum is the empty portfolio because all project proxy scores are positive. We disclose that result rather than invent a minimum-investment rule, and normalize risk excess by a positive payoff-table range instead of dividing by zero.

## Slide 12. Goal Programming Results and Priorities

- Balanced uses equal weights on normalized undesirable deviations.
- Focused scenarios use 0.60 on one goal and 0.20 on each other.
- All main GP scenarios have Optimal status.
- Risk-focused selection counts are **{{RISK_COUNTS}}** as budgets rise.
- The table shows baseline balanced GP, not every preference scenario.

**Recommended visual:** This compact balanced table; keep all 24 scenarios as report backup.

{{SLIDE_GP_TABLE}}

**30-60 second explanation:**
Balanced means equal weight on relative undesirable deviations, not equal expenditure or equal sector representation. The table shows that compromise at each budget. Other preference scenarios emphasize one of the three goals and can select different portfolios. In particular, risk-focused GP selects relatively few projects because each additional project increases the additive proxy total. These are explicit hypothetical preferences, not universal investor priorities. All the scenarios retain the same project universe and hard budget, and their detailed deviations are available in the final report.

## Slide 13. IP vs GP: Observed Trade-offs

- IP maximizes a single primary objective under hard constraints.
- Balanced GP sacrifices IPS and selects fewer projects.
- Total Funding-History Risk Proxy decreases; strategy improves.
- Some proxy reduction reflects portfolio size.
- Neither model is inherently superior.

**Recommended visual:** `03_ip_vs_gp_performance.png` or its vector PDF; table with deviations in final results is backup.

**30-60 second explanation:**
The comparison uses the same sample, budget and baseline constraints, so differences arise from the objective. IP must produce the maximum IPS, while GP accepts lower potential to address its other goals. The plotted balanced solutions have lower total Funding-History Risk Proxy and higher strategic alignment. However, selecting fewer projects itself reduces an additive proxy total. I therefore do not interpret the chart as proof that GP finds financially safer investments. The result demonstrates a preference-dependent compromise, and the appropriate model depends on the decision-maker's question.

## Slide 14. Sensitivity Analysis

- Budgets: $25M, $50M, $75M on the same candidates.
- Priorities change both portfolio size and sector composition.
- Scenario assumptions: P005 requires P004; P003 excludes P004.
- IP is unchanged at $25M; exclusion changes higher-budget portfolios.
- Additional GP fixed-target runs separate feasibility from recalibration.

**Recommended visual:** `06_gp_priority_composition.png`; use logical-scenario table as backup, not a second crowded chart.

**30-60 second explanation:**
Sensitivity analysis checks whether the decision is stable under different resources and preferences. Priority changes can shift both how many projects are selected and which sectors appear. The logical case is explicitly hypothetical: it demonstrates decision-maker-supplied interdependencies, not relationships discovered in Crunchbase. At the two larger budgets the baseline IP includes both mutually exclusive projects, so the assumed constraint changes the solution. GP also has fixed-target comparisons to isolate the effect of adding constraints from changes in the payoff targets and scales.

## Slide 15. Assumptions and Limitations

- Historical funding is not a current investment price.
- IPS is retrospective; exits do not guarantee returns.
- Funding-History Risk Proxy is not direct financial risk.
- Sector strategy, logical pairs and priorities are supplied assumptions.
- Missing raw tables and stratification limit provenance/generalization.
- Multi-period budgets omitted: no defensible future annual costs.

**Recommended visual:** Dataset-derived / calculated / assumed classification table; no decorative graphic.

**30-60 second explanation:**
The key limitation is interpretation. Optimization can be mathematically correct while its coefficients remain imperfect proxies. Historical funding is not a current price, IPS includes past outcomes, and the risk proxy shares much of its information with IPS. Strategy and logical dependencies come from scenarios, not the source. The fixed sample also limits generalization, and missing raw tables prevent full raw reconstruction here. Finally, future annual spending is not observed, so multi-period budgeting was intentionally omitted rather than implemented using unsupported Year-1, Year-2 and Year-3 assumptions.

## Slide 16. Key Findings and Conclusion

- Objectives and preferences materially change capital allocation.
- IP provides the maximum-IPS benchmark; GP exposes goal trade-offs.
- All {{PORTFOLIOS}} exported portfolio objectives independently cross-checked.
- {{VALIDATION_PASSED}}/{{VALIDATION_COUNT}} validation checks and six tests passed.
- Frozen results, score definitions and reporting use one source of truth.

**Recommended visual:** A short findings/validation table; no additional plot.

**30-60 second explanation:**
The project demonstrates how an explicit mathematical model turns a limited-capital selection problem into a transparent decision process. IP supplies the single-objective benchmark, and GP shows what changes when additional aspirations receive weight. Sensitivity analysis makes those preferences and assumptions visible rather than hiding them. The implementation and exported results have been checked independently, while the academic materials are generated from the same frozen files. My conclusion is about the value of explicit, validated Operations Research modelling, with clear limits on what historical proxies can establish.
