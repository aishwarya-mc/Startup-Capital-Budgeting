````markdown
# Startup Capital Budgeting & Portfolio Optimization

## Project Overview

This project focuses on optimizing startup investment decisions under a limited budget using Operations Research techniques.

A publicly available startup dataset is analyzed to identify relevant investment patterns and create a structured modelling dataset. Each selected startup is assigned an Investment Potential Score, which is then used to optimize the selection of startups under different budget scenarios.

The project currently implements **Integer Programming** and proposes **Goal Programming** as a multi-objective extension.

---

## Problem Statement

How can an investor select the most promising combination of startups while making the best use of a limited investment budget?

---

## Objectives

- Analyze publicly available startup investment data.
- Prepare a structured dataset for optimization.
- Generate an Investment Potential Score for startups.
- Optimize startup selection using Integer Programming.
- Extend the optimization using Goal Programming.
- Develop an interactive decision-support system.

---

## Methodology

```text
Public Startup Dataset
        ↓
Data Preparation
        ↓
100-Project Modelling Dataset
        ↓
Statistical Analysis
        ↓
Investment Potential Scoring
        ↓
Integer Programming
        ↓
Goal Programming
        ↓
Model Comparison
        ↓
User Interface
````

---

## Dataset

The project uses a publicly available startup investment dataset containing information related to:

* Startups and companies
* Funding rounds
* Investments
* Acquisitions
* IPOs
* Funds
* People and organizations
* Startup sectors and outcomes

The raw data is processed to create a **100-project modelling dataset** suitable for optimization.

---

## Statistical Analysis

Exploratory analysis is performed to understand:

* Investment distribution
* Funding patterns
* Sector-wise investment
* Startup outcomes
* Relationship between funding and investment

The analysis is available in the `notebooks/` directory, with generated visualizations stored in `results/`.

---

## Investment Potential Scoring

An Investment Potential Score is assigned to each startup using relevant startup and investment indicators.

This score represents the relative investment potential of each project and is used as the primary objective in the Integer Programming model.

The scored dataset is stored in:

`data/processed/startup_projects_scored.csv`

---

## Integer Programming

Binary Integer Programming is used to select startups from the 100-project dataset.

Each startup has a binary selection decision:

* **1** → Startup selected
* **0** → Startup not selected

The model aims to maximize the total Investment Potential Score while ensuring that the selected investments remain within the available budget.

The model is evaluated under multiple budget scenarios:

* $25 Million
* $50 Million
* $75 Million

---

## Goal Programming

Goal Programming is proposed as a multi-objective extension of the Integer Programming model.

Instead of focusing only on investment potential, the proposed model will consider multiple goals such as:

* Investment potential
* Investment risk
* Strategic alignment

The model will identify a portfolio that provides a balanced solution across these objectives.

---

## Project Status

### Completed

* Dataset exploration
* Data preparation
* 100-project modelling dataset
* Statistical analysis
* Investment Potential Scoring
* Integer Programming
* Multiple budget scenarios
* Optimization results

### Planned

* Risk scoring
* Strategic-alignment scoring
* Goal Programming implementation
* Integer Programming vs Goal Programming comparison
* Sensitivity analysis
* Interactive user interface

---

## Project Structure

```text
Startup-Capital-Budgeting/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── results/
│
├── src/
│   ├── inspect_data.py
│   └── integer_programming.py
│
├── docs/
│
└── README.md
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Jupyter Notebook
* PuLP
* Git & GitHub

---

## Future System

The final system will allow users to:

1. Load the startup dataset.
2. View statistical information.
3. Select an optimization technique.
4. Specify an investment budget.
5. Generate an optimized startup portfolio.
6. Compare optimization results.

The final goal is to develop an interactive **startup investment decision-support system**.

```
```
