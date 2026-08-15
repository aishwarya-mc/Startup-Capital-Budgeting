import pandas as pd
from pathlib import Path
import pulp


# ============================================================
# INTEGER PROGRAMMING MODEL
# ============================================================
#
# Decision variable:
#   x_i = 1 if startup/project i is selected
#         0 otherwise
#
# Objective:
#   Maximize total investment potential
#
#       Maximize Sum(P_i * x_i)
#
# Budget constraint:
#
#       Sum(C_i * x_i) <= B
#
# Mutual exclusion:
#
#       x_P003 + x_P004 <= 1
#
# Prerequisite:
#
#       x_P005 <= x_P004
#
# Binary restriction:
#
#       x_i ∈ {0,1}
#
# Mutual-exclusion and prerequisite relationships are
# modelling assumptions because they are not provided
# directly by the dataset.
# ============================================================


# ============================================================
# 1. LOAD DATA
# ============================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "processed"
    / "startup_projects.csv"
)

df = pd.read_csv(input_file)


print("STARTUP CAPITAL BUDGETING - INTEGER PROGRAMMING")


print(f"\nNumber of projects: {len(df)}")


# ============================================================
# 2. CREATE INVESTMENT POTENTIAL SCORE
# ============================================================

def normalize(series):
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(100.0, index=series.index)

    return (
        (series - min_value)
        / (max_value - min_value)
        * 100
    )


df["rounds_score"] = normalize(
    df["funding_rounds"]
)

df["duration_score"] = normalize(
    df["funding_duration_years"]
)


status_scores = {
    "ipo": 100,
    "acquired": 90,
    "operating": 70,
    "closed": 20
}

df["status_score"] = (
    df["status"]
    .map(status_scores)
    .fillna(50)
)


df["outcome_score"] = (
    (df["acquisition"] + df["ipo"]) / 2
) * 100


df["investment_potential_score"] = (
    0.30 * df["rounds_score"]
    + 0.25 * df["duration_score"]
    + 0.25 * df["status_score"]
    + 0.20 * df["outcome_score"]
)

df["investment_potential_score"] = (
    df["investment_potential_score"].round(2)
)


# ============================================================
# 3. INTEGER PROGRAMMING FUNCTION
# ============================================================

def solve_portfolio(budget):

    model = pulp.LpProblem(
        "Startup_Capital_Budgeting",
        pulp.LpMaximize
    )

    # Binary decision variables
    x = {
        i: pulp.LpVariable(
            f"x_{i}",
            cat="Binary"
        )
        for i in df.index
    }

    # --------------------------------------------------------
    # OBJECTIVE
    # --------------------------------------------------------

    model += pulp.lpSum(
        df.loc[i, "investment_potential_score"] * x[i]
        for i in df.index
    )

    # --------------------------------------------------------
    # BUDGET CONSTRAINT
    # --------------------------------------------------------

    model += (
        pulp.lpSum(
            df.loc[i, "investment_cost"] * x[i]
            for i in df.index
        )
        <= budget,
        "Budget_Constraint"
    )

    # --------------------------------------------------------
    # MUTUAL EXCLUSION
    # P003 and P004 cannot both be selected.
    # --------------------------------------------------------

    p3 = df.index[
        df["project_id"] == "P003"
    ].tolist()

    p4 = df.index[
        df["project_id"] == "P004"
    ].tolist()

    if p3 and p4:
        model += (
            x[p3[0]] + x[p4[0]] <= 1,
            "Mutual_Exclusion_P003_P004"
        )

    # --------------------------------------------------------
    # PREREQUISITE
    # P005 requires P004.
    # --------------------------------------------------------

    p4 = df.index[
        df["project_id"] == "P004"
    ].tolist()

    p5 = df.index[
        df["project_id"] == "P005"
    ].tolist()

    if p4 and p5:
        model += (
            x[p5[0]] <= x[p4[0]],
            "Prerequisite_P005_requires_P004"
        )

    # --------------------------------------------------------
    # SOLVE
    # --------------------------------------------------------

    solver = pulp.PULP_CBC_CMD(msg=False)

    model.solve(solver)

    # --------------------------------------------------------
    # GET SELECTED PROJECTS
    # --------------------------------------------------------

    selected_indices = [
        i for i in df.index
        if pulp.value(x[i]) == 1
    ]

    selected_projects = df.loc[
        selected_indices
    ].copy()

    total_cost = selected_projects[
        "investment_cost"
    ].sum()

    total_potential = selected_projects[
        "investment_potential_score"
    ].sum()

    budget_used = (
        total_cost / budget * 100
        if budget > 0
        else 0
    )

    return (
        model,
        selected_projects,
        total_cost,
        total_potential,
        budget_used
    )


# ============================================================
# 4. RUN DIFFERENT BUDGET SCENARIOS
# ============================================================

budgets = [
    25_000_000,
    50_000_000,
    75_000_000
]


summary_results = []
all_selected_projects = []


for budget in budgets:

    (
        model,
        selected_projects,
        total_cost,
        total_potential,
        budget_used
    ) = solve_portfolio(budget)

    status = pulp.LpStatus[model.status]


    print(f"BUDGET: ${budget:,.0f}")
   

    print("Solver Status:", status)
    print(f"Projects Selected: {len(selected_projects)}")
    print(f"Total Investment: ${total_cost:,.2f}")
    print(f"Budget Used: {budget_used:.2f}%")
    print(
        f"Total Investment Potential Score: "
        f"{total_potential:.2f}"
    )

    print("\nSelected Projects:")

    if len(selected_projects) > 0:

        result = selected_projects[
            [
                "project_id",
                "startup_name",
                "sector",
                "investment_cost",
                "investment_potential_score"
            ]
        ]

        print(result.to_string(index=False))

        # Add budget information for saving
        temp = result.copy()
        temp["budget"] = budget
        all_selected_projects.append(temp)

    else:
        print("No projects selected.")

    # Save summary information
    summary_results.append({
        "budget": budget,
        "solver_status": status,
        "projects_selected": len(selected_projects),
        "total_investment": total_cost,
        "budget_used_percent": budget_used,
        "total_potential_score": total_potential
    })


# ============================================================
# 5. SAVE BUDGET SUMMARY
# ============================================================

results_dir = project_root / "results"

results_dir.mkdir(
    parents=True,
    exist_ok=True
)

summary_df = pd.DataFrame(summary_results)

summary_file = (
    results_dir
    / "integer_programming_budget_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


# ============================================================
# 6. SAVE SELECTED PROJECTS
# ============================================================

if all_selected_projects:

    selected_df = pd.concat(
        all_selected_projects,
        ignore_index=True
    )

    selected_file = (
        results_dir
        / "integer_programming_selected_projects.csv"
    )

    selected_df.to_csv(
        selected_file,
        index=False
    )


# ============================================================
# 7. SAVE SCORED DATASET
# ============================================================

scored_file = (
    project_root
    / "data"
    / "processed"
    / "startup_projects_scored.csv"
)

df.to_csv(
    scored_file,
    index=False
)


# ============================================================
# 8. FINAL OUTPUT
# ============================================================

print("FILES CREATED")


print(f"\nBudget summary:")
print(summary_file)

print(f"\nSelected projects:")
print(selected_file)

print(f"\nScored dataset:")
print(scored_file)

