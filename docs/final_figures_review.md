# Final Optimization Figures: Review and Captions

All seven optimization figures are retained because each answers a distinct question. Presentation-only refinements standardize the term **Funding-History Risk Proxy**, identify units, improve headings and export at 300 dpi plus vector PDF. Figure 7 now includes the requested IP logical comparison alongside the existing fixed-target GP comparison. No input values, model results or selections are altered.

| Figure | Analytical purpose / suggested caption | Frozen source and filters |
|---|---|---|
| 01_budget_potential | **Budget vs total investment potential.** Baseline IP and four GP priorities at the three budgets; all points are total IPS, not financial return. | ip_vs_gp_comparison.csv; baseline; total_potential |
| 02_budget_project_count | **Budget vs number of selected projects.** Shows portfolio-size responses separately from score changes. Counts refer to selected portfolios, not the 100-project candidate sample. | Same comparison; baseline; projects_selected |
| 03_ip_vs_gp_performance | **IP and balanced GP on the same sample.** Separate panels for potential, total Funding-History Risk Proxy and strategic points prevent conflating scales. Proxy is not financial risk; strategic points express supplied preferences. | Same comparison; baseline; single_objective/balanced |
| 04_selected_sectors | **Selected projects by sector.** IP versus balanced GP at each budget; sector counts need not equal the sample's ten companies per sector. | sector_composition.csv; baseline; recalibrated; IP and balanced GP |
| 05_gp_goal_deviations | **Normalized undesirable GP deviations.** Four priorities per budget. Potential/strategy use target denominators; risk proxy uses the payoff range because its target is zero. Dimensionless; lower is preferred. | ip_vs_gp_comparison.csv; baseline GP; normalized_deviation_* |
| 06_gp_priority_composition | **Portfolio sector composition under GP preferences.** Stacked counts reveal which sectors change when priorities change, not an objective industry ranking. | sector_composition.csv; baseline GP; recalibrated; projects_selected |
| 07_logical_constraint_sensitivity | **Assumed-logic minus baseline.** Upper row: IP. Lower row: balanced GP with baseline targets/scales fixed. Values are changes in score-points. Negative IPS means a potential sacrifice; proxy direction needs separate interpretation. | sensitivity_changes.csv; logic_recalibrated/IP/single_objective and logic_fixed_targets/GP/balanced |

PNG and PDF files are in [results/optimization/charts/](../results/optimization/charts/). Source and output hashes are in [chart_manifest.json](../results/optimization/charts/chart_manifest.json). Plot code is [plot_optimization.py](../src/plot_optimization.py). Titles identify the scenario; legends distinguish compared models/priorities. Each plot labels its axes and units. The PDF exports retain vector text and shapes for print.

## Presentation choices

Use figure 03 on the main comparison slide and figure 06 on the sensitivity slide. Use the IP and GP numerical tables on their result slides. Figures 01/02/04/05/07 support questions or a longer presentation; showing every figure on the same slide would be redundant and unreadable. Full size figures in the report remain analytically distinct.

## Historical exploratory charts

The five original exploratory figures and their notebooks are preserved unchanged. They describe the modelling sample, not optimized selections. In particular, the original `projects_by_sector.png` title says "Selected Investment Projects" but its bars are the ten sampled candidates per sector; do not describe it as an IP/GP portfolio. The original cost histogram uses linear bins displayed on a log x-axis; use its counts cautiously and prefer the verified descriptive statistics table for the short presentation. Neither historical chart is promoted as a new optimization result.

No decorative plots or duplicate new chart families were added. The final consistency check verifies plotted source values, source hashes, file existence, PNG integrity and seven PNG/PDF pairs. Visual review checks title/legend readability and layout in addition to numerical provenance.
