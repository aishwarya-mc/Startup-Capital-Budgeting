# Final submission consistency report

**806/806 submission checks passed.**
Existing model validation: **1586/1586 passed**; six existing tests passed on rerun.
All 60 exported portfolios retain Optimal problem/solution statuses. No mathematical model, score, data, configuration, target, weight or numerical portfolio result was changed.

50 frozen artifacts retain their original SHA256 hashes. Generated academic tables match the frozen output files.
Checks reconcile all comparison totals/deviations, per-budget views, 420 sector data rows, chart source/output hashes, image resolution, links, 80 viva questions, 16 slide outlines and 19 methodology sections.

Tests and validation logs: [tests.txt](tests.txt), [validation.txt](validation.txt). Detailed submission checks: [consistency_checks.csv](consistency_checks.csv).

## Authoritative results

See [final results summary](../../docs/final_results_summary.md) for baseline IP, all GP scenarios, deviations and sensitivity. The source authority remains results/optimization/*.csv.

## Files created

- `docs/archive/README.md`
- `docs/final_figures_review.md`
- `docs/final_model_audit.md`
- `docs/final_presentation_content.md`
- `docs/final_results_summary.md`
- `docs/project_explanation_beginner.md`
- `docs/submission_freeze.json`
- `docs/submission_templates/README.md`
- `docs/submission_templates/final_model_audit.md`
- `docs/submission_templates/final_presentation_content.md`
- `docs/submission_templates/final_results_summary.md`
- `docs/submission_templates/methodology.md`
- `docs/submission_templates/project_explanation_beginner.md`
- `docs/submission_templates/viva_preparation.md`
- `docs/viva_preparation.md`
- `results/optimization/README.md`
- `results/optimization/charts/chart_manifest.json`
- `results/submission/consistency_checks.csv`
- `results/submission/consistency_report.md`
- `results/submission/file_changes.json`
- `results/submission/tests.txt`
- `results/submission/validation.txt`
- `src/build_submission_docs.py`
- `src/check_submission.py`

## Files modified

- `README.md`
- `docs/audit.md`
- `docs/goal_programming.md`
- `docs/methodology.md`
- `docs/multi_period_feasibility.md`
- `docs/phase_log.md`
- `docs/risk_methodology.md`
- `docs/strategic_methodology.md`
- `results/optimization/charts/01_budget_potential.pdf`
- `results/optimization/charts/01_budget_potential.png`
- `results/optimization/charts/02_budget_project_count.pdf`
- `results/optimization/charts/02_budget_project_count.png`
- `results/optimization/charts/03_ip_vs_gp_performance.pdf`
- `results/optimization/charts/03_ip_vs_gp_performance.png`
- `results/optimization/charts/04_selected_sectors.pdf`
- `results/optimization/charts/04_selected_sectors.png`
- `results/optimization/charts/05_gp_goal_deviations.pdf`
- `results/optimization/charts/05_gp_goal_deviations.png`
- `results/optimization/charts/06_gp_priority_composition.pdf`
- `results/optimization/charts/06_gp_priority_composition.png`
- `results/optimization/charts/07_logical_constraint_sensitivity.pdf`
- `results/optimization/charts/07_logical_constraint_sensitivity.png`
- `results/optimization/charts/README.md`
- `src/plot_optimization.py`

## Files removed

None. Historical data, notebooks and results are retained.

## Unresolved limitations

Missing original raw tables prevent raw reconstruction and independent verification of the previously reported 462,651 entities and 11,259 candidates. Historical funding is not a current price. The Funding-History Risk Proxy is not financial risk or failure probability and shares inputs with IPS. Strategy, logic and priorities remain scenario assumptions. Multi-period expenditures are unavailable; UI and NLP are out of scope.

## Final project status

| Component | Status |
|---|---|
| Repository audit and model freeze | DONE |
| IP formulation/results presentation | DONE |
| Logical-constraint scenario explanation | DONE |
| Three score definitions and limitations | DONE |
| GP formulation, deviations and normalization | DONE |
| Payoff targets and priority scenarios | DONE |
| Authoritative IP vs GP comparison | DONE |
| Budget/priority/logical sensitivity | DONE |
| Multi-period omission explanation | DONE |
| Seven publication figures | DONE |
| Final results summary | DONE |
| Nineteen-section methodology | DONE |
| Beginner study guide | DONE |
| 80-question viva guide | DONE |
| Sixteen-slide content and speaking notes | DONE |
| Cleanup, historical labelling and final consistency | DONE |
| Existing tests and validation rerun | DONE |
| Raw reconstruction/upstream count re-verification | NOT DONE: source files absent; explicitly disclosed |
| UI, NLP, multi-period implementation | NOT DONE: intentionally excluded |
| PowerPoint file | NOT DONE: slide content only, as requested |
