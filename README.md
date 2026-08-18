````markdown
# Startup Capital Budgeting and Portfolio Optimization

## Overview

A data-driven startup investment optimization framework that uses Operations Research techniques to select an optimal portfolio under limited capital.

The project uses a publicly available startup dataset, performs statistical analysis, generates an Investment Potential Score, and applies optimization techniques for investment selection.

## Problem Statement

How can we select the most promising combination of startups while maximizing investment potential under a limited investment budget?

## Objectives

- Prepare and analyze startup investment data.
- Create a structured 100-project modelling dataset.
- Generate Investment Potential Scores.
- Optimize startup selection using Integer Programming.
- Extend the model using Goal Programming.
- Develop an interactive decision-support interface.

## Methodology

```text
Public Startup Dataset
        ↓
Data Preparation
        ↓
100-Project Dataset
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

## Integer Programming

Binary decision variable:

```text
xᵢ = 1 → startup selected
xᵢ = 0 → startup not selected
```

### Objective

[
\max \sum_{i=1}^{100} P_i x_i
]

### Budget Constraint

[
\sum_{i=1}^{100} C_i x_i \leq B
]

Where:

* (P_i) = Investment Potential Score
* (C_i) = Investment Cost
* (B) = Available Budget

## Goal Programming

Goal Programming is proposed as a multi-objective extension considering:

* Investment potential
* Investment risk
* Strategic alignment

Basic formulation:

[
Actual + d^- - d^+ = Target
]

Goal Programming will be implemented and compared with Integer Programming in the next phase.

## Project Status

### Implemented

* Dataset preparation
* Statistical analysis
* Investment Potential Scoring
* Binary Integer Programming
* Multiple budget scenarios
* Optimization results

### Future Work

* Risk and strategic-alignment scoring
* Goal Programming
* IP vs GP comparison
* Sensitivity analysis
* Interactive user interface

## Project Structure

```text
Startup-Capital-Budgeting/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── results/
├── src/
├── docs/
└── README.md
```

## Technologies

* Python
* Pandas
* NumPy
* Matplotlib
* Jupyter Notebook
* PuLP
* Git & GitHub

## Expected Outcome

The final system will provide an interactive platform for loading startup data, generating statistics, selecting an optimization technique, and producing an optimized investment portfolio.

```
```
