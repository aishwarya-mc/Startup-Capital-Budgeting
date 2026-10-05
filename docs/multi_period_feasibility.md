# Phase 2: multi-period feasibility

The processed data has total historical funding, first/last funding dates and
calendar-year summaries. It does not have committed future cash calls, project
expenditure schedules or per-period investment requirements. The two available
raw tables describe fund raising by funds and historical IPO events, not future
startup expenditures. Historical funding-round data, even if restored, describes
past financing rather than defensible future spending requirements.

The final implemented models therefore use a **single aggregate budget**.
No Year 1/2/3 allocation is fabricated. Multi-period budgeting is omitted, and
no sector quota or minimum portfolio size is imposed. Sector composition is an
output; strategic sector preferences are soft goals, not hard sector constraints.

Validation: inspected all available CSV schemas and the preprocessing notebook;
no project-level future-period cost fields exist. No data or model changes were
needed for this phase.

## Final submission statement

Multi-period budgeting was considered in the original proposal. However, the source dataset contains historical funding information rather than defensible project-specific future annual expenditure requirements. Implementing Year-1, Year-2 and Year-3 budget constraints would therefore require unsupported cost assumptions. The final model uses single-period budget scenarios instead.
