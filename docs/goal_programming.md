# Weighted linear goal programming

Same original 100 projects, binary decisions and cost proxy as IP. Hard
constraints are budget `sum(C_i*x_i)<=B`, binary x, and only the logical pairs
enabled in the named configuration. No minimum spending, portfolio-size floor,
sector quota or multi-period costs are introduced.

Let P, R, S be portfolio sums of IPS, Funding-History Risk Proxy and strategic points.
All coefficients are fixed before optimization. For each goal:

```
P + dP_minus - dP_plus = P_target
R + dR_minus - dR_plus = R_target
S + dS_minus - dS_plus = S_target
all deviations >= 0
```

Undesirable deviations are potential shortfall dP_minus, risk excess dR_plus,
and strategic shortfall dS_minus. Minimize the **sum of positive penalties**:

`wP*dP_minus/P_scale + wR*dR_plus/R_scale + wS*dS_minus/S_scale`.

Negative signs on excess-risk or strategy-shortfall penalties would reward
undesirable deviations and can make the deviation formulation unbounded. They
are therefore not used. There are no products of variables or portfolio-average
ratios. Budget remains hard; all three targets are soft goals. Weights are
compensatory preferences, **not lexicographic priority levels**.

## Targets and normalization: payoff method
For each budget and logical configuration independently, optimize:
1. Maximum total potential; among potential optima minimize total risk.
2. Minimum total risk.
3. Maximum total strategy; among strategy optima minimize total risk.

The resulting 3-by-3 payoff table reports all three achieved measures for each
anchor. Individual best values define ideal targets P_target, R_target,
S_target. These are optimization-derived aspirations conditional on the sample
and scenario, not observed investor targets and not necessarily jointly feasible.

All project risk scores are positive. With no minimum-investment requirement,
the minimum-risk solution is the **empty portfolio**, giving R_target=0. This
is a valid consequence of the authorized hard constraints, not an error to hide
by imposing an arbitrary return floor. In particular, strong risk weights may
produce a small or empty portfolio; this must be reported, not filtered out.

P_scale=P_target, S_scale=S_target. Dividing by the zero risk target is invalid,
so R_scale is the largest risk among the payoff anchors minus R_target. This is
a positive payoff-range normalization in risk-score points. It is not a hard
risk cap or the maximum risk of every feasible portfolio. Degenerate zero scales
raise an explanatory error rather than silently choosing a denominator.

Targets/scales are shared across all four priority scenarios for a given budget
and logical configuration. Changing constraints recomputes the payoff table.
Logical sensitivity also includes GP runs with **baseline targets held fixed**
to distinguish constraint effects from recalibration effects.

## Weight scenarios
| Scenario | Potential | Risk | Strategy |
|---|---:|---:|---:|
| balanced | 1/3 | 1/3 | 1/3 |
| potential_focused | .60 | .20 | .20 |
| risk_focused | .20 | .60 | .20 |
| strategy_focused | .20 | .20 | .60 |

These are explicitly chosen scenario assumptions in config/model_config.json.
They illustrate trade-offs, not empirically justified or recommended preferences.
No weights multiply the hard budget.

Normalized undesirable deviation is `bad_deviation/scale`; the reported
achievement index is `1-bad_deviation/scale`. A value of 1 means goal met. Risk
achievement uses the payoff range, **not achieved risk divided by zero**. Values
can be negative if deviation exceeds the reference scale; they are not clipped
or presented as probabilities. All six deviation variables are exported.

Risk is additive exposure in score-points, not portfolio variance or average
risk. This choice creates a portfolio-size trade-off against additive potential
and strategy. The documented proxy is not independent of IPS history components.

## Execution and validation
`python src/goal_programming.py` saves GP/anchor summary, all 100 decisions per
run, selected projects, targets/scales, configuration snapshot and validations.
PuLP/CBC must prove an optimal solution (both problem and solution status);
time-limited feasible solutions are not accepted as optimal. Costs are scaled
to millions inside constraints without rounding original dollar inputs.
Binary/budget/logical/total checks run on every solution. GP also verifies each
goal equation, nonnegative deviations and recomputed weighted objective.

For the submission, use the complete [methodology](methodology.md), including all six deviation definitions and the generated target table. Throughout this technical note, risk means Funding-History Risk Proxy, not direct financial risk.
