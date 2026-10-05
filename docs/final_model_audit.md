# Final Model Freeze and Audit

## Scope and source of truth

Audited the current datasets, all notebook cells, source scripts, configuration, exported result schemas/values, tests, documentation and all twelve existing PNG charts (five exploratory, seven optimization). The mathematical implementation was inspected before editing submission material. **No new mathematical or implementation error was found. No model, score, target, weight, dataset or validated portfolio result is changed by academic finalization.**

The freeze manifest [submission_freeze.json](submission_freeze.json) stores hashes of the protected implementation, configuration, datasets, notebooks, tests, original archive and numerical result files. Presentation labels and reports may be refined; original data/notebooks and historical results remain available. The scored dataset SHA256 is `a32762d4be16af4280bf15cbbc4ec51694d0ce22225b79e7be21b01078297b15`.

The final numerical authority is `results/optimization/`: `ip_summary.csv`, `gp_summary.csv`, `goal_targets.csv`, `payoff_summary.csv` and `ip_vs_gp_comparison.csv`, with their selected/decision files. Per-budget comparisons are reproducible views, not independent versions. Frozen sources feed the tables in the README, report, methodology, beginner guide, viva guide and slide content through `src/build_submission_docs.py`.

## Confirmed pipeline

```text
Raw Crunchbase Dataset
-> Filtering / preprocessing
-> 100-project stratified dataset
-> Feature engineering
-> Investment Potential Score
-> Funding-History Risk Proxy
-> Strategic Alignment Score
-> Integer Programming
-> Goal Programming
-> Budget scenarios
-> Priority scenarios
-> Logical-constraint scenarios
-> IP vs GP comparison
-> Sensitivity analysis
-> Validation
```

The raw filtering stages are implemented in the preserved notebook but cannot be rerun completely in this checkout. The 100-project-to-results stages are available and validated. `objects.csv`, `funding_rounds.csv`, `acquisitions.csv` and other referenced raw tables are absent; only `funds.csv` and `ipos.csv` are present. The previously reported **462,651 entities** and **11,259 candidates** come from the supplied project brief, not a new count verified here. No intermediate counts have been invented.

## Classification of information and choices

| Class | Exact examples | How to describe them |
|---|---|---|
| Dataset-derived historical information | company identity/name, sector, country, status, founding/funding dates, funding rounds and totals; acquisition/IPO event membership | Historical recorded information, subject to completeness and source availability. |
| Derived/calculated variables | project IDs, funding years/duration, funding bands, cost proxy, normalized score components, IPS, Funding-History Risk Proxy, Strategic Alignment Score and portfolio totals | Reproducible calculations; a derived value may still rely on assumptions. |
| Modelling assumptions | Fixed sector/sample allocation, funding cutoffs, indivisible projects, historical funding as cost, IPS weights/status rubric, risk directions/equal weights, additive aggregation, payoff ideal method/range normalization | Interpretive/design choices, not observed business facts. |
| Decision-maker inputs | $25M/$50M/$75M budgets, enterprise-software sector priorities, GP priority weights, optional project interdependencies | Explicit preferences or supplied business rules. Current inputs are hypothetical scenarios. |
| Intentionally omitted | Multi-period spending constraints; UI; Nonlinear Programming | Not implemented. Annual costs are unsupported; UI/NLP are outside final scope. |

Acquisition/IPO indicators are calculated joins to recorded events, not probabilities or guarantees of success. Strategy is explicitly a **Decision-maker supplied strategic preference**, not an objective industry ranking. Logical pairs are **Scenario-based modelling assumptions**, not Crunchbase observations.

## Frozen mathematical specification

- Baseline IP: binary x; maximize total IPS; historical funding-based budget constraint only.
- Optional prerequisite: P005 requires P004; optional exclusion: P003/P004. The `baseline` configuration leaves both disabled.
- IPS: original `.30/.25/.25/.20` weighted normalized rounds, normalized calendar duration, status and outcome components, rounded to two decimals.
- Funding-History Risk Proxy: equal-weight reverse normalized rounds/duration, rounded to six decimals. Correlation with IPS: **-0.9600**; shared information and strong redundancy are acknowledged.
- Strategy: exact sector mapping in the configuration; identical sector means identical supplied preference score.
- GP: three linear goal equations and positive normalized penalties for P shortfall, R excess, S shortfall. No average-risk ratio or nonlinear model.
- Targets: individual maximum P, minimum total R and maximum S under the same hard constraints. Minimum R is zero at the empty portfolio. R normalization uses payoff-anchor risk range, not the zero target.
- Weights: balanced 1/3 each; focused .60 on the named goal and .20 on each other. Targets/scales are unchanged across priorities within a budget/logic case.

## Results and validation

Authoritative baseline IP: **$25M: 24 projects, IPS 706.67; $50M: 34 projects, IPS 968.34; $75M: 40 projects, IPS 1,184.18**.

Authoritative baseline balanced GP: **$25M: 18 projects, IPS 570.01; $50M: 25 projects, IPS 819.18; $75M: 30 projects, IPS 1,025.02**.

All 60 exported portfolios have Optimal solver status: 6 IP, 24 main GP, 18 payoff anchors, 12 additional fixed-target GP. The existing artifact validator passes **1586/1586 checks**; existing tests pass six cases. Independent HiGHS models cross-check exported CBC objectives. These checks concern numerical correctness, not economic truth of the proxies.

## Historical and cleanup decisions

- Original notebooks and raw/source datasets are retained unchanged.
- Original root-level IP CSVs are historical/superseded for baseline reporting. Their earlier discrepancy was already documented; it is not a new error or a reason to replace frozen final results.
- `docs/audit.md` and `docs/phase_log.md` are explicitly historical phase records; their earlier missing-work statements or smaller intermediate check counts are not current status.
- `docs/archive/` contains original pre-extension material and is labelled historical. Do not execute the archived original script to reproduce the final submission.
- Per-budget comparison CSVs remain as documented views; deleting them would remove useful reproducibility artifacts. No redundant new numerical result set is introduced.
- Five EDA figures remain historical context. The seven optimization figures are the publication set. No decorative charts are added.
- Local dependency installation and ignored Python caches are environment artifacts, not academic deliverables. No source data or historical notebook is deleted.

## Multi-period omission

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.

## Unresolved limitations

Raw-to-sample reconstruction and the two reported upstream counts cannot be independently verified without missing raw inputs. Historical funding is not a current investment price. The stratified sample limits generalization. Historical exits/closed statuses do not establish current investability. IPS is retrospective; the Funding-History Risk Proxy is not direct financial risk or failure probability. Strategy, logic, weights and ideal-target policies remain assumptions. These are disclosed limitations, not hidden data fixes.

See [final consistency report](../results/submission/consistency_report.md) for preservation checks, generated-document consistency and the created/modified file inventory.
