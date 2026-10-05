"""Render academic documents from frozen outputs. Never solve or change a model.

Edit narrative templates in docs/submission_templates, then run this script.
--check verifies generated documents and the immutable submission manifest.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/optimization"
TEMPLATES = ROOT / "docs/submission_templates"


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def values():
    ip = pd.read_csv(OUT / "ip_summary.csv")
    gp = pd.read_csv(OUT / "gp_summary.csv")
    compare = pd.read_csv(OUT / "ip_vs_gp_comparison.csv")
    targets = pd.read_csv(OUT / "goal_targets.csv")
    payoff = pd.read_csv(OUT / "payoff_summary.csv")
    delta = pd.read_csv(OUT / "sensitivity_changes.csv")
    sectors = pd.read_csv(OUT / "sector_composition.csv")
    data = pd.read_csv(ROOT / "data/processed/startup_projects_scored.csv")
    cfg = json.loads((ROOT / "config/model_config.json").read_text())
    meta = json.loads((OUT / "run_metadata.json").read_text())
    base = ip[ip.logical_scenario == "baseline"].sort_values("budget")
    balanced = gp[(gp.logical_scenario == "baseline") & (gp.priority == "balanced")].sort_values("budget")
    common = compare[(compare.logical_scenario == "baseline") & compare.priority.isin(["single_objective", "balanced"])].sort_values(["budget", "model"], ascending=[True, False])
    money = lambda v: f"${v:,.0f}"
    number = lambda v: f"{v:,.2f}"
    budget = lambda v: f"${v/1e6:g}M"
    def portfolio_rows(frame, prefix=False, deviations=False):
        rows = []
        for _, r in frame.iterrows():
            row = [budget(r.budget)]
            if prefix:
                row += [r.logical_scenario, r.get("priority", r.model)]
            else:
                row += ["IP" if r.model == "IP" else "GP balanced"]
            row += [int(r.projects_selected), money(r.total_investment), f"{r.budget_utilization_percent:.2f}%",
                    number(r.total_potential), number(r.total_risk), number(r.total_strategic)]
            if deviations:
                row += [number(r[f"undesirable_{k}"]) for k in ["potential", "risk", "strategic"]]
            rows.append(row)
        return rows
    headers = ["Budget", "Model", "Projects", "Investment proxy (USD)", "Utilization", "IPS points", "Funding-History Risk Proxy points", "Strategy points"]
    result = {
        "IP_TABLE": table(headers, portfolio_rows(base)),
        "BALANCED_TABLE": table(headers, portfolio_rows(balanced)),
        "COMPARISON_TABLE": table(headers + ["P shortfall", "R excess", "S shortfall"], portfolio_rows(common, deviations=True)),
        "GP_ALL_TABLE": table(["Budget", "Logic", "Priority"] + headers[2:] + ["P shortfall", "R excess", "S shortfall"], portfolio_rows(gp.sort_values(["logical_scenario", "budget", "priority"]), prefix=True, deviations=True)),
        "IP_LOGIC_TABLE": table(["Budget", "Logic", "Model"] + headers[2:], portfolio_rows(ip.sort_values(["budget", "logical_scenario"]), prefix=True)),
        "TARGET_TABLE": table(["Budget", "Logic", "P target / scale", "R target", "S target / scale", "R payoff scale"],
            [[budget(r.budget),r.logical_scenario,number(r.target_potential),number(r.target_risk),number(r.target_strategic),f"{r.scale_risk:,.6f}"] for _,r in targets.iterrows()]),
        "PAYOFF_TABLE": table(["Budget", "Logic", "Optimized goal", "Projects", "IPS", "Funding-History Risk Proxy", "Strategy"],
            [[budget(r.budget),r.logical_scenario,r.anchor,int(r.projects_selected),number(r.total_potential),number(r.total_risk),number(r.total_strategic)] for _,r in payoff.iterrows()]),
        "WEIGHT_TABLE": table(["Priority scenario", "Potential", "Risk proxy", "Strategy"],
            [[name]+["1/3" if abs(weights[k]-1/3)<1e-12 else f"{weights[k]:.2f}" for k in ["potential","risk","strategic"]] for name,weights in cfg["gp_priorities"].items()]),
        "STRATEGY_TABLE": table(["Sector", "Strategic Alignment Score"], [[k,str(v)] for k,v in cfg["strategy"]["sector_scores"].items()]),
        "CORRELATION": f"{data.investment_potential_score.corr(data.risk_score):.4f}",
        "VALIDATION_COUNT": str(meta["checks"]), "VALIDATION_PASSED": str(meta["passed"]),
        "PORTFOLIOS": str(meta["portfolios_validated"]),
        "DATA_HASH": hashlib.sha256((ROOT/'data/processed/startup_projects_scored.csv').read_bytes()).hexdigest(),
        "IP_BRIEF": "; ".join(f"{budget(r.budget)}: {int(r.projects_selected)} projects, IPS {number(r.total_potential)}" for _,r in base.iterrows()),
        "GP_BRIEF": "; ".join(f"{budget(r.budget)}: {int(r.projects_selected)} projects, IPS {number(r.total_potential)}" for _,r in balanced.iterrows()),
        "RISK_COUNTS": "/".join(str(int(v)) for v in gp[(gp.logical_scenario=='baseline')&(gp.priority=='risk_focused')].sort_values('budget').projects_selected),
        "SLIDE_STATS": table(["Verified sample measure", "Value"], [
            ["Minimum Investment Cost Proxy", money(data.investment_cost.min())],
            ["Median Investment Cost Proxy", money(data.investment_cost.median())],
            ["Maximum Investment Cost Proxy", money(data.investment_cost.max())],
            ["Recorded acquisitions / IPOs", f"{data.acquisition.sum()} / {data.ipo.sum()}"]]),
        "SAMPLE_STATS": table(["Measure", "Verified value"], [["Projects / sectors",f"{len(data)} / {data.sector.nunique()}"],
            ["Investment proxy: minimum / median / mean / maximum", " / ".join(money(v) for v in [data.investment_cost.min(),data.investment_cost.median(),data.investment_cost.mean(),data.investment_cost.max()])],
            ["Total historical funding",money(data.investment_cost.sum())],
            ["Mean funding rounds / calendar funding duration",f"{data.funding_rounds.mean():.2f} / {data.funding_duration_years.mean():.2f} years"],
            ["IPS range / mean",f"{data.investment_potential_score.min():.2f}-{data.investment_potential_score.max():.2f} / {data.investment_potential_score.mean():.4f}"],
            ["Funding-History Risk Proxy range / mean",f"{data.risk_score.min():.2f}-{data.risk_score.max():.2f} / {data.risk_score.mean():.4f}"],
            ["Strategy range / mean",f"{data.strategic_score.min():.0f}-{data.strategic_score.max():.0f} / {data.strategic_score.mean():.2f}"],
            ["Statuses", "; ".join(f"{k}: {v}" for k,v in data.status.value_counts().items())],
            ["Recorded acquisition / IPO indicators",f"{data.acquisition.sum()} / {data.ipo.sum()}"],
            ["Missing country / founded date",f"{data.country_code.isna().sum()} / {data.founded_at.isna().sum()}"]]),
        "SECTOR_BANDS": table(["Sector", "Low", "Medium", "High", "Very High"], [[sector]+[int(v) for v in row] for sector,row in pd.crosstab(data.sector,data.funding_band)[['Low','Medium','High','Very High']].iterrows()])
    }
    differences=[]
    for b,g in common.groupby('budget'):
        a=g[g.model=='IP'].iloc[0]; z=g[g.model=='GP'].iloc[0]
        differences.append([budget(b),int(z.projects_selected-a.projects_selected)]+[f"{z[k]-a[k]:+,.2f}" for k in ['total_investment','total_potential','total_risk','total_strategic']])
    result['TRADEOFF_TABLE']=table(['Budget','Change in projects','Change in USD proxy','Change in IPS','Change in risk proxy','Change in strategy'],differences)
    def sensitivity_table(frame):
        return table(['Budget change','Model / priority','Projects change','USD proxy change','IPS change','Risk proxy change','Strategy change','Added / removed'],
            [[f"{budget(r.from_budget)} to {budget(r.to_budget)}",f"{r.from_model} / {r.to_priority}",f"{r.delta_projects_selected:+.0f}"]+
             [f"{r[k]:+,.2f}" for k in ['delta_total_investment','delta_total_potential','delta_total_risk','delta_total_strategic']]+
             [f"{r.added_count} / {r.removed_count}"] for _,r in frame.iterrows()])
    result['BUDGET_DELTAS']=sensitivity_table(delta[(delta.dimension=='budget')&(delta.from_logical_scenario=='baseline')&delta.from_priority.isin(['single_objective','balanced'])])
    result['PRIORITY_DELTAS']=sensitivity_table(delta[(delta.dimension=='priority')&(delta.from_logical_scenario=='baseline')])
    logic=delta[(delta.dimension=='logic_recalibrated')&(delta.from_model=='IP')]
    result['LOGIC_DELTAS']=sensitivity_table(logic)
    result['LOGIC_MEMBERSHIP']=table(['Budget','Added projects','Removed projects','Jaccard overlap'],[[budget(r.from_budget),r.added_projects if pd.notna(r.added_projects) else 'None',r.removed_projects if pd.notna(r.removed_projects) else 'None',f'{r.jaccard_similarity:.4f}'] for _,r in logic.iterrows()])
    composition=sectors[(sectors.budget==50000000)&(sectors.model=='GP')&(sectors.logical_scenario=='baseline')&(sectors.target_policy=='recalibrated')].pivot(index='sector',columns='priority',values='projects_selected')
    composition=composition[list(cfg['gp_priorities'])]
    result['PRIORITY_SECTORS']=table(['Sector']+list(composition.columns),[[k]+[str(int(v)) for v in row] for k,row in composition.iterrows()])
    # A worked example is evaluated from an actual existing project, not invented input.
    e=data[data.project_id=='P004'].iloc[0]
    result['SCORE_EXAMPLE']=f"P004 ({e.startup_name}) has {int(e.funding_rounds)} funding rounds, {int(e.funding_duration_years)} calendar funding years, status {e.status}, acquisition={int(e.acquisition)}, IPO={int(e.ipo)}. Its normalized rounds and duration scores are {e.rounds_score:.6f} and {e.duration_score:.6f}; status score {e.status_score:.0f}, outcome score {e.outcome_score:.0f}. Thus IPS = {e.investment_potential_score:.2f}, Funding-History Risk Proxy = {e.risk_score:.6f}, Strategic Alignment Score = {e.strategic_score:.0f}, and investment cost proxy = {money(e.investment_cost)}."
    z=balanced.iloc[0]
    result['GP_WORKED']=f"At {budget(z.budget)}, balanced GP achieves P={z.total_potential:.2f}, R={z.total_risk:.6f}, S={z.total_strategic:.0f}. Targets are P={z.target_potential:.2f}, R={z.target_risk:.0f}, S={z.target_strategic:.0f}; the risk scale is {z.scale_risk:.6f}. Undesirable deviations are dP-={z.d_potential_minus:.2f}, dR+={z.d_risk_plus:.6f}, dS-={z.d_strategic_minus:.0f}. The normalized weighted objective is {z.objective:.6f}. Other deviations are zero. Small residuals reflect solver output precision."
    result['BALANCED_DEVIATIONS']=table(['Budget','dP-','dP+','dR-','dR+','dS-','dS+','P achievement','R achievement','S achievement','GP objective'],
        [[budget(r.budget)]+[f'{r[k]:.6f}' for k in ['d_potential_minus','d_potential_plus','d_risk_minus','d_risk_plus','d_strategic_minus','d_strategic_plus','normalized_achievement_potential','normalized_achievement_risk','normalized_achievement_strategic','objective']] for _,r in balanced.iterrows()])
    result['SLIDE_IP_TABLE']=table(['Budget','Projects','Investment proxy USD','Utilization','Total IPS'],[[budget(r.budget),int(r.projects_selected),money(r.total_investment),f'{r.budget_utilization_percent:.2f}%',number(r.total_potential)] for _,r in base.iterrows()])
    result['SLIDE_GP_TABLE']=table(['Budget','Projects','IPS','Risk proxy','Strategy'],[[budget(r.budget),int(r.projects_selected),number(r.total_potential),number(r.total_risk),number(r.total_strategic)] for _,r in balanced.iterrows()])
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    frozen=json.loads((ROOT/'docs/submission_freeze.json').read_text())['protected']
    changed=[p for p,h in frozen.items() if not (ROOT/p).exists() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    if changed:
        raise AssertionError(f'Frozen model/data/results changed: {changed}')
    replacements=values()
    count=0
    for template in sorted(TEMPLATES.glob('*.md')):
        source=template.read_text(encoding='utf-8')
        def replace(match):
            return replacements[match.group(1)]
        rendered=re.sub(r'\{\{([A-Z_]+)\}\}',replace,source)
        if '{{' in rendered:
            raise AssertionError(f'Unresolved template marker in {template.name}')
        target=ROOT/('README.md' if template.name=='README.md' else f'docs/{template.name}')
        if args.check:
            if target.read_text(encoding='utf-8')!=rendered:
                raise AssertionError(f'Stale generated document: {target}')
        else:
            target.write_text(rendered,encoding='utf-8')
        count+=1
    print(f'{"Verified" if args.check else "Rendered"} {count} academic documents; {len(frozen)} frozen artifacts unchanged.')


if __name__=='__main__':
    main()
