# Sequential implementation record

> Historical implementation phase record. Intermediate check counts record earlier stages; final submission status is in [final model audit](final_model_audit.md).

The audit was reported before changing files. Each phase was reported to the
user before proceeding. Original artifacts are recorded in the archive manifest.

| Phase | Files created/modified | Formulas/assumptions | Results and validation |
|---|---|---|---|
| 0 Audit | docs/audit.md; docs/archive/* | Recorded exact original IPS, budget-only IP, inactive logical examples | 100 unique projects; 23 original scored columns; IPS and saved totals reproduced. Found missing raw tables. |
| 1 IP | src/integer_programming.py; src/portfolio_model.py; config/model_config.json; results/optimization/ip_* | Original IPS unchanged; max sum(P*x), budget and binary; optional original logical examples labelled assumptions | Fresh baseline IPS 706.67/968.34/1184.18. Saved $50M/$75M results were inconsistent with active source. Six optimal runs; initial 66 checks passed (later expanded). |
| 2 Periods | docs/multi_period_feasibility.md | Single aggregate budget; no future allocations assumed | Inspected available schemas: no defensible future project-period costs. Multi-period budgeting omitted. |
| 3 Risk | src/score_projects.py; docs/risk_methodology.md; scored CSV; score reports | .5 inverse normalized rounds + .5 inverse normalized duration; equal weights and risk interpretation are assumptions | Range 12.5–100, mean 74.1667; range, finiteness, identical-input, monotonicity and original-column preservation checks passed. |
| 4 Strategy | config/model_config.json; docs/strategic_methodology.md; scored CSV; score reports | Hypothetical enterprise-software mandate, tiered sector lookup 0/25/50/75/100 | Range 0–100, mean 50; same-sector rule and complete mapping. Final scored dataset: 100 rows, 25 columns. |
| 5 GP | src/goal_programming.py; docs/goal_programming.md; config/model_config.json | Linear goal equations; positive penalties for P/S shortfall and R excess; payoff ideal targets; zero-risk ideal normalized by payoff range | $25M smoke test: 18 projects, P570.01/R1337.50/S1225; goal equations and objective validated. |
| 6 Scenarios | results/optimization/gp_*, payoff_*, goal_targets.csv, config snapshot; refreshed ip_* | Four explicit weight scenarios, two logical configurations, three budgets | 24 GP runs plus 18 payoff anchors optimal. Initial 672 GP/payoff checks passed, expanded later. Risk-focused portfolios 7/10/12 projects at baseline. |
| 7 Comparison | src/compare_models.py; comparison report and tables | Same sample/budget/hard constraints; IP evaluated against GP references after solving | Balanced GP loses P136.66/149.16/159.16, lowers R541.67/941.67/1054.17, gains S100 at each budget; no claim GP is better. |
| 8 Sensitivity | src/sensitivity_analysis.py; sensitivity reports/CSVs; sector_composition.csv; gp_fixed_targets_* | Budget and priority changes; logical constraints with recalibrated and fixed baseline targets | 75 comparisons, 420 sector rows; 12 additional fixed-target GP solutions validated. Added/removed IDs, overlap and sector cost/count changes saved. |
| 9 Charts | src/plot_optimization.py; results/optimization/charts/* | Same scenario definitions; separate units/axes; risk range denominator labelled | Seven PNG/PDF figures; comparison/sector/deviation/composition charts visually inspected; EDA charts unchanged. |
| 10 Validation | src/validate_results.py; tests/test_models.py; validation/solver reports; run_metadata.json | Explicit tolerances; reject nonoptimal incumbents; independent SciPy/HiGHS formulations | 1586/1586 artifact checks, all 60 objective cross-checks, six tests passed. Original raw/base/notebook/result file hashes unchanged. |
| 11 Documentation/reproduction | README.md; docs/methodology.md; docs/data_dictionary.csv; docs/team_split.md scope note; results/README.md; requirements.txt; src/run_analysis.py | Dataset-derived vs derived vs decision-maker inputs separated; limitations and zero-risk normalization explicit | Complete delivery index, pinned tested dependencies and one-command sequential reproduction. Full command records execution and test reports. |

## Important methodological limitations

The risk index's correlation with IPS is -0.9600 because history inputs overlap;
it is not independent risk measurement. IPS retains retrospective outcome
information and is not a prospective return prediction. Strategic tiers and
logical pairs are scenario inputs. Ideal targets and weights are modelling
choices. No future spending data, dependencies or startup-specific risk values
were fabricated. No UI or NLP work was performed.
