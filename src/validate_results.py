"""Reload artifacts; independently recompute feasibility and HiGHS optima."""
import hashlib
import json
import platform
import importlib.metadata
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint
from portfolio_model import ROOT, RESULTS, METRICS, config, load_data, validate
from integer_programming import calculate_ips
from score_projects import funding_history_risk, strategic_alignment


def independent_optimum(df, s):
    """Build a separate SciPy/HiGHS formulation from exported scenario metadata."""
    gp = s["model"] == "GP"
    n, size = len(df), len(df) + (6 if gp else 0)
    c = np.zeros(size)
    lower, upper = np.zeros(size), np.full(size, np.inf)
    upper[:n] = 1
    integrality = np.zeros(size)
    integrality[:n] = 1
    rows, lo, hi = [], [], []
    def constraint(coeff, lb=-np.inf, ub=np.inf):
        rows.append(coeff); lo.append(lb); hi.append(ub)
    cost = np.zeros(size); cost[:n] = df.investment_cost/1e6
    constraint(cost, ub=s["budget"]/1e6)
    ids = dict(zip(df.project_id, range(n)))
    logic = config()["logical_scenarios"][s["logical_scenario"]]
    for a,b in logic["prerequisites"]:
        row = np.zeros(size); row[ids[a]] = 1; row[ids[b]] = -1
        constraint(row, ub=0)
    for a,b in logic["mutual_exclusions"]:
        row = np.zeros(size); row[ids[a]] = 1; row[ids[b]] = 1
        constraint(row, ub=1)
    if gp:
        for j,(k,col) in enumerate(METRICS.items()):
            row = np.zeros(size); row[:n] = df[col]
            row[n+2*j] = 1; row[n+2*j+1] = -1
            constraint(row, lb=s[f"target_{k}"], ub=s[f"target_{k}"])
            c[n+2*j+(1 if k == "risk" else 0)] = s[f"weight_{k}"]/s[f"scale_{k}"]
    elif s["model"] == "IP":
        c[:n] = -df.investment_potential_score
    else:
        c[:n] = df.risk_score
        if s["anchor"] != "risk":
            row = np.zeros(size); row[:n] = df[METRICS[s["anchor"]]]
            constraint(row, lb=s["primary_optimum"]-1e-7)
    answer = milp(c, integrality=integrality, bounds=Bounds(lower,upper),
                  constraints=LinearConstraint(np.array(rows),lo,hi),
                  options={"mip_rel_gap":0, "time_limit":120})
    if not answer.success or answer.status != 0:
        raise RuntimeError(f"Independent HiGHS check failed: {answer.message}")
    return -answer.fun if s["model"] == "IP" else answer.fun


def main():
    df = load_data(True)
    all_checks, cross_checks = [], []
    def check(name, passed):
        all_checks.append({"model":"Dataset/artifacts", "check":name,"passed":bool(passed)})
    check("IPS_formula_preserved", np.allclose(calculate_ips(df).investment_potential_score, df.investment_potential_score, rtol=0,atol=1e-8))
    check("risk_formula_recomputed", np.allclose(funding_history_risk(df).round(6),df.risk_score,rtol=0,atol=1e-8))
    check("strategy_formula_recomputed", np.array_equal(strategic_alignment(df,config()["strategy"]),df.strategic_score))
    manifest=json.loads((ROOT/'docs/archive/pre_extension_sha256.json').read_text())
    for relative, digest in manifest.items():
        if relative.startswith(('data/raw/','notebooks/')) or relative == 'data/processed/startup_projects.csv' or relative.startswith('results/'):
            check(f"original_preserved:{relative}",hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest)
    keys = ["budget", "model", "logical_scenario", "priority"]
    for prefix in ["ip", "gp", "payoff", "gp_fixed_targets"]:
        summaries = pd.read_csv(RESULTS/f"{prefix}_summary.csv")
        decisions = pd.read_csv(RESULTS/f"{prefix}_decisions.csv")
        selected = pd.read_csv(RESULTS/f"{prefix}_selected.csv")
        check(f"{prefix}_unique_scenarios",not summaries.duplicated([k for k in keys if k in summaries]).any())
        check(f"{prefix}_all_decision_rows", len(decisions)==100*len(summaries))
        for _, s in summaries.iterrows():
            def matching(frame):
                mask = pd.Series(True,index=frame.index)
                for k in keys:
                    if k in frame:
                        mask &= frame[k]==s[k]
                return frame[mask]
            d, chosen = matching(decisions), matching(selected)
            all_checks.extend(validate(df,{"summary":s,"decisions":d}))
            expected=set(d.loc[d.x>.5,'project_id'])
            check(f"{prefix}:{s.budget}:{s.logical_scenario}:{s.get('priority','IP')}:selected_export",set(chosen.project_id)==expected and len(chosen)==len(expected))
            source = df.set_index('project_id').loc[chosen.project_id]
            exported = chosen.set_index('project_id')[source.columns]
            check(f"{prefix}:{s.budget}:{s.logical_scenario}:{s.get('priority','IP')}:selected_data",source.equals(exported))
            optimum=independent_optimum(df,s)
            gap=abs(optimum-s.objective)
            tolerance=1e-6 if s.model=='GP' else 1e-3
            cross_checks.append({"artifact":prefix,"budget":s.budget,"model":s.model,
                "logical_scenario":s.logical_scenario,"priority":s.get('priority','single_objective'),
                "cbc_objective":s.objective,"highs_objective":optimum,"absolute_difference":gap,
                "passed":gap<=tolerance})
        print(f"Validated {prefix}: {len(summaries)} portfolios",flush=True)
    cross=pd.DataFrame(cross_checks)
    cross.to_csv(RESULTS/'independent_solver_validation.csv',index=False)
    for row in cross_checks:
        all_checks.append({**row,'check':'independent_HiGHS_objective'})
    # Target provenance and cross-scenario optimization properties.
    payoff=pd.read_csv(RESULTS/'payoff_summary.csv')
    targets=pd.read_csv(RESULTS/'goal_targets.csv')
    ip=pd.read_csv(RESULTS/'ip_summary.csv')
    for _,t in targets.iterrows():
        anchors=payoff[(payoff.budget==t.budget)&(payoff.logical_scenario==t.logical_scenario)].set_index('anchor')
        for k in METRICS:
            check(f"target:{t.budget}:{t.logical_scenario}:{k}",abs(t[f'target_{k}']-anchors.loc[k,'primary_optimum'])<=1e-5)
        p=ip[(ip.budget==t.budget)&(ip.logical_scenario==t.logical_scenario)].iloc[0]
        check(f"potential_anchor_matches_IP:{t.budget}:{t.logical_scenario}",abs(t.target_potential-p.total_potential)<=1e-5)
        check(f"risk_scale_payoff:{t.budget}:{t.logical_scenario}",abs(t.scale_risk-(anchors.total_risk.max()-t.target_risk))<=1e-5)
    for scenario,g in ip.groupby('logical_scenario'):
        check(f"IP_potential_monotone_budget:{scenario}",(g.sort_values('budget').total_potential.diff().dropna()>=-1e-5).all())
    cfg_snapshot=json.loads((RESULTS/'scenario_config_snapshot.json').read_text())
    check('config_matches_run_snapshot',cfg_snapshot==config())
    report=pd.DataFrame(all_checks)
    report.to_csv(RESULTS/'validation_report.csv',index=False)
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','pulp','matplotlib','scipy']}
    metadata={'python':platform.python_version(),'platform':platform.platform(),'packages':versions,
              'input_sha256':hashlib.sha256((ROOT/'data/processed/startup_projects_scored.csv').read_bytes()).hexdigest(),
              'portfolios_validated':len(cross),'checks':len(report),'passed':int(report.passed.sum()),
              'tolerances':{'binary':1e-6,'budget_usd':.01,'totals_points':1e-5,'goal_equations_points':1e-3,'independent_GP_objective':1e-6,'independent_IP_payoff_objective':1e-3}}
    (RESULTS/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    (RESULTS/'validation_report.md').write_text(f"# Validation report\n\n{int(report.passed.sum())}/{len(report)} checks passed across {len(cross)} exported portfolios.\n\n"
        "Checks reload all 100 decisions per run; verify binary values, solver status, budget, logical pairs, totals, selected-row exports, goals, nonnegative deviations, normalized reporting and objectives.\n\n"
        "An independently constructed SciPy/HiGHS model cross-checks all 60 CBC portfolio objectives (including payoff tie-breaks and fixed-target GP). Identical project sets are not required for tied optima.\n\n"
        "Score formulas, preserved IPS, original raw/base/notebook/result artifacts, payoff targets, configuration snapshot and IP budget monotonicity are also checked.\n\n"
        "See validation_report.csv for individual checks, independent_solver_validation.csv for solver objective differences and run_metadata.json for versions, tolerances and input hash.\n")
    print(f"VALIDATION: {report.passed.sum()}/{len(report)} passed")
    if not report.passed.all():
        print(report[~report.passed].to_string(index=False))
        raise AssertionError('Validation failures')


if __name__=='__main__':
    main()
