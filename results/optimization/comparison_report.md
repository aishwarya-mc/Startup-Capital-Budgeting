# IP versus GP: observed results

Both models use identical project data and hard constraints within each named logical scenario.
IP maximizes IPS; GP minimizes weighted normalized goal shortfalls/excess.
IP deviations are evaluated after solving against the same GP targets; they are not IP constraints.
Neither formulation is intrinsically better. Risk and strategic points retain their documented limitations.

## Baseline: balanced GP versus IP

| Budget | Model | Projects | Cost USD | Utilization % | Potential | Risk points | Strategy points |
|---:|---|---:|---:|---:|---:|---:|---:|
|$25M|IP|24|24,929,310|99.72|706.67|1879.17|1125|
|$25M|GP|18|24,833,829|99.34|570.01|1337.50|1225|
|$50M|IP|34|49,980,834|99.96|968.34|2745.83|1625|
|$50M|GP|25|49,897,820|99.80|819.18|1804.17|1725|
|$75M|IP|40|74,989,291|99.99|1184.18|3141.67|1900|
|$75M|GP|30|74,862,396|99.82|1025.02|2087.50|2000|

## Trade-offs

- $25M: balanced GP selects 6 fewer projects; potential changes by -136.66, total risk by -541.67, strategy by +100 versus IP.
- $50M: balanced GP selects 9 fewer projects; potential changes by -149.16, total risk by -941.67, strategy by +100 versus IP.
- $75M: balanced GP selects 10 fewer projects; potential changes by -159.16, total risk by -1054.17, strategy by +100 versus IP.

Lower total risk partly reflects smaller portfolios, not proven safer startups or lower loss probabilities.
A larger budget expands the feasible set, but portfolios need not be nested. GP targets and normalization
are recalibrated at each budget, so GP objective values across budgets are not a common welfare scale.
The CSV tables include targets, all undesirable deviations and normalized achievement for every priority.
Solver-selected portfolios may differ among tied optima; changes in identities need not imply a unique recommendation.
