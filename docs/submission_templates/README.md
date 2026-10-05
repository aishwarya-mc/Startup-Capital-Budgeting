# Startup Capital Budgeting: Portfolio Optimization

Final non-UI academic submission: **Integer Programming and linear weighted Goal Programming** on the same frozen 100 historical startup projects. The mathematical implementation, scores, configuration and numerical results are unchanged during submission finalization.

## Read and present the project

| Material | Purpose |
|---|---|
| [Final model audit](docs/final_model_audit.md) | Freeze, provenance, classification of data/calculations/assumptions and scope |
| [Methodology](docs/methodology.md) | Nineteen sections covering the exact implemented mathematics |
| [Final results summary](docs/final_results_summary.md) | Authoritative comparison, all GP priorities, sensitivity and limitations |
| [Beginner explanation](docs/project_explanation_beginner.md) | Study the complete project from zero, with numerical examples |
| [Viva preparation](docs/viva_preparation.md) | 80 questions and technically consistent answers |
| [Presentation content](docs/final_presentation_content.md) | Sixteen slide outlines with 30-60 second speaking notes; no PowerPoint file |
| [Figure guide](docs/final_figures_review.md) | Seven publication figures, source tables, captions and interpretation |
| [Final consistency report](results/submission/consistency_report.md) | Tests, validation, hashes and created/modified files |

## Authoritative baseline results

The main presentation compares baseline IP with baseline balanced GP. Full costs, risk-proxy/strategy totals and relevant deviations appear in the [single main comparison table](docs/final_results_summary.md#3-authoritative-ip-vs-gp-comparison).

{{SLIDE_IP_TABLE}}

Baseline balanced GP:

{{SLIDE_GP_TABLE}}

All statuses are Optimal. Balanced GP sacrifices potential and selects fewer projects while reducing total Funding-History Risk Proxy and improving strategic alignment under the assumed preferences. This does not make GP inherently better than IP.

## Frozen model

- IP: `max sum(IPS_i*x_i)`, subject to `sum(C_i*x_i)<=B` and binary x.
- IPS: `round(.30*N(rounds)+.25*N(duration)+.25*status_score+.20*outcome_score,2)`. N uses the full-sample min-max range; the original normalizer maps a constant column to 100. Status: IPO100/acquired90/operating70/closed20/default50. Outcome: `50*(acquisition+ipo)`.
- **Funding-History Risk Proxy**: `round(.50*(100-N(rounds))+.50*(100-N(duration)),6)`. Not failure probability or direct financial risk. Its IPS correlation is **{{CORRELATION}}** because history inputs overlap.
- **Decision-maker supplied strategic preference**: software/enterprise100, web/mobile75, ecommerce/hardware50, advertising/games_video25, biotech/medical0. The hypothetical investor focuses on enterprise software; this is not an objective industry ranking.
- GP: minimize `wP*dP_minus/P_scale + wR*dR_plus/R_scale + wS*dS_minus/S_scale`, with three linear goal equations and the same hard constraints.
- Targets come from individual-objective optima. The risk-only ideal is zero at the empty portfolio; R_scale is the payoff-anchor risk range, avoiding division by zero. Balanced weights are 1/3 each; focused weights are .60/.20/.20.
- Baseline excludes logical pairs. The separate `assumed_logic` case imposes P005 requires P004 and P003/P004 exclusion as **Scenario-based modelling assumptions** supplied by a hypothetical decision-maker.

Exact definitions: [methodology](docs/methodology.md), [configuration](config/model_config.json), [data dictionary](docs/data_dictionary.csv), [GP detail](docs/goal_programming.md), [risk detail](docs/risk_methodology.md), [strategy detail](docs/strategic_methodology.md).

## Verify the submission without changing model results

From this README's directory, use the tested Python environment (Python 3.9; dependencies pinned in `requirements.txt`):

```powershell
python -m pip install -r requirements.txt
python src/validate_results.py
python -m unittest discover -s tests -v
python src/build_submission_docs.py --check
python src/check_submission.py
```

In this supplied workspace, PuLP is installed locally in the parent `.python_packages`. From this directory, set `$env:PYTHONPATH = (Resolve-Path ../.python_packages).Path` if using that installation. No package update is required in the existing tested environment.

`build_submission_docs.py` reads frozen result files and narrative templates under `docs/submission_templates/`; it never optimizes or rescales scores. Without `--check`, it renders the academic documents. Edit those templates rather than generated documents. `check_submission.py` checks freeze hashes, rendered text, table consistency, links, figure inputs and document coverage, then records the file inventory.

Existing full analysis reproduction remains `python src/run_analysis.py`. It re-solves and rewrites generated analysis artifacts; it is separate from the read-only model checks used to preserve this submission. No rescoring or re-solving is needed to study the final outputs.

## Result locations and validation

Authoritative numerical files are under [results/optimization/](results/optimization/):

- [IP summary](results/optimization/ip_summary.csv), [GP summary](results/optimization/gp_summary.csv), [payoff table](results/optimization/payoff_summary.csv), [targets](results/optimization/goal_targets.csv).
- [Canonical comparison](results/optimization/ip_vs_gp_comparison.csv), [sensitivity changes](results/optimization/sensitivity_changes.csv), [sector composition](results/optimization/sector_composition.csv).
- Each portfolio prefix includes selected rows and all 100 decisions per run; `gp_fixed_targets_*` isolates logical-constraint effects.
- [Validation](results/optimization/validation_report.md): **{{VALIDATION_PASSED}}/{{VALIDATION_COUNT}} checks across {{PORTFOLIOS}} portfolios**, independent HiGHS objective cross-checks, plus six existing tests.
- [Seven PNG/vector-PDF figures](results/optimization/charts/), with no new decorative plots.

The final dataset has 100 rows and 25 columns: [startup_projects_scored.csv](data/processed/startup_projects_scored.csv). Raw data, original notebooks, base data and existing validated numerical results are preserved.

## Historical artifacts and limitations

Root-level `results/integer_programming_*.csv` files and `docs/archive/` are historical/superseded for final baseline reporting. The [earlier audit](docs/audit.md) records why their higher-budget totals differ. They are not a competing authority. Per-budget comparison CSVs are views of the canonical current comparison.

Only `funds.csv` and `ipos.csv` remain in `data/raw/`; the main source tables needed to rebuild the sample are missing. **462,651 raw entities and 11,259 candidates are previously reported counts, not locally reverified.** The final sample and optimization outputs are verifiable.

Historical funding is an Investment Cost Proxy, not a current price. The dataset ends around 2013, the sample is deliberately stratified, and closed/exited companies are historical modelling cases. IPS is retrospective; exits do not guarantee returns. Funding-History Risk Proxy is strongly related to IPS and lacks financial-risk calibration or covariance. Strategic alignment, logical relationships and GP priorities remain explicit preference scenarios.

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

UI and Nonlinear Programming are intentionally outside this submission. No missing costs, relationships or company-specific scores were invented.
