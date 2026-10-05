# Strategic Alignment Score: Decision-maker supplied strategic preference

Strategic alignment is a **Decision-maker supplied strategic preference**, not an objective industry ranking and not observed in Crunchbase. This study assumes a
hypothetical investor focused on enterprise software, with adjacent digital
markets receiving partial preference. The score is an ordinal preference rubric
treated as additive cardinal points for this scenario; equal 25-point spacing is
an assumption, not empirically estimated utility.

| Tier | Sectors | Score | Assumed strategic rationale |
|---|---|---:|---|
| Core | software, enterprise | 100 | Direct enterprise/software mandate |
| Adjacent digital | web, mobile | 75 | Related delivery channels/platforms |
| Complementary | ecommerce, hardware | 50 | Possible commerce/infrastructure fit |
| Peripheral | advertising, games_video | 25 | Digital sectors outside core mandate |
| Outside mandate | biotech, medical | 0 | Specialist life-science focus outside this hypothetical mandate |

`S_i = sector_scores[sector_i]`. No further normalization, outcomes, random
numbers or startup-specific overrides are used. Zero means outside the assumed
mandate, not poor investment quality. Sector categories are coarse and do not
establish a company's actual business fit. All companies in a sector have equal
scores, so within-sector strategic differentiation is unavailable.

Edit `strategy.sector_scores` in `config/model_config.json` and rerun
`python src/score_projects.py` and the optimization pipeline. Every observed
sector must have a finite 0-100 score; unknown sectors fail instead of receiving
an undocumented default. Goal targets must be recomputed after strategy changes.

The sector field is dataset-derived; the mapping is entirely a decision-maker
assumption. `strategic_score` is derived by applying that mapping. Total strategic
alignment is the additive `sum(S_i*x_i)`; it rewards both mandate fit and number
of aligned investments. No hard sector quota is introduced.
