\# Detailed Project Methodology



\## 1. Project Overview



The project develops a startup investment portfolio optimization system using Operations Research techniques.



The central idea is to start with publicly available startup investment data, identify relevant startup characteristics, transform them into a structured modelling dataset, calculate an Investment Potential Score, and then use optimization techniques to determine which startups should be selected under a limited investment budget.



The project is designed around the following overall pipeline:



```text

Public Startup Dataset

&#x20;       ↓

Data Exploration

&#x20;       ↓

Data Preparation

&#x20;       ↓

100-Project Modelling Dataset

&#x20;       ↓

Feature Engineering

&#x20;       ↓

Investment Potential Scoring

&#x20;       ↓

Integer Programming

&#x20;       ↓

Goal Programming

&#x20;       ↓

Scenario / Model Comparison

&#x20;       ↓

User Interface

```



The current repository contains the implemented data-processing and Integer Programming components. Goal Programming and the complete user interface are planned extensions.



\---



\## 2. Dataset



\### 2.1 Source Dataset



The project uses a publicly available startup investment dataset containing information about companies, funding, investments, acquisitions, IPOs, people, organizations, and other startup-related entities.



The raw dataset is divided into multiple CSV files rather than being provided as one single table.



The main raw files are:



\* `objects.csv`

\* `relationships.csv`

\* `funding\_rounds.csv`

\* `degrees.csv`

\* `offices.csv`

\* `people.csv`

\* `milestones.csv`

\* `investments.csv`

\* `acquisitions.csv`

\* `funds.csv`

\* `ipos.csv`



These files represent different aspects of the startup ecosystem.



\---



\## 3. Understanding the Raw CSV Files



\### 3.1 objects.csv



This is the main entity table.



It contains information about entities such as companies and people.



Important attributes include:



\* `id` → unique identifier of the entity

\* `entity\_type` → identifies the type of entity

\* `name` → company or entity name

\* `category\_code` → startup sector/category

\* `status` → operating, acquired, closed, IPO, etc.

\* `founded\_at` → founding date

\* `country\_code` → country

\* `funding\_rounds` → number of funding rounds

\* `funding\_total\_usd` → total funding received

\* `first\_funding\_at` → first funding date

\* `last\_funding\_at` → latest funding date



This file provides much of the basic startup information used in the modelling dataset.



\### 3.2 funding\_rounds.csv



This file contains individual funding-round information.



Important information includes:



\* Funding round ID

\* Company/object ID

\* Funding date

\* Funding round type

\* Funding round code

\* Amount raised

\* Pre-money valuation

\* Post-money valuation

\* Whether the round was the first round

\* Whether the round was the final round



This data is useful for understanding the funding history and funding activity of startups.



\### 3.3 acquisitions.csv



This file records acquisition events.



Important information includes:



\* Acquiring company

\* Acquired company

\* Acquisition price

\* Currency

\* Acquisition date



For this project, acquisition information contributes to understanding whether a startup achieved a significant outcome.



\### 3.4 ipos.csv



This file contains information about companies that went public.



Important information includes:



\* Company/object ID

\* Valuation amount

\* Valuation currency

\* Amount raised

\* Public listing date

\* Stock symbol



IPO information is used as one of the indicators of startup outcome.



\### 3.5 relationships.csv



Contains relationships between entities.



It can describe connections between companies, people, investors, and other entities.



It is useful for understanding the startup ecosystem, although it is not directly required for the current Integer Programming formulation.



\### 3.6 people.csv



Contains information about people associated with the startup ecosystem.



It can be used to study founders, employees, investors, and other individuals.



It is primarily part of the broader dataset rather than a direct input to the current optimization model.



\### 3.7 degrees.csv



Contains educational information associated with people.



It can potentially support future founder-profile or human-capital analysis.



\### 3.8 offices.csv



Contains information about company offices and locations.



This can provide geographical information about startups.



\### 3.9 milestones.csv



Contains important startup milestones.



Milestones can potentially be used in future versions of the investment scoring system.



\### 3.10 investments.csv



Contains investment relationships and investment activity involving companies and investors.



This provides additional information about the startup investment ecosystem.



\### 3.11 funds.csv



Contains information about investment funds.



This is part of the original dataset but is not a primary input to the current portfolio optimization model.



\---



\## 4. Dataset Exploration



Before modelling, the raw CSV files are systematically explored.



The dataset exploration stage performs:



\* File identification

\* Row and column inspection

\* Column-name inspection

\* Missing-value analysis

\* Basic statistical analysis

\* Category analysis

\* Status analysis

\* Funding analysis

\* Sector analysis



For example, the exploration notebook examines entity types, startup categories, startup statuses, funding statistics, funding rounds, acquisition information, and IPO information.



The purpose of this stage is to determine:



> Which information from the large raw dataset is actually useful for the investment optimization problem?



\---



\## 5. Identifying Eligible Startups



The raw entity data is filtered to identify companies suitable for the modelling process.



The exploration process considers companies with:



\* `entity\_type = Company`

\* Positive total funding

\* At least one funding round



The funding dates are then converted into proper date values.



The first funding year is extracted to support further filtering and analysis.



The project focuses on startups with funding activity in the 2010–2013 period for the modelling dataset.



\---



\## 6. Creating the Modelling Dataset



The raw startup information is transformed into a structured dataset specifically designed for optimization.



The resulting dataset contains 100 startup projects.



Each project receives a unique project ID:



```text

P001

P002

P003

...

P100

```



The modelling dataset contains attributes such as:



\* Project ID

\* Company ID

\* Startup name

\* Sector

\* Country

\* Status

\* Founded date

\* First funding date

\* Last funding date

\* First funding year

\* Last funding year

\* Funding duration

\* Number of funding rounds

\* Total funding

\* Investment cost

\* Acquisition indicator

\* IPO indicator

\* Funding band



The actual processed dataset confirms this structure.



\---



\## 7. Feature Engineering



Feature engineering converts raw startup information into variables that can be meaningfully used by the optimization model.



The important derived features include:



\*\*Funding Duration\*\*



Calculated from the period between the startup's first and last funding activity. It represents how long the startup remained involved in the observed funding process.



\*\*Funding Rounds\*\*



The number of funding rounds represents the level of repeated investment activity associated with the startup.



\*\*Startup Status\*\*



Startup status provides an indication of the company's observed outcome. The implemented scoring system assigns different values to different statuses.



\*\*Acquisition Indicator\*\*



Indicates whether the startup has an acquisition event.



\* 1 → acquired

\* 0 → not acquired



\*\*IPO Indicator\*\*



Indicates whether the startup has an IPO.



\* 1 → IPO

\* 0 → no IPO



\*\*Investment Cost\*\*



The current model uses the startup's total funding amount as the investment cost. This is the amount used in the budget constraint.



The processed dataset shows `investment\_cost` alongside `funding\_total\_usd`.



\---



\## 8. Funding Band



The modelling dataset also categorizes startups according to their funding level.



The funding band provides a simplified categorical representation of investment scale, such as:



\* Low

\* Medium

\* High

\* Very High



This provides an easier way to understand the relative funding level of each startup.



\---



\## 9. Investment Potential Score



The next stage is to convert the startup characteristics into a single numerical Investment Potential Score.



The purpose is to create one measure that represents the relative attractiveness of each startup for the optimization model.



The current implementation combines four components:



\* Funding-round score

\* Funding-duration score

\* Status score

\* Outcome score



\---



\## 10. Funding-Round Score



The number of funding rounds is normalized to a 0–100 scale.



The startup with the lowest number of rounds receives a score near the lower end, while the startup with the highest number receives a score near 100.



This allows funding-round counts to be combined with other features having different numerical scales.



\---



\## 11. Funding-Duration Score



Funding duration is also normalized to a 0–100 scale.



A longer observed funding duration therefore contributes a higher normalized score.



This feature is intended to capture the persistence of the startup's funding activity.



\---



\## 12. Status Score



The implementation assigns predefined scores to startup statuses:



| Status    | Score |

|-----------|-------|

| IPO       | 100   |

| Acquired  | 90    |

| Operating | 70    |

| Closed    | 20    |



If a status does not match one of these categories, a default score of 50 is used.



These values are modelling assumptions introduced by the project rather than values directly provided by the dataset.



\---



\## 13. Outcome Score



The model uses acquisition and IPO indicators to create an additional outcome score.



The two binary indicators are combined so that successful acquisition or IPO outcomes contribute positively to the score.



This produces an outcome measure ranging from 0 to 100.



\---



\## 14. Final Investment Potential Score



The four components are combined using weighted scoring:



\* Funding rounds → 30%

\* Funding duration → 25%

\* Status → 25%

\* Startup outcome → 20%



Therefore, the Investment Potential Score represents a weighted combination of the startup's funding activity, funding persistence, current/observed status, and outcome indicators.



The resulting score is rounded to two decimal places.



This score becomes the objective value used by the Integer Programming model.



\---



\## 15. Why Do We Need a Score?



The optimization model needs a numerical value that tells it:



> How valuable is it to select this startup?



The raw dataset contains many different types of information, but the optimization model needs a consistent objective value.



Therefore:



```text

Raw startup characteristics

&#x20;       ↓

Feature engineering

&#x20;       ↓

Normalized features

&#x20;       ↓

Weighted Investment Potential Score

&#x20;       ↓

Optimization objective

```



\---



\## 16. Integer Programming



The first optimization technique is Binary Integer Programming.



The decision is:



> Should each startup be selected for the investment portfolio or not?



For every startup \*i\*, a binary decision variable is created.



\* xᵢ = 1 → startup is selected

\* xᵢ = 0 → startup is not selected



Because the decision can only be 0 or 1, this is a binary integer optimization problem.



\---



\## 17. Integer Programming Objective



The objective is to maximize the total Investment Potential Score of all selected startups.



In simple terms:



> Select the combination of startups that gives the highest total investment potential.



The model therefore considers the score of every startup and decides which combination produces the best portfolio.



\---



\## 18. Budget Constraint



The investor cannot select unlimited startups because capital is limited.



Therefore, the total investment cost of the selected startups must remain within the available budget.



Conceptually:



```text

Total cost of selected startups ≤ Available budget

```



This ensures that the resulting portfolio is financially feasible.



\---



\## 19. Optimization Scenarios



The model is solved separately for different available budgets.



The current implementation uses:



\* $25 million

\* $50 million

\* $75 million



For every budget:



1\. The optimization model is created.

2\. Binary decision variables are generated.

3\. The objective is defined.

4\. The budget constraint is applied.

5\. The CBC solver is executed.

6\. Selected startups are identified.

7\. Total investment is calculated.

8\. Total potential score is calculated.

9\. Budget utilization is calculated.

10\. Results are saved.



The implementation performs these three scenarios programmatically.



\---



\## 20. Optimization Solver



The Integer Programming model is implemented using PuLP.



The CBC solver is used to solve the optimization problem.



The solver determines the values of the binary decision variables that produce the best feasible portfolio.



\---



\## 21. Integer Programming Outputs



For every budget scenario, the system generates:



\*\*Selected Projects\*\*

The list of startups selected by the optimization model.



\*\*Total Investment\*\*

The total investment cost of all selected startups.



\*\*Budget Utilization\*\*

The percentage of the available budget that is actually used.



\*\*Total Investment Potential\*\*

The combined Investment Potential Score of the selected startups.



\*\*Solver Status\*\*

Indicates whether the optimization problem was successfully solved.



These results are saved in:



\* `results/integer\_programming\_budget\_summary.csv`

\* `results/integer\_programming\_selected\_projects.csv`



\---



\## 22. Scored Dataset Output



After calculating the Investment Potential Score, the complete scored dataset is saved as:



`data/processed/startup\_projects\_scored.csv`



This creates a reusable input for subsequent optimization models.



The important idea is that both Integer Programming and Goal Programming can work from the same structured/scored project dataset.



\---



\## 23. Goal Programming



The second optimization technique is Goal Programming.



Integer Programming currently focuses on one primary objective:



> Maximize Investment Potential.



However, real investment decisions may involve several objectives simultaneously.



For example, an investor may want:



\* High investment potential

\* Low investment risk

\* Strong strategic alignment



These objectives may conflict with each other.



A portfolio that maximizes investment potential may not necessarily minimize risk.



This is where Goal Programming is introduced.



\---



\## 24. Goal Programming Concept



Goal Programming is a multi-objective optimization technique.



Instead of asking:



> "What portfolio gives the maximum score?"



we ask:



> "What portfolio best satisfies several desired goals?"



Each goal is assigned a desired target.



The model then attempts to minimize undesirable deviations from those targets.



\---



\## 25. Proposed Goal Programming Goals



The proposed Goal Programming model will consider:



\*\*Goal 1: Investment Potential\*\*

Try to achieve a high overall Investment Potential Score.



\*\*Goal 2: Investment Risk\*\*

Try to maintain an acceptable level of investment risk. A risk score will need to be defined as part of the Goal Programming implementation.



\*\*Goal 3: Strategic Alignment\*\*

Try to ensure that the selected portfolio satisfies strategic preferences such as sector or portfolio composition.



The exact formulation of these additional goals is still part of the planned implementation.



\---



\## 26. Goal Priorities



Because multiple goals may conflict, the model needs to determine which goals are more important.



This can be done using:



\* Goal priorities

\* Weights

\* Target values



For example, the investor may prioritize investment potential more strongly than strategic alignment.



The final implementation will determine the appropriate goal structure.



\---



\## 27. Integer Programming vs Goal Programming



The two optimization methods serve different purposes.



\*\*Integer Programming\*\*



Focuses on:



> Maximum Investment Potential



while satisfying the budget.



\*\*Goal Programming\*\*



Focuses on:



> Balanced achievement of multiple investment goals



while satisfying the required constraints.



Therefore, both models can receive the same startup dataset but produce different recommended portfolios because they optimize different decision criteria.



\---



\## 28. Scenario and Sensitivity Analysis



After both optimization approaches are implemented, the project can evaluate how portfolio decisions change when model conditions change.



Possible scenarios include:



\* Different budget levels

\* Different goal priorities

\* Different target values

\* Different risk preferences

\* Different strategic preferences



The purpose is to determine whether the recommended portfolio is stable or highly sensitive to changes in assumptions.



\---



\## 29. Model Comparison



The final analysis will compare the portfolios produced by Integer Programming and Goal Programming.



Important comparison measures include:



\* Selected startups

\* Number of selected startups

\* Total investment

\* Budget utilization

\* Investment Potential Score

\* Risk level

\* Strategic alignment

\* Differences in portfolio composition



This allows the project to answer:



> Which optimization approach provides a more suitable investment portfolio for different decision-making preferences?



\---



\## 30. User Interface



The final project requires a user interface through which the user can interact with the system.



The interface should allow the user to:



\*\*Load Data\*\*

Upload or load the startup dataset.



\*\*View Statistics\*\*

Generate statistics and visualizations on demand.



\*\*Select Optimization Method\*\*

The user should be able to choose between:



\* Integer Programming

\* Goal Programming



\*\*Enter Budget\*\*

The user can specify the available investment budget.



\*\*Run Optimization\*\*

The selected optimization model is executed using the chosen parameters.



\*\*View Results\*\*

The interface displays:



\* Selected startups

\* Total investment

\* Budget utilization

\* Investment Potential Score

\* Other relevant optimization metrics



\---



\## 31. Final System Architecture



The complete system will therefore follow:



```text

Dataset

&#x20;  ↓

Data Processing

&#x20;  ↓

Feature Engineering

&#x20;  ↓

Investment Potential Scoring

&#x20;  ↓

Optimization Dataset

&#x20;  ↓

User Selects Model

&#x20;  ↙            ↘

Integer Programming   Goal Programming

&#x20;  ↘            ↙

Optimized Portfolio

&#x20;  ↓

Results \& Analysis

&#x20;  ↓

Decision Support

```



\---



\## 32. Current Implementation vs Planned Work



\### Currently Implemented



\* Raw dataset exploration

\* Startup filtering

\* 100-project modelling dataset

\* Feature engineering

\* Investment Potential Scoring

\* Binary decision variables

\* Budget constraint

\* Integer Programming objective

\* PuLP/CBC optimization

\* $25M, $50M and $75M scenarios

\* Optimization result generation

\* Scored dataset generation



The current Integer Programming code contains the mutual-exclusion and prerequisite relationships only as commented modelling assumptions, so they are not active constraints in the current execution.



\### Planned



\* Risk feature development

\* Strategic-alignment feature development

\* Goal Programming

\* IP vs GP comparison

\* Sensitivity analysis

\* Complete user interface

\* End-to-end system integration

