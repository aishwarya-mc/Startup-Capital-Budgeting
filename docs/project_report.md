# Startup Capital Budgeting: Team Project Report

**Course:** Operations Research · **Techniques:** Integer Programming and Goal Programming · **Tool:** Python (PuLP / CBC) with a Streamlit interface

This report lets any team member understand the whole project, run the application, and present it with confidence. It summarises the existing technical documents in this folder; where exact definitions are needed, it points to them.

**Contents**

1. [Project at a glance](#1-project-at-a-glance)
2. [The problem in plain language](#2-the-problem-in-plain-language)
3. [Dataset and preparation](#3-dataset-and-preparation)
4. [Scores used by the models](#4-scores-used-by-the-models)
5. [Technique 1: Integer Programming](#5-technique-1-integer-programming)
6. [Technique 2: Goal Programming](#6-technique-2-goal-programming)
7. [Results](#7-results)
8. [Interpreting the results](#8-interpreting-the-results)
9. [The user interface](#9-the-user-interface)
10. [How to use the UI: step by step](#10-how-to-use-the-ui-step-by-step)
11. [Presentation guide](#11-presentation-guide)
12. [Likely questions and answers](#12-likely-questions-and-answers)
13. [Limitations and honest caveats](#13-limitations-and-honest-caveats)
14. [Repository map and reproduction](#14-repository-map-and-reproduction)
15. [Glossary](#15-glossary)

---

## 1. Project at a glance

| Item | Detail |
|---|---|
| **Question** | Given a fixed budget, which startups should an investor fund? |
| **Data** | Crunchbase startup records (historical, up to about 2013); a stratified sample of **100 projects** across **10 sectors** |
| **Technique 1** | **Integer Programming (IP):** maximise one score (investment potential) |
| **Technique 2** | **Goal Programming (GP):** balance three goals (potential, risk, strategic fit) |
| **Budgets studied** | $25M, $50M, $75M (the UI allows any budget) |
| **Solver** | PuLP with the CBC solver; every reported solution is proven optimal |
| **Interface** | Streamlit app: load data, generate statistics on demand, run either technique, compare |
| **Validation** | 1,586 numerical checks passed; 60 portfolios independently cross-checked; unit tests pass |

**One-sentence summary:** *IP picks the portfolio with the highest total potential; GP gives up some potential to reduce risk and improve strategic fit, and the UI lets anyone explore that trade-off interactively.*

### How the project meets the course requirement

| Requirement from the instructor | Where it is met |
|---|---|
| Publicly available dataset | Crunchbase startup data (public Kaggle dataset) |
| Apply optimisation techniques from the course | Integer Programming and Goal Programming |
| UI where data can be loaded | **Data** tab and sidebar upload |
| Statistics generated on demand | **Statistics** tab (Generate button) |
| At least two optimisations, user-selectable | **Optimize** tab: choose IP or GP |

---

## 2. The problem in plain language

An investor has a limited pot of money and a list of 100 startups. Each startup has a **cost** (what it would take to fund it) and some **attractiveness scores**. Funding everyone would cost about **$1.38 billion**, so a $50M budget covers only a small part. The investor must choose a subset.

This is a classic **capital budgeting** problem. Each startup is an all-or-nothing decision (fund it fully or not at all), which is why the variables are binary and the model is an *integer* program.

Two different ways to define "best":

- **IP:** "best" means the highest total *investment potential*, nothing else.
- **GP:** "best" means being as close as possible to ideal targets on *several* goals at once, weighted by the decision-maker's priorities.

---

## 3. Dataset and preparation

**Source.** The Crunchbase historical tables (companies, funding rounds, acquisitions, IPOs, and so on). Coverage ends around 2013.

**Filtering (documented in `notebooks/01_dataset_exploration.ipynb`):**

1. Keep entities of type *Company* with positive total funding and at least one funding round.
2. Keep companies whose **first funding year** is 2010–2013.
3. Keep ten named sectors: advertising, biotech, ecommerce, enterprise, games/video, hardware, medical, mobile, software, web.
4. Cap historical funding at $100M.

**Sampling.** The remaining candidates were split by sector and funding band (Low / Medium / High / Very High), and a fixed random sample was drawn with `random_state=42`: 2 / 3 / 3 / 2 companies per band in each sector. That gives **10 sectors × 10 companies = 100 projects**. The sample is deliberately *stratified*, not proportional to the real population, so every sector and funding scale is represented.

**The final dataset** (`data/processed/startup_projects_scored.csv`) holds 100 rows. Key facts:

| Measure | Value |
|---|---|
| Projects / sectors | 100 / 10 |
| Cost: minimum / median / maximum | $7,208 / $5.95M / $100M |
| Total cost of all projects | $1,379,594,386 |
| Status mix | 92 operating, 3 acquired, 3 IPO, 2 closed |

**Cost proxy.** A startup's "investment cost" is its historical total funding. It is a size-related proxy, *not* a real purchase price or valuation.

> Only `funds.csv` and `ipos.csv` among the raw tables are tracked in the repository; the very large raw files are git-ignored. The processed 100-project files are what the models use.

---

## 4. Scores used by the models

Every project gets three scores on a 0–100 scale. `N(·)` below means min–max normalisation to 0–100 across the 100 projects.

| Score | Formula | Meaning |
|---|---|---|
| **Investment Potential Score (IPS)** | 0.30·N(rounds) + 0.25·N(duration) + 0.25·status score + 0.20·outcome score | A relative attractiveness heuristic: more funding rounds, longer funding history, a better status, and recorded exits all raise it. |
| **Funding-History Risk Proxy** | 0.50·(100 − N(rounds)) + 0.50·(100 − N(duration)) | Higher means less observed funding history. **It is not a failure probability.** |
| **Strategic Alignment Score** | Lookup by sector | How well the sector fits the investor's mandate. |

- **Status score:** IPO 100, acquired 90, operating 70, closed 20.
- **Outcome score:** 50 × (acquisition flag + IPO flag).
- **Strategic scores (hypothetical enterprise-software investor):** software and enterprise 100; web and mobile 75; ecommerce and hardware 50; advertising and games/video 25; biotech and medical 0. These are *decision-maker preferences*, not facts about the industries, and the UI lets you change them.

**Important relationship.** IPS and the risk proxy correlate at **−0.96**, because both come from the same funding-history variables. In practice, the high-potential companies are also the ones with the lowest "risk" proxy, and vice versa. This is why the goals interact in interesting ways, and it is a point to state openly in the presentation.

Full definitions: `docs/methodology.md`, `docs/risk_methodology.md`, `docs/strategic_methodology.md`.

---

## 5. Technique 1: Integer Programming

A **0–1 knapsack** problem. For project *i*, the decision variable is *xᵢ* = 1 if funded, 0 otherwise.

```
Maximise     Σ IPSᵢ · xᵢ                    (total investment potential)
subject to   Σ Cᵢ · xᵢ ≤ B                   (stay within the budget)
             xᵢ ∈ {0, 1}                      (fund fully or not at all)
```

- `Cᵢ` is the project's cost and `B` is the budget.
- **Optional logic rules** (scenario assumptions, not dataset facts):
  - *A requires B:* `xₐ ≤ x_b`
  - *A excludes B:* `xₐ + x_b ≤ 1`
- CBC solves it to proven optimality (relative and absolute gap set to 0).

**Strength:** simple, transparent, finds the true maximum of one objective.
**Weakness:** ignores everything except that one objective.

---

## 6. Technique 2: Goal Programming

GP replaces "maximise one thing" with "get as close as possible to targets on several goals".

**Three goals**

| Goal | Aim |
|---|---|
| Potential (P) | Total IPS as high as possible |
| Risk (R) | Total risk proxy as low as possible |
| Strategic (S) | Total strategic alignment as high as possible |

**Targets.** Each goal's target is its *ideal value*, found by optimising that goal alone under the same budget. The risk ideal is zero (the empty portfolio).

**Deviation variables.** Each goal gets an under-achievement variable *d⁻* and an over-achievement variable *d⁺*:

```
Σ IPSᵢ xᵢ  + dP⁻ − dP⁺ = T_P
Σ Rᵢ  xᵢ  + dR⁻ − dR⁺ = T_R
Σ Sᵢ  xᵢ  + dS⁻ − dS⁺ = T_S
```

**Objective.** Only the *undesirable* deviations are penalised (too little potential, too much risk, too little strategic fit), each divided by a scale so the goals are comparable:

```
Minimise   wP · dP⁻ / S_P   +   wR · dR⁺ / S_R   +   wS · dS⁻ / S_S
```

The same budget and binary constraints from IP still apply. The weights `w` express the decision-maker's priorities.

**Preset priorities**

| Preset | Potential | Risk | Strategic |
|---|---:|---:|---:|
| Balanced | 1/3 | 1/3 | 1/3 |
| Potential focused | 0.60 | 0.20 | 0.20 |
| Risk focused | 0.20 | 0.60 | 0.20 |
| Strategy focused | 0.20 | 0.20 | 0.60 |

**Achievement %** (shown in the UI): `100 × (1 − undesirable deviation / scale)`. 100% means the goal's ideal target was met.

---

## 7. Results

All results are proven optimal. Baseline means no logic rules.

### 7.1 Integer Programming

| Budget | Projects | Investment | Utilisation | Potential | Risk proxy | Strategic |
|---|---:|---:|---:|---:|---:|---:|
| $25M | 24 | $24,929,310 | 99.72% | 706.67 | 1,879.17 | 1,125 |
| $50M | 34 | $49,980,834 | 99.96% | 968.34 | 2,745.83 | 1,625 |
| $75M | 40 | $74,989,291 | 99.99% | 1,184.18 | 3,141.67 | 1,900 |

### 7.2 Goal Programming (balanced priority)

| Budget | Projects | Investment | Potential | Risk proxy | Strategic |
|---|---:|---:|---:|---:|---:|
| $25M | 18 | $24,833,829 | 570.01 | 1,337.50 | 1,225 |
| $50M | 25 | $49,897,820 | 819.18 | 1,804.17 | 1,725 |
| $75M | 30 | $74,862,396 | 1,025.02 | 2,087.50 | 2,000 |

### 7.3 IP vs balanced GP (change = GP − IP)

| Budget | Projects | Potential | Risk proxy | Strategic |
|---|---:|---:|---:|---:|
| $25M | −6 | −136.66 | −541.67 | +100 |
| $50M | −9 | −149.16 | −941.67 | +100 |
| $75M | −10 | −159.16 | −1,054.17 | +100 |

### 7.4 GP priorities at $50M (baseline)

| Priority | Projects | Potential | Risk proxy | Strategic |
|---|---:|---:|---:|---:|
| Balanced | 25 | 819.18 | 1,804.17 | 1,725 |
| Potential focused | 30 | 938.34 | 2,245.83 | 1,675 |
| Risk focused | 10 | 513.35 | 408.33 | 775 |
| Strategy focused | 28 | 807.51 | 2,225.00 | 1,925 |

### 7.5 Effect of logic rules (IP)

With the two assumed rules (P005 requires P004; P003 and P004 mutually exclusive):

- **$25M:** no change; the baseline already satisfied both rules.
- **$50M:** 33 projects, potential 958.34 (baseline 968.34). The baseline picked both P003 and P004, which the rule forbids.
- **$75M:** 40 projects, potential 1,168.34 (baseline 1,184.18).

Adding constraints can only keep or lower the best attainable potential.

Source files: `results/optimization/*.csv`; full tables in `docs/final_results_summary.md`.

---

## 8. Interpreting the results

1. **More budget buys more projects**, with diminishing returns: extra potential per extra dollar falls as the budget grows.
2. **IP has the highest potential by construction**, and GP can never beat it on that single goal. GP's value is that it balances goals.
3. **Balanced GP funds fewer projects** with lower total risk and a slightly higher strategic score. Part of the "risk reduction" comes simply from funding fewer companies, since the risk proxy is a *sum*. State this honestly.
4. **Priorities steer the portfolio.** Risk-focused GP funds only about 10 projects at $50M; strategy-focused GP leans toward software and enterprise.
5. **Neither technique is "better".** They answer different questions. IP asks "what maximises one measure?"; GP asks "what is the best compromise given my priorities?"
6. **Logic rules cost something.** Business interdependencies can reduce the best achievable value, and the model quantifies by how much.

---

## 9. The user interface

A Streamlit web app, run locally. It reuses the validated formulations (via `src/ui_engine.py`) and reproduces the published numbers: for example, IP at $50M gives 34 projects and potential 968.34; balanced GP gives 25 projects and 819.18.

### 9.1 Layout

| Area | Purpose |
|---|---|
| **Sidebar** | Global settings: dataset, sector preferences, budget, logic rules |
| **Overview** | Summary cards and the submitted reference results |
| **Data** | Browse, filter, search and download the table |
| **Statistics** | Descriptive analytics, generated on demand |
| **Optimize** | Run IP or GP and inspect the portfolio |
| **Compare & Explore** | Side-by-side comparison, budget sweep, trade-off curve |
| **Methodology** | Formulas, definitions and limitations |

### 9.2 Key terms shown on screen

| Term | Meaning |
|---|---|
| **Universe cost** | Total cost of all candidate projects (about $1,379.59M); the budget is only a small share of it |
| **Logic rules** | Count of active "A requires B" / "A excludes B" restrictions |
| **Logic scenario: baseline** | No logic rules |
| **Logic scenario: assumed_logic** | The two example rules are applied |
| **Priority** (GP) | The weight preset used; IP shows `single_objective` |
| **Reference results table** | A static copy of the submitted results; it never changes with your inputs and serves as the answer key to check the live results against |

---

## 10. How to use the UI: step by step

### 10.1 Start the app

Open the project folder (the one containing `app.py`) in VS Code, open a terminal, and run:

```powershell
python -m pip install -r requirements.txt   # first time only
streamlit run app.py
```

A browser tab opens at `http://localhost:8501`. Press `Ctrl+C` in the terminal to stop it.

If `streamlit` is not recognised, use `python -m streamlit run app.py`. If modules are missing, make sure VS Code is using the Python interpreter where you installed the requirements.

### 10.2 Configure the sidebar

1. **Dataset.** The 100-project sample loads automatically. To use your own data, click **Upload** and choose a CSV. A template is available on the Data tab. Use **Back to sample dataset** to return.
2. **Strategic preference by sector.** Expand it and drag the sliders (0–100). Higher means the sector fits the investor's mandate better.
3. **Capital budget.** Drag the slider (in $M).
4. **Logical constraints.** Choose **None**, **Assumed** (the two example rules) or **Custom**. For Custom, add rows in the table: pick the rule type and two project IDs.

### 10.3 Explore the data (Data tab)

Filter by sector or status, search by name or ID, and download the table as CSV.

**Uploading your own CSV** needs: `project_id` (unique), `startup_name`, `sector`, `investment_cost` (> 0), and either the two scores (`investment_potential_score`, `risk_score`) or the raw fields to compute them (`funding_rounds`, `funding_duration_years`, `status`, optional `acquisition`, `ipo`).

### 10.4 Generate statistics (Statistics tab)

Tick the analyses you want and press **Generate statistics**. Nothing is computed until you press it.

| Analysis | What it shows |
|---|---|
| Summary table | Mean, median, quartiles of every numeric field |
| Distributions | Cost (log scale) and potential histograms |
| Sector profile | Total cost and mean scores per sector |
| Correlations | Heatmap; shows the −0.96 potential-risk relationship |
| Cost vs potential map | Every project plotted; bubble size is strategic fit |
| Status & funding mix | Company status and funding bands |
| Top / bottom projects | Potential per $1M invested |

### 10.5 Run an optimisation (Optimize tab)

**Integer Programming**

1. Choose **Integer Programming**.
2. Pick an objective (normally "Maximise investment potential").
3. Press **Solve with Integer Programming**.

**Goal Programming**

1. Choose **Goal Programming**.
2. Click a preset (Balanced, Potential Focused, Risk Focused, Strategy Focused) or drag the three weight sliders.
3. Press **Solve with Goal Programming**.

**Reading the result**

- **Cards:** status, projects funded, money invested, and the three score totals.
- **Badges:** budget, binary and logic checks. If a rule is violated, a warning shows instead.
- **Gauge:** share of the budget used.
- **Goal bars (GP only):** achievement of each goal, 100% being ideal.
- **Scatter plot:** funded projects in teal against unfunded in grey.
- **Table:** the chosen portfolio, with a CSV download.

> After changing the budget, weights or rules, press **Solve** again; a warning tells you when the displayed result is stale.

### 10.6 Compare and explore (Compare & Explore tab)

| View | What to do | What you learn |
|---|---|---|
| **IP vs GP at this budget** | Loads automatically | A table, radar chart, overlap heatmap and sector mix for IP and all four GP priorities |
| **Budget sweep** | Set the range and points, press **Run sweep** | How totals and project counts change with budget; diminishing returns |
| **Trade-off explorer** | Press **Trace trade-off curve** | How GP outcomes move as weight shifts toward potential |

Sweeps solve several optimisation problems and take a few seconds.

### 10.7 Quick sanity check

Use the sample data, budget $50M, logic **None**. IP should return **34 projects, potential 968.3**; balanced GP should return **25 projects, potential 819.2**. These match the reference table on the Overview tab.

---

## 11. Presentation guide

A suggested five-to-seven minute flow, with a live demonstration.

| Step | Say / show |
|---|---|
| 1. Problem (30 s) | "An investor with a fixed budget must choose among 100 startups. Funding all would cost $1.38B." |
| 2. Data (45 s) | Overview and Data tabs. Crunchbase, stratified sample, three scores. |
| 3. Statistics (60 s) | Generate all analyses. Point to the correlation heatmap: potential and risk move opposite ways, so goals conflict. |
| 4. Integer Programming (60 s) | Show the formulation (Methodology tab), then Solve at $50M: 34 projects, potential 968.34. |
| 5. Goal Programming (90 s) | Explain targets and deviations. Solve *Balanced*: 25 projects. Then *Risk Focused* to show the portfolio shrinking and shifting. |
| 6. Constraints (30 s) | Switch to *Assumed* logic, re-solve, and show the logic badge and the small drop in potential. |
| 7. Comparison (60 s) | Compare & Explore: radar and budget sweep. |
| 8. Conclusion (30 s) | "IP maximises one objective; GP finds a compromise. The right choice depends on what the investor values." |

**Tips**

- Open the app **before** presenting and click through once, so the first solve is warm.
- Keep the budget at $50M unless demonstrating a change.
- Say clearly that the strategic scores and logic rules are *assumptions*.
- If asked something unexpected, the Methodology tab has the formulas on screen.

**Suggested division of work for a team**

| Part | Presenter focus |
|---|---|
| Problem, data, statistics | Sections 2–4 |
| Integer Programming | Section 5 and 7.1 |
| Goal Programming | Section 6 and 7.2–7.4 |
| UI demonstration and comparison | Sections 9–10 |
| Limitations and conclusion | Sections 8 and 13 |

---

## 12. Likely questions and answers

**Why integer programming and not linear programming?**
A project is funded fully or not at all. Allowing fractions (LP) would let the model buy 0.37 of a startup, which does not match the decision.

**Why does IP use almost the whole budget?**
Extra potential is always worth having, and with 100 projects of varied sizes, a combination that fills the budget almost exactly nearly always exists (about 99.7–99.99% used).

**Why does GP fund fewer projects but still seem sensible?**
It deliberately trades some potential for lower total risk and better strategic fit. Note that the risk proxy is a sum, so funding fewer companies lowers it mechanically.

**Is GP better than IP?**
No. They answer different questions. IP is best for one objective; GP is best when several objectives matter.

**How are the GP targets chosen?**
Each target is the best value achievable for that goal alone, under the same budget. The risk target is zero (empty portfolio).

**What do the deviation variables mean?**
They measure how far a goal falls short of (or overshoots) its target. Only the undesirable direction is penalised.

**What does the risk score actually measure?**
Limited observed funding history. It is a proxy, not a failure probability or financial risk measure.

**Why do potential and risk correlate so strongly (−0.96)?**
Both are built from funding rounds and duration. It means the two scores are largely redundant, which is a stated limitation.

**Are the strategic scores real?**
No. They represent a hypothetical enterprise-software investor and can be changed in the UI.

**Are the logic rules from the data?**
No. They are illustrative scenario assumptions showing how business dependencies can be modelled.

**Can the model handle a different dataset?**
Yes. Upload a CSV with the required columns and the same models run on it.

**How do you know the solution is optimal?**
CBC is run with zero optimality gap and the status must be *Optimal*. Results were also cross-checked independently (60 portfolios, 1,586 checks).

**Why no multi-period budgeting?**
The dataset has historical funding, not defensible future yearly spending, so a multi-year model would need unsupported assumptions.

---

## 13. Limitations and honest caveats

- **Historical academic demonstration.** Not investment advice. Data ends around 2013.
- **Cost is a proxy:** historical funding, not a purchase price or valuation.
- **Potential score is retrospective:** it uses status and outcomes already observed, so it is not a forward-looking prediction.
- **Risk proxy is not real risk:** it comes from funding history only and overlaps heavily with potential.
- **Weights and scores are assumptions:** score weights, status values, strategic preferences, GP priorities and logic pairs are modelling choices.
- **Sample is stratified:** 100 projects, equal per sector; conclusions apply to this sample, not the whole market.
- **Ties:** when several portfolios are equally optimal, the specific selection can vary.
- **Single period:** one budget at a time.
- **UI:** the live GP solves reuse the same formulation and match the frozen results for the default configuration. Choosing "minimise risk" as an IP objective returns the trivial empty portfolio, which is expected.

---

## 14. Repository map and reproduction

```
app.py                     Streamlit interface
.streamlit/config.toml     Theme settings
src/
  ui_engine.py             Solver layer used by the UI
  portfolio_model.py       Shared model building and validation
  integer_programming.py   Batch IP runs
  goal_programming.py      Batch GP runs
  score_projects.py        Score calculation
  sensitivity_analysis.py  Sensitivity experiments
  validate_results.py      Independent checks
config/model_config.json   Budgets, logic scenarios, strategy scores, GP priorities
data/processed/            The 100-project dataset (plain and scored)
results/optimization/      Frozen results, charts and validation outputs
docs/                      Methodology, audit, results summary, viva prep, this report
tests/test_models.py       Unit tests
```

**Reproduce and verify**

```powershell
python -m pip install -r requirements.txt
python src/validate_results.py
python -m unittest discover -s tests -v
streamlit run app.py
```

**Further reading in `docs/`:** `methodology.md` (exact mathematics), `final_results_summary.md` (all result tables), `project_explanation_beginner.md` (study from zero), `viva_preparation.md` (80 Q&As), `final_presentation_content.md` (slide outlines), `team_split.md` (work split).

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **Capital budgeting** | Choosing which projects to fund with limited money |
| **Binary variable** | A 0/1 decision; here 1 = fund the project |
| **Knapsack problem** | Choosing items under a capacity limit to maximise value |
| **Integer Programming (IP)** | Optimisation where some variables must be whole numbers |
| **Goal Programming (GP)** | Optimisation that minimises deviations from several targets |
| **Objective function** | The quantity being maximised or minimised |
| **Constraint** | A rule a solution must satisfy (for example the budget) |
| **Deviation variable** | Measures how far a goal is above or below its target |
| **Payoff table / ideal target** | The best value each goal can reach on its own |
| **Prerequisite constraint** | "A requires B": A may be chosen only if B is |
| **Mutual exclusion** | "A excludes B": at most one of the two |
| **IPS** | Investment Potential Score |
| **Risk proxy** | Funding-History Risk Proxy, a score derived from funding history |
| **Strategic alignment** | Fit between a project's sector and the investor's mandate |
| **Utilisation** | Share of the budget actually spent |
| **Optimal (solver status)** | The solver proved no better solution exists |
| **Stratified sampling** | Sampling within defined groups so each is represented |
| **Jaccard overlap** | Shared projects divided by all projects in either portfolio (0–1) |
