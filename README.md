````markdown

\# Startup Capital Budgeting and Portfolio Optimization



\## Overview



This project develops a data-driven decision-support framework for selecting startup investment portfolios under limited capital.



A publicly available startup investment dataset is processed and transformed into a structured modelling dataset. Statistical analysis is performed to understand investment patterns, followed by the construction of an Investment Potential Score for each startup.



The scored projects are then used in optimization models to determine which startups should be selected under different investment budgets.



The current implementation focuses on Binary Integer Programming, while Goal Programming is proposed as the next phase for multi-objective portfolio optimization.



\---



\## Problem Statement



Investors and organizations often need to select a portfolio of startups from a large number of investment opportunities while operating under a limited budget.



The problem is to determine:



> Which combination of startups should be selected to maximize investment potential while satisfying the available investment budget?



The project addresses this problem using Operations Research optimization techniques.



\---



\## Objectives



\- Prepare and analyze publicly available startup investment data.

\- Construct a structured dataset suitable for optimization.

\- Generate an Investment Potential Score for each startup.

\- Formulate a Binary Integer Programming model for portfolio selection.

\- Evaluate portfolio selection under multiple budget scenarios.

\- Extend the framework using Goal Programming for multiple investment objectives.

\- Provide an interactive decision-support interface in the future phase.



\---



\## Dataset



The project uses a publicly available startup investment dataset containing information related to companies, funding, acquisitions, IPOs, and other startup characteristics.



The raw dataset consists of multiple CSV files. Relevant information is extracted and transformed into a modelling dataset.



\### Final Modelling Dataset



The project uses a structured dataset containing:



\- 100 startup projects

\- Multiple startup sectors

\- Investment cost

\- Funding-related attributes

\- Startup outcome information

\- Investment Potential Score



The processed datasets are stored in:



```text

data/

├── raw/

└── processed/

````



\---



\## Project Pipeline



```text

Public Startup Dataset

&#x20;       ↓

Data Preparation

&#x20;       ↓

100-Project Modelling Dataset

&#x20;       ↓

Statistical Analysis

&#x20;       ↓

Investment Potential Scoring

&#x20;       ↓

Integer Programming

&#x20;       ↓

Goal Programming

&#x20;       ↓

Scenario \& Model Comparison

&#x20;       ↓

Decision-Support User Interface

```



\---



\## Methodology



\### 1. Data Preparation



The raw startup investment data is processed to construct a consistent modelling dataset.



The resulting dataset contains 100 startup projects selected for the optimization study.



\---



\### 2. Statistical Analysis



Exploratory and statistical analysis is performed to understand:



\* Investment-cost distribution

\* Funding rounds

\* Funding patterns

\* Sector distribution

\* Startup outcomes

\* Investment relationships



The analysis and visualizations are stored in the `notebooks/` and `results/` directories.



\---



\### 3. Investment Potential Scoring



An Investment Potential Score is generated for each startup using relevant historical startup indicators.



The resulting scored dataset is used as an input to the optimization model.



Output:



```text

data/processed/startup\_projects\_scored.csv

```



\---



\## 4. Integer Programming



The current optimization model uses Binary Integer Programming.



For each startup:



```text

xᵢ = 1  → startup is selected

xᵢ = 0  → startup is not selected

```



\### Objective



The model maximizes the total Investment Potential Score:



\[

\\max \\sum\_{i=1}^{100} P\_i x\_i

]



where:



\* (P\_i) = Investment Potential Score of startup (i)

\* (x\_i) = binary selection variable



\### Budget Constraint



\[

\\sum\_{i=1}^{100} C\_i x\_i \\leq B

]



where:



\* (C\_i) = investment cost of startup (i)

\* (B) = available investment budget



The model selects the combination of startups that provides the highest total investment potential while remaining within the available budget.



\---



\## Budget Scenarios



The Integer Programming model is evaluated under three investment budgets:



| Budget | Projects Selected | Total Investment | Potential Score |

| -----: | ----------------: | ---------------: | --------------: |

|   $25M |                24 |          $24.93M |          706.67 |

|   $50M |                33 |          $49.93M |          958.34 |

|   $75M |                40 |          $74.59M |         1168.34 |



> These results correspond to the current implemented version of the Integer Programming model.



\---



\## 5. Goal Programming



Goal Programming is proposed as a multi-objective extension of the Integer Programming model.



Instead of optimizing only investment potential, the proposed model will consider multiple goals such as:



\* Investment potential

\* Investment risk

\* Strategic alignment



The model will use deviation variables to measure the difference between achieved values and desired targets.



Basic goal formulation:



\[

Actual + d^- - d^+ = Target

]



The final Goal Programming implementation and comparison with Integer Programming are part of the next development phase.



\---



\## Project Status



\### Implemented



\* \[x] Dataset exploration

\* \[x] Data preparation

\* \[x] 100-project modelling dataset

\* \[x] Statistical analysis

\* \[x] Investment Potential Scoring

\* \[x] Binary Integer Programming

\* \[x] Multiple budget scenarios

\* \[x] Optimization result generation



\### Planned



\* \[ ] Risk scoring

\* \[ ] Strategic-alignment scoring

\* \[ ] Goal Programming implementation

\* \[ ] Integer Programming vs Goal Programming comparison

\* \[ ] Scenario and sensitivity analysis

\* \[ ] Interactive user interface

\* \[ ] Final decision-support system



\---



\## Project Structure



```text

Startup-Capital-Budgeting/

│

├── data/

│   ├── raw/

│   └── processed/

│

├── notebooks/

│   ├── 01\_dataset\_exploration.ipynb

│   └── 02\_statistical\_analysis.ipynb

│

├── results/

│   ├── data\_dictionary.csv

│   ├── integer\_programming\_budget\_summary.csv

│   ├── integer\_programming\_selected\_projects.csv

│   └── visualizations/

│

├── src/

│   ├── inspect\_data.py

│   └── integer\_programming.py

│

├── docs/

│   └── \[project documentation]

│

└── README.md

```



\---



\## Technologies Used



\* Python

\* Pandas

\* NumPy

\* Matplotlib

\* Jupyter Notebook

\* Integer Programming / Operations Research

\* Git \& GitHub



\---



\## Outputs



The project generates:



\* Processed startup datasets

\* Scored startup dataset

\* Statistical analysis results

\* Data visualizations

\* Integer Programming budget summaries

\* Selected startup portfolios



Important optimization outputs are stored in:



```text

results/integer\_programming\_budget\_summary.csv

results/integer\_programming\_selected\_projects.csv

```



\---



\## Team Development



The project is developed collaboratively, with different team members contributing to:



\* Dataset preparation and analysis

\* Statistical modelling

\* Investment scoring

\* Optimization modelling

\* Documentation

\* User-interface development

\* Future Goal Programming implementation



\---



\## Future Direction



The final system aims to provide an interactive platform where users can:



1\. Load the startup dataset.

2\. Generate statistics on demand.

3\. Select an optimization technique.

4\. Specify an investment budget.

5\. Generate an optimized startup portfolio.

6\. Compare different optimization approaches.



The long-term objective is to transform the project into an interactive startup investment decision-support system.



```

```



