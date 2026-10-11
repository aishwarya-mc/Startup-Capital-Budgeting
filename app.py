"""Startup Capital Budgeting Studio: interactive UI for Integer and Goal Programming.

Run with:  streamlit run app.py
"""
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import ui_engine as eng  # noqa: E402
from portfolio_model import config  # noqa: E402

st.set_page_config(page_title="Startup Capital Budgeting Studio", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------- theme
PAL = {"indigo": "#6C8CFF", "teal": "#2DD4BF", "amber": "#FBBF24", "rose": "#FB7185",
       "violet": "#A78BFA", "sky": "#38BDF8", "muted": "#8B95B0", "grid": "#222B47"}
SEQ = [PAL["indigo"], PAL["teal"], PAL["amber"], PAL["rose"], PAL["violet"], PAL["sky"],
       "#34D399", "#F472B6", "#FB923C", "#94A3B8"]
GOAL_LABEL = {"potential": "Investment potential", "risk": "Funding-history risk", "strategic": "Strategic fit"}
GOAL_COLOR = {"potential": PAL["indigo"], "risk": PAL["rose"], "strategic": PAL["teal"]}

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; max-width: 1400px;}
h1,h2,h3 {letter-spacing: -.01em;}
.hero {padding: 28px 32px; border-radius: 18px; margin-bottom: 18px;
  background: radial-gradient(1200px 300px at 0% 0%, rgba(108,140,255,.28), transparent 60%),
              radial-gradient(900px 300px at 100% 100%, rgba(45,212,191,.20), transparent 60%), #131A30;
  border: 1px solid #222B47;}
.hero h1 {margin: 0 0 6px 0; font-size: 2.1rem;}
.hero p {margin: 0; color: #9AA5C4; font-size: 1.02rem;}
.kpi {background:#131A30; border:1px solid #222B47; border-radius:14px; padding:14px 18px; height:100%;}
.kpi .l {color:#8B95B0; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em;}
.kpi .v {font-size:1.65rem; font-weight:700; margin-top:2px;}
.kpi .s {color:#8B95B0; font-size:.8rem; margin-top:2px;}
.card {background:#131A30; border:1px solid #222B47; border-radius:14px; padding:18px 20px; height:100%;}
.card h4 {margin:0 0 6px 0;}
.card p {color:#9AA5C4; margin:0; font-size:.92rem;}
.pill {display:inline-block; padding:2px 10px; border-radius:99px; font-size:.75rem; font-weight:600;
  background:rgba(45,212,191,.15); color:#2DD4BF; margin-right:6px;}
.pill.warn {background:rgba(251,113,133,.15); color:#FB7185;}
div[data-testid="stTabs"] button {font-size: 1rem; padding: 10px 18px;}
</style>
""", unsafe_allow_html=True)


def kpi(label, value, sub=""):
    return f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>'


def kpi_row(items):
    for col, it in zip(st.columns(len(items)), items):
        col.markdown(kpi(*it), unsafe_allow_html=True)


def style(fig, h=380, legend=True):
    fig.update_layout(height=h, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=40, b=10), colorway=SEQ, font=dict(color="#CBD3EA"),
                      showlegend=legend, legend=dict(orientation="h", y=-0.18, x=0))
    fig.update_xaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["grid"])
    fig.update_yaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["grid"])
    return fig


def usd(v):
    return f"${v / 1e6:,.2f}M"


# ----------------------------------------------------------------------------- state / data
CFG = config()
DEFAULT_SECTOR = CFG["strategy"]["sector_scores"]
PRESETS = CFG["gp_priorities"]

if "source" not in st.session_state:
    st.session_state.source = "default"
    st.session_state.raw = eng.default_data()
    st.session_state.name = "Crunchbase sample: 100 startup projects"


def load_upload(file):
    try:
        raw = pd.read_csv(file)
        eng.prepare(raw, {s: 0 for s in raw.get("sector", pd.Series(dtype=str)).unique()}
                    if "strategic_score" not in raw else None)
        st.session_state.raw = raw
        st.session_state.name = f"Uploaded: {file.name}"
        st.session_state.source = "upload"
        st.session_state.pop("results", None)
        st.session_state.pop("stats_on", None)
        return None
    except Exception as e:  # shown to the user
        return str(e)


@st.cache_data(show_spinner=False)
def cached_ip(df, budget, pre, exc, objective):
    return eng.run_ip(df, budget, pre, exc, objective)


@st.cache_data(show_spinner=False)
def cached_targets(df, budget, pre, exc):
    return eng.payoff_targets(df, budget, pre, exc)


@st.cache_data(show_spinner=False)
def cached_gp(df, budget, weights, pre, exc):
    w = dict(weights)
    t, s = cached_targets(df, budget, pre, exc)
    return eng.run_gp(df, budget, w, pre, exc, t, s)


def achievement(df_sel, targets, scales):
    """Normalised 0-100 achievement of the three goals for any selection (same definition as GP)."""
    return {"potential": 100 * df_sel.investment_potential_score.sum() / targets["potential"],
            "strategic": 100 * df_sel.strategic_score.sum() / targets["strategic"],
            "risk": 100 * (1 - df_sel.risk_score.sum() / scales["risk"])}


# ----------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 📈 Capital Budgeting Studio")
    st.caption("Integer Programming  ·  Goal Programming")
    st.divider()
    st.markdown("**1 · Dataset**")
    up = st.file_uploader("Upload a project CSV", type="csv", label_visibility="collapsed")
    if up is not None and st.session_state.get("last_upload") != up.name:
        err = load_upload(up)
        st.session_state.last_upload = up.name
        if err:
            st.error(err)
    if st.session_state.source == "upload" and st.button("↩ Back to sample dataset", width="stretch"):
        st.session_state.source = "default"
        st.session_state.raw = eng.default_data()
        st.session_state.name = "Crunchbase sample: 100 startup projects"
        st.session_state.last_upload = None
        st.rerun()
    st.caption(f"Active: **{st.session_state.name}**")

    raw = st.session_state.raw
    sectors = sorted(raw.sector.dropna().unique()) if "sector" in raw else []
    with st.expander("Strategic preference by sector (0–100)"):
        st.caption("Decision-maker input. Drives the *strategic fit* score.")
        sector_scores = {s: st.slider(s, 0, 100, int(DEFAULT_SECTOR.get(s, 50)), 5, key=f"sec_{s}") for s in sectors}

    try:
        DF, NOTES = eng.prepare(raw, sector_scores if sectors else None)
    except Exception as e:
        st.error(f"Dataset problem: {e}")
        st.stop()

    st.markdown("**2 · Budget**")
    total = float(DF.investment_cost.sum())
    hi = int(max(10, np.ceil(total / 1e6)))
    BUDGET = st.slider("Capital budget ($M)", 1, min(hi, 400), min(50, hi), 1) * 1e6
    st.caption(f"Portfolio universe costs {usd(total)} in total.")

    st.markdown("**3 · Logical constraints**")
    logic_mode = st.radio("Scenario", ["None", "Assumed (from config)", "Custom"], label_visibility="collapsed")
    PRE, EXC = (), ()
    ids = list(DF.project_id)
    label = dict(zip(DF.project_id, DF.project_id + " · " + DF.startup_name.astype(str)))
    if logic_mode.startswith("Assumed"):
        sc = CFG["logical_scenarios"]["assumed_logic"]
        PRE = tuple(tuple(p) for p in sc["prerequisites"] if set(p) <= set(ids))
        EXC = tuple(tuple(p) for p in sc["mutual_exclusions"] if set(p) <= set(ids))
        st.caption("P005 requires P004 · P003 and P004 are mutually exclusive.")
    elif logic_mode == "Custom":
        base = pd.DataFrame({"rule": pd.Series(dtype=str), "project A": pd.Series(dtype=str), "project B": pd.Series(dtype=str)})
        ed = st.data_editor(base, num_rows="dynamic", hide_index=True, key="logic_editor", width="stretch",
                            column_config={"rule": st.column_config.SelectboxColumn("rule", options=["A requires B", "A excludes B"]),
                                           "project A": st.column_config.SelectboxColumn("A", options=ids),
                                           "project B": st.column_config.SelectboxColumn("B", options=ids)})
        ok = ed.dropna()
        ok = ok[ok["project A"] != ok["project B"]]
        PRE = tuple((a, b) for r, a, b in zip(ok.rule, ok["project A"], ok["project B"]) if r == "A requires B")
        EXC = tuple((a, b) for r, a, b in zip(ok.rule, ok["project A"], ok["project B"]) if r == "A excludes B")
        st.caption(f"{len(PRE)} prerequisite · {len(EXC)} exclusion rule(s)")
    st.divider()
    st.caption("Solver: PuLP + CBC, proven-optimal MIP (gap 0).")

# ----------------------------------------------------------------------------- header
st.markdown(f"""<div class="hero"><h1>Startup Capital Budgeting Studio</h1>
<p>Choose which startups to fund under a fixed budget. Explore the data, run <b>Integer Programming</b> or
<b>Goal Programming</b>, and compare the trade-offs interactively.</p></div>""", unsafe_allow_html=True)

t_home, t_data, t_stats, t_opt, t_cmp, t_method = st.tabs(
    ["🏠 Overview", "🗂 Data", "📊 Statistics", "⚙️ Optimize", "⚖️ Compare & Explore", "📘 Methodology"])

# ----------------------------------------------------------------------------- overview
with t_home:
    kpi_row([("Projects", f"{len(DF)}", f"{DF.sector.nunique()} sectors"),
             ("Universe cost", usd(total), f"median {usd(DF.investment_cost.median())}"),
             ("Budget", usd(BUDGET), f"{100 * BUDGET / total:.1f}% of universe"),
             ("Logic rules", f"{len(PRE) + len(EXC)}", logic_mode)])
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="card"><h4>① Load</h4><p>Use the bundled 100-project Crunchbase sample or upload your own CSV. '
                'Missing scores are computed with the project formulas.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="card"><h4>② Explore</h4><p>Generate statistics on demand: distributions, sector '
                'profiles, correlations and cost-versus-potential maps.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="card"><h4>③ Optimize</h4><p>Maximise a single score with <b>Integer Programming</b>, '
                'or balance three goals with <b>Goal Programming</b>, then compare.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Reference results from the frozen submission")
    ref = pd.read_csv(ROOT / "results/optimization/ip_vs_gp_comparison.csv")
    scen = st.radio("Logic scenario", ["baseline", "assumed_logic"], horizontal=True)
    ref = ref[ref.logical_scenario == scen]
    ref = ref.assign(**{"budget ($M)": ref.budget / 1e6, "investment ($M)": ref.total_investment / 1e6})
    ref = ref[["budget ($M)", "model", "priority", "projects_selected", "investment ($M)", "total_potential",
               "total_risk", "total_strategic", "solver_status"]].round(2)
    st.dataframe(ref, width="stretch", hide_index=True, height=300)
    st.caption("Baseline numbers produced by the batch scripts in `src/`. The live optimizer on this page reproduces them "
               "when the sample dataset, default sector scores and no logic rules are used.")

# ----------------------------------------------------------------------------- data
with t_data:
    st.subheader("Project data")
    for n in NOTES:
        st.info(n)
    f1, f2, f3 = st.columns([2, 2, 3])
    sel_sec = f1.multiselect("Sector", sectors, placeholder="All sectors")
    sel_stat = f2.multiselect("Status", sorted(DF.status.dropna().unique()) if "status" in DF else [], placeholder="All statuses")
    q = f3.text_input("Search name or ID")
    view = DF
    if sel_sec:
        view = view[view.sector.isin(sel_sec)]
    if sel_stat:
        view = view[view.status.isin(sel_stat)]
    if q:
        view = view[view.startup_name.astype(str).str.contains(q, case=False) | view.project_id.str.contains(q, case=False)]
    show = ["project_id", "startup_name", "sector", "status", "country_code", "funding_rounds", "investment_cost",
            "investment_potential_score", "risk_score", "strategic_score"]
    show = [c for c in show if c in view]
    st.dataframe(view[show], width="stretch", hide_index=True, height=430,
                 column_config={"investment_cost": st.column_config.NumberColumn("cost (USD)", format="$%d"),
                                "investment_potential_score": st.column_config.ProgressColumn("potential", min_value=0, max_value=100, format="%.1f"),
                                "risk_score": st.column_config.ProgressColumn("risk proxy", min_value=0, max_value=100, format="%.1f"),
                                "strategic_score": st.column_config.ProgressColumn("strategic", min_value=0, max_value=100, format="%.0f")})
    d1, d2 = st.columns(2)
    d1.download_button("⬇ Download current table (CSV)", DF.to_csv(index=False), "projects.csv", "text/csv", width="stretch")
    d2.download_button("⬇ Download upload template", eng.default_data().head(5).to_csv(index=False),
                       "template.csv", "text/csv", width="stretch")
    with st.expander("Required columns for an uploaded CSV"):
        st.markdown("""
- **Always:** `project_id` (unique), `startup_name`, `sector`, `investment_cost` (> 0)
- **Scores:** either `investment_potential_score` and `risk_score` (0–100), **or** `funding_rounds`, `funding_duration_years`,
  `status` (and optional `acquisition`, `ipo`) so they can be computed
- **Strategic fit:** computed from the sector sliders in the sidebar""")

# ----------------------------------------------------------------------------- statistics
with t_stats:
    st.subheader("Descriptive statistics on demand")
    opts = ["Summary table", "Distributions", "Sector profile", "Correlations", "Cost vs potential map", "Status & funding mix", "Top / bottom projects"]
    pick = st.multiselect("Choose analyses", opts, default=opts[:3])
    if st.button("▶ Generate statistics", type="primary"):
        st.session_state.stats_on = pick
    shown = st.session_state.get("stats_on")
    if not shown:
        st.info("Select analyses and press **Generate statistics**.")
    else:
        num = [c for c in ["investment_cost", "investment_potential_score", "risk_score", "strategic_score",
                           "funding_rounds", "funding_duration_years"] if c in DF]
        if "Summary table" in shown:
            st.markdown("#### Summary")
            kpi_row([("Mean cost", usd(DF.investment_cost.mean()), ""), ("Median cost", usd(DF.investment_cost.median()), ""),
                     ("Mean potential", f"{DF.investment_potential_score.mean():.1f}", "score 0–100"),
                     ("Mean risk proxy", f"{DF.risk_score.mean():.1f}", "score 0–100")])
            st.dataframe(DF[num].describe().T.round(2), width="stretch")
        if "Distributions" in shown:
            st.markdown("#### Distributions")
            c1, c2 = st.columns(2)
            logx = DF.investment_cost.gt(0)
            f = px.histogram(DF, x=np.log10(DF.investment_cost), nbins=25, color_discrete_sequence=[PAL["indigo"]])
            f.update_layout(title="Investment cost (log10 USD)", xaxis_title="log10(cost)", yaxis_title="projects")
            c1.plotly_chart(style(f, legend=False), width="stretch")
            f = px.histogram(DF, x="investment_potential_score", nbins=20, color_discrete_sequence=[PAL["teal"]], marginal="box")
            f.update_layout(title="Investment potential score")
            c2.plotly_chart(style(f, legend=False), width="stretch")
        if "Sector profile" in shown:
            st.markdown("#### Sector profile")
            g = DF.groupby("sector").agg(projects=("project_id", "count"), cost=("investment_cost", "sum"),
                                         potential=("investment_potential_score", "mean"), risk=("risk_score", "mean"),
                                         strategic=("strategic_score", "mean")).reset_index()
            c1, c2 = st.columns(2)
            f = px.bar(g.sort_values("cost"), x="cost", y="sector", orientation="h", color_discrete_sequence=[PAL["indigo"]])
            f.update_layout(title="Total cost by sector (USD)")
            c1.plotly_chart(style(f, legend=False), width="stretch")
            m = g.melt("sector", ["potential", "risk", "strategic"], "metric", "mean score")
            f = px.bar(m, x="sector", y="mean score", color="metric", barmode="group",
                       color_discrete_map={k: GOAL_COLOR[k] for k in GOAL_COLOR})
            f.update_layout(title="Mean scores by sector")
            c2.plotly_chart(style(f), width="stretch")
        if "Correlations" in shown:
            st.markdown("#### Correlation matrix")
            cm = DF[num].corr().round(2)
            f = px.imshow(cm, text_auto=True, color_continuous_scale=[[0, PAL["rose"]], [.5, "#131A30"], [1, PAL["teal"]]],
                          zmin=-1, zmax=1, aspect="auto")
            st.plotly_chart(style(f, 420, legend=False), width="stretch")
            if {"investment_potential_score", "risk_score"} <= set(cm):
                st.caption(f"Potential and risk proxy correlate at **{cm.loc['investment_potential_score', 'risk_score']:.2f}**: "
                           "both are derived from funding history, so the goals conflict by construction.")
        if "Cost vs potential map" in shown:
            st.markdown("#### Cost vs potential")
            f = px.scatter(DF, x="investment_cost", y="investment_potential_score", color="sector", log_x=True,
                           size=DF.strategic_score + 8, hover_name="startup_name",
                           hover_data=["project_id", "status", "risk_score"], color_discrete_sequence=SEQ)
            f.update_layout(xaxis_title="Cost (USD, log)", yaxis_title="Potential score")
            st.plotly_chart(style(f, 460), width="stretch")
        if "Status & funding mix" in shown:
            st.markdown("#### Status & funding mix")
            c1, c2 = st.columns(2)
            if "status" in DF:
                s = DF.status.value_counts().reset_index()
                f = px.pie(s, names="status", values="count", hole=.55, color_discrete_sequence=SEQ)
                f.update_layout(title="Company status")
                c1.plotly_chart(style(f), width="stretch")
            if "funding_band" in DF:
                s = DF.funding_band.value_counts().reset_index()
                f = px.bar(s, x="funding_band", y="count", color_discrete_sequence=[PAL["amber"]])
                f.update_layout(title="Funding band")
                c2.plotly_chart(style(f, legend=False), width="stretch")
        if "Top / bottom projects" in shown:
            st.markdown("#### Efficiency: potential per $1M invested")
            e = DF.assign(potential_per_musd=DF.investment_potential_score / (DF.investment_cost / 1e6))
            cols = ["project_id", "startup_name", "sector", "investment_cost", "investment_potential_score", "potential_per_musd"]
            c1, c2 = st.columns(2)
            c1.caption("Most efficient")
            c1.dataframe(e.nlargest(10, "potential_per_musd")[cols], hide_index=True, width="stretch")
            c2.caption("Least efficient")
            c2.dataframe(e.nsmallest(10, "potential_per_musd")[cols], hide_index=True, width="stretch")


# ----------------------------------------------------------------------------- optimize
def render_result(out, sel, goals=None, tag=""):
    kpi_row([("Status", out["status"], "proven optimal" if out["status"] == "Optimal" else ""),
             ("Projects funded", f"{out['projects']}", f"of {len(DF)}"),
             ("Investment", usd(out["investment"]), f"{out['utilization_pct']:.2f}% of budget"),
             ("Potential", f"{out['potential']:,.1f}", "total score"),
             ("Risk proxy", f"{out['risk']:,.1f}", "lower is better"),
             ("Strategic fit", f"{out['strategic']:,.0f}", "total score")])
    bad = eng.logic_ok(DF, sel, PRE, EXC)
    st.markdown((f'<span class="pill warn">logic violated: {bad}</span>' if bad else
                 '<span class="pill">budget ✓</span><span class="pill">binary ✓</span><span class="pill">logic ✓</span>'),
                unsafe_allow_html=True)
    g1, g2 = st.columns([1, 1])
    fig = go.Figure(go.Indicator(mode="gauge+number", value=out["utilization_pct"], number={"suffix": "%", "valueformat": ".1f", "font": {"size": 34}},
                                 title={"text": "Budget utilisation", "font": {"size": 15}},
                                 gauge={"axis": {"range": [0, 100]}, "bar": {"color": PAL["indigo"]},
                                        "bgcolor": "#131A30", "borderwidth": 0}))
    g1.plotly_chart(style(fig, 300, False), width="stretch", key=f"gauge{tag}")
    if goals is not None:
        gg = goals.assign(label=goals.goal.map(GOAL_LABEL))
        f = px.bar(gg, x="achievement_pct", y="label", orientation="h", color="goal", color_discrete_map=GOAL_COLOR,
                   text=gg.achievement_pct.map("{:.1f}%".format))
        f.update_layout(title="Goal achievement (100% = ideal)", xaxis=dict(range=[0, 105]), yaxis_title="", xaxis_title="")
        g2.plotly_chart(style(f, 300, False), width="stretch", key=f"goals{tag}")
    else:
        by = sel.groupby("sector").investment_cost.sum().reset_index()
        f = px.pie(by, names="sector", values="investment_cost", hole=.55, color_discrete_sequence=SEQ)
        f.update_traces(textinfo="percent", textposition="inside")
        f.update_layout(title="Capital by sector", uniformtext_minsize=9, uniformtext_mode="hide")
        g2.plotly_chart(style(f, 300), width="stretch", key=f"pie{tag}")
    chosen = DF.project_id.isin(sel.project_id)
    f = px.scatter(DF.assign(decision=np.where(chosen, "Funded", "Not funded")), x="investment_cost",
                   y="investment_potential_score", color="decision", log_x=True, hover_name="startup_name",
                   hover_data=["project_id", "sector", "risk_score", "strategic_score"],
                   color_discrete_map={"Funded": PAL["teal"], "Not funded": "#3A4468"})
    f.update_layout(title="Which projects were funded", xaxis_title="Cost (USD, log)", yaxis_title="Potential")
    st.plotly_chart(style(f, 400), width="stretch", key=f"map{tag}")
    st.markdown("**Selected portfolio**")
    cols = [c for c in ["project_id", "startup_name", "sector", "status", "investment_cost", "investment_potential_score",
                        "risk_score", "strategic_score"] if c in sel]
    st.dataframe(sel[cols].sort_values("investment_potential_score", ascending=False), hide_index=True,
                 width="stretch", height=320)
    st.download_button("⬇ Download portfolio (CSV)", sel[cols].to_csv(index=False), f"portfolio_{tag}.csv", "text/csv", key=f"dl{tag}")


with t_opt:
    st.subheader("Run an optimisation")
    method = st.radio("Technique", ["Integer Programming", "Goal Programming"], horizontal=True)
    if method == "Integer Programming":
        st.markdown("Select projects (binary decisions) to **optimise one score** subject to the budget"
                    + (" and logic rules." if PRE or EXC else "."))
        objective = st.selectbox("Objective", ["potential", "strategic", "risk"],
                                 format_func=lambda k: {"potential": "Maximise investment potential",
                                                        "strategic": "Maximise strategic fit",
                                                        "risk": "Minimise risk proxy (note: trivial empty portfolio)"}[k])
        if st.button("▶ Solve with Integer Programming", type="primary"):
            with st.spinner("Solving…"):
                out, sel = cached_ip(DF, BUDGET, PRE, EXC, objective)
            st.session_state.results = ("ip", out, sel, None)
    else:
        st.markdown("**Trade off three goals** by weighting them. Each goal has an ideal target from a single-objective "
                    "optimum; GP minimises weighted normalised shortfall.")
        pc = st.columns(len(PRESETS))
        for col, (name, w) in zip(pc, PRESETS.items()):
            def setp(w=w):
                for k in ("potential", "risk", "strategic"):
                    st.session_state[f"w_{k}"] = int(round(w[k] * 100))
            col.button(name.replace("_", " ").title(), on_click=setp, width="stretch")
        w1, w2, w3 = st.columns(3)
        wts = {"potential": w1.slider("Potential weight", 0, 100, 33, key="w_potential"),
               "risk": w2.slider("Risk-reduction weight", 0, 100, 33, key="w_risk"),
               "strategic": w3.slider("Strategic-fit weight", 0, 100, 33, key="w_strategic")}
        if sum(wts.values()) == 0:
            st.warning("Give at least one goal a positive weight.")
        elif st.button("▶ Solve with Goal Programming", type="primary"):
            with st.spinner("Solving payoff table and goal program…"):
                out, sel, goals = cached_gp(DF, BUDGET, tuple(sorted(wts.items())), PRE, EXC)
            st.session_state.results = ("gp", out, sel, goals)
    res = st.session_state.get("results")
    if res:
        kind, out, sel, goals = res
        st.divider()
        st.markdown(f"### Result · {out['model']} · budget {usd(out['budget'])}")
        if abs(out["budget"] - BUDGET) > 1:
            st.warning("The budget slider changed after this run. Press Solve again to refresh.")
        if goals is not None:
            st.caption("Weights used: " + ", ".join(f"{GOAL_LABEL[k]} {v:.0%}" for k, v in out["weights"].items()))
        render_result(out, sel, goals, kind)

# ----------------------------------------------------------------------------- compare
with t_cmp:
    st.subheader("Compare techniques and explore trade-offs")
    sub = st.radio("View", ["IP vs GP at this budget", "Budget sweep", "Trade-off explorer"], horizontal=True)
    if sub == "IP vs GP at this budget":
        ip, ip_sel = cached_ip(DF, BUDGET, PRE, EXC, "potential")
        targets, scales = cached_targets(DF, BUDGET, PRE, EXC)
        rows, sels = [("Integer Programming", ip, ip_sel)], {"Integer Programming": ip_sel}
        for name, w in PRESETS.items():
            o, s, _ = cached_gp(DF, BUDGET, tuple(sorted(w.items())), PRE, EXC)
            rows.append((f"GP · {name.replace('_', ' ')}", o, s))
            sels[f"GP · {name.replace('_', ' ')}"] = s
        tab = pd.DataFrame([{"Model": n, "Projects": o["projects"], "Investment ($M)": o["investment"] / 1e6,
                             "Potential": o["potential"], "Risk proxy": o["risk"], "Strategic": o["strategic"]}
                            for n, o, _ in rows])
        st.dataframe(tab.round(2), hide_index=True, width="stretch")
        c1, c2 = st.columns(2)
        rad = go.Figure()
        for i, (n, o, s) in enumerate(rows):
            a = achievement(s, targets, scales)
            r = [a["potential"], a["strategic"], a["risk"], a["potential"]]
            rad.add_trace(go.Scatterpolar(r=r, theta=["Potential", "Strategic fit", "Risk control", "Potential"],
                                          name=n, line=dict(color=SEQ[i % len(SEQ)])))
        rad.update_layout(title="Goal achievement (% of ideal)", polar=dict(radialaxis=dict(range=[0, 100], gridcolor=PAL["grid"]),
                                                                            bgcolor="rgba(0,0,0,0)"))
        c1.plotly_chart(style(rad, 430), width="stretch")
        names = list(sels)
        sets = {n: set(sels[n].project_id) for n in names}
        jac = pd.DataFrame([[len(sets[a] & sets[b]) / max(1, len(sets[a] | sets[b])) for b in names] for a in names],
                           index=names, columns=names)
        f = px.imshow(jac.round(2), text_auto=True, color_continuous_scale=[[0, "#131A30"], [1, PAL["indigo"]]], zmin=0, zmax=1)
        f.update_layout(title="Portfolio overlap (Jaccard)")
        c2.plotly_chart(style(f, 430, False), width="stretch")
        mix = pd.concat([s.assign(model=n).groupby(["model", "sector"]).investment_cost.sum().reset_index() for n, s in sels.items()])
        f = px.bar(mix, x="model", y="investment_cost", color="sector", color_discrete_sequence=SEQ)
        f.update_layout(title="Capital allocated by sector", xaxis_title="", yaxis_title="USD")
        st.plotly_chart(style(f, 420), width="stretch")
    elif sub == "Budget sweep":
        lo, hi2 = st.slider("Budget range ($M)", 5, int(min(hi, 400)), (10, int(min(hi, 150))), 5)
        steps = st.slider("Points", 4, 14, 8)
        bal = tuple(sorted({"potential": 1 / 3, "risk": 1 / 3, "strategic": 1 / 3}.items()))
        if st.button("▶ Run sweep", type="primary"):
            rows = []
            prog = st.progress(0.0)
            bs = np.linspace(lo, hi2, steps) * 1e6
            for i, b in enumerate(bs):
                o, _ = cached_ip(DF, float(b), PRE, EXC, "potential")
                g, _, _ = cached_gp(DF, float(b), bal, PRE, EXC)
                for n, r in (("Integer Programming", o), ("Goal Programming (balanced)", g)):
                    rows.append({"budget_m": b / 1e6, "model": n, "potential": r["potential"], "risk": r["risk"],
                                 "strategic": r["strategic"], "projects": r["projects"]})
                prog.progress((i + 1) / len(bs))
            st.session_state.sweep = pd.DataFrame(rows)
        sw = st.session_state.get("sweep")
        if sw is not None:
            cols = st.columns(2)
            for (m, lab), col in zip([("potential", "Total potential"), ("risk", "Total risk proxy"),
                                      ("strategic", "Total strategic fit"), ("projects", "Projects funded")], cols * 2):
                f = px.line(sw, x="budget_m", y=m, color="model", markers=True, color_discrete_sequence=[PAL["indigo"], PAL["teal"]])
                f.update_layout(title=lab, xaxis_title="Budget ($M)", yaxis_title="")
                col.plotly_chart(style(f, 330), width="stretch")
            ipx = sw[sw.model == "Integer Programming"].reset_index(drop=True)
            marg = (ipx.potential.diff() / ipx.budget_m.diff()).dropna()
            st.caption(f"Marginal return of the IP: **{marg.iloc[0]:.1f}** potential per extra $1M at the low end, "
                       f"falling to **{marg.iloc[-1]:.1f}** at the high end (diminishing returns).")
            st.download_button("⬇ Download sweep (CSV)", sw.to_csv(index=False), "budget_sweep.csv", "text/csv")
    else:
        st.markdown("Slide the **potential weight** from 0 to 100% (remaining weight split between risk and strategy) to "
                    "trace the Goal-Programming trade-off curve.")
        n = st.slider("Resolution", 5, 15, 9)
        if st.button("▶ Trace trade-off curve", type="primary"):
            pts = []
            prog = st.progress(0.0)
            for i, p in enumerate(np.linspace(0, 1, n)):
                w = tuple(sorted({"potential": p, "risk": (1 - p) / 2, "strategic": (1 - p) / 2}.items()))
                o, _, _ = cached_gp(DF, BUDGET, w, PRE, EXC)
                pts.append({"potential_weight": p, "potential": o["potential"], "risk": o["risk"],
                            "strategic": o["strategic"], "projects": o["projects"]})
                prog.progress((i + 1) / n)
            st.session_state.tradeoff = pd.DataFrame(pts)
        tr = st.session_state.get("tradeoff")
        if tr is not None:
            c1, c2 = st.columns(2)
            f = go.Figure()
            for k in ("potential", "risk", "strategic"):
                f.add_trace(go.Scatter(x=tr.potential_weight, y=tr[k] / tr[k].max() * 100, mode="lines+markers",
                                       name=GOAL_LABEL[k], line=dict(color=GOAL_COLOR[k])))
            f.update_layout(title="Goal totals (indexed to own max = 100)", xaxis_title="Weight on potential", yaxis_title="index")
            c1.plotly_chart(style(f, 400), width="stretch")
            f = px.scatter(tr, x="risk", y="potential", color="strategic", size="projects", color_continuous_scale="Viridis",
                           hover_data=["potential_weight"])
            f.update_traces(mode="lines+markers")
            f.update_layout(title="Potential vs risk frontier (colour = strategic fit)", xaxis_title="Risk proxy (lower better)")
            c2.plotly_chart(style(f, 400, False), width="stretch")
            st.dataframe(tr.round(3), hide_index=True, width="stretch")

# ----------------------------------------------------------------------------- methodology
with t_method:
    st.subheader("Models implemented")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Integer Programming (0–1 knapsack)")
        st.latex(r"\max \sum_i s_i x_i \quad \text{s.t.}\quad \sum_i c_i x_i \le B,\; x_i \in \{0,1\}")
        st.latex(r"x_a \le x_b \;(\text{a requires b}),\qquad x_a + x_b \le 1 \;(\text{exclusion})")
        st.markdown("`s_i` = chosen score (default: investment potential), `c_i` = investment cost, `B` = budget.")
    with c2:
        st.markdown("#### Goal Programming (linear weighted)")
        st.latex(r"\min\; w_P\frac{d_P^-}{S_P}+w_R\frac{d_R^+}{S_R}+w_S\frac{d_S^-}{S_S}")
        st.latex(r"\sum_i p_i x_i + d_P^- - d_P^+ = T_P \quad (\text{similarly } R, S)")
        st.markdown("Targets `T` are the single-objective ideals (risk ideal = 0). Scales `S` normalise goals to comparable units. "
                    "Only *undesirable* deviations are penalised.")
    st.markdown("""
#### Scores
| Score | Definition |
|---|---|
| Investment potential | .30·N(rounds) + .25·N(duration) + .25·status score + .20·outcome score |
| Funding-history risk proxy | .50·(100−N(rounds)) + .50·(100−N(duration)) — a proxy, **not** failure probability |
| Strategic fit | Decision-maker preference for the project's sector (sidebar sliders) |

*N(·)* is min–max normalisation to 0–100. Status scores: IPO 100, acquired 90, operating 70, closed 20.

#### Honest limitations
Potential and the risk proxy are strongly negatively correlated because both derive from funding history. Strategic scores and logic
rules are hypothetical decision-maker inputs, not facts from the dataset. Full derivations are in `docs/methodology.md`.
""")
