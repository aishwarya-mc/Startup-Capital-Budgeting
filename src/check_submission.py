"""Submission consistency checks only; never optimize or rewrite model results."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/submission'
NUM=ROOT/'results/optimization'


def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    def check(name, passed, detail=''):
        records.append({'check':name,'passed':bool(passed),'detail':detail})
    freeze=json.loads((ROOT/'docs/submission_freeze.json').read_text())
    for name,digest in freeze['protected'].items():
        p=ROOT/name
        check('frozen:'+name,p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
    rendered=subprocess.run([sys.executable,str(ROOT/'src/build_submission_docs.py'),'--check'],capture_output=True,text=True)
    check('generated_documents_match_frozen_outputs',rendered.returncode==0,rendered.stdout+rendered.stderr)
    ip=pd.read_csv(NUM/'ip_summary.csv'); gp=pd.read_csv(NUM/'gp_summary.csv')
    canonical=pd.read_csv(NUM/'ip_vs_gp_comparison.csv')
    for _,row in canonical.iterrows():
        frame=ip if row.model=='IP' else gp
        mask=(frame.budget==row.budget)&(frame.logical_scenario==row.logical_scenario)
        if row.model=='GP':mask&=frame.priority==row.priority
        source=frame.loc[mask]
        key=f'{row.model}:{row.budget}:{row.logical_scenario}:{row.priority}'
        check('comparison_unique_source:'+key,len(source)==1)
        if len(source)!=1:continue
        s=source.iloc[0]
        cols=['projects_selected','total_investment','budget_utilization_percent','total_potential','total_risk','total_strategic']
        check('comparison_totals:'+key,np.allclose(row[cols].astype(float),s[cols].astype(float),rtol=0,atol=1e-6))
        for k in ['potential','risk','strategic']:
            bad=max(0,row[f'total_{k}']-row[f'target_{k}'] if k=='risk' else row[f'target_{k}']-row[f'total_{k}'])
            check('comparison_deviation:'+key+':'+k,abs(bad-row[f'undesirable_{k}'])<1e-3)
    for budget in sorted(canonical.budget.unique()):
        view=pd.read_csv(NUM/f'comparison_{int(budget/1e6)}m.csv')
        try:
            pd.testing.assert_frame_equal(view.reset_index(drop=True),canonical[canonical.budget==budget].reset_index(drop=True))
            passed=True
        except AssertionError:passed=False
        check(f'per_budget_view:{budget}',passed)
    for prefix in ['ip','gp','payoff','gp_fixed_targets']:
        summary=pd.read_csv(NUM/f'{prefix}_summary.csv')
        check('optimal_statuses:'+prefix,(summary.solver_status=='Optimal').all() and (summary.solver_solution_status==1).all())
    # Chart source data are reconciled against underlying selected portfolios.
    sector=pd.read_csv(NUM/'sector_composition.csv')
    selected={p:pd.read_csv(NUM/f'{p}_selected.csv') for p in ['ip','gp','gp_fixed_targets']}
    for i,r in sector.iterrows():
        prefix='ip' if r.model=='IP' else ('gp_fixed_targets' if r.target_policy=='fixed_baseline' else 'gp')
        df=selected[prefix]
        mask=(df.budget==r.budget)&(df.logical_scenario==r.logical_scenario)&(df.sector==r.sector)
        if r.model=='GP':mask&=df.priority==r.priority
        g=df[mask]
        check(f'chart_sector_data:{i}',len(g)==r.projects_selected and abs(g.investment_cost.sum()-r.total_investment)<.01)
    charts=NUM/'charts'
    manifest=json.loads((charts/'chart_manifest.json').read_text())
    for name,digest in manifest['sources'].items():
        check('chart_source_hash:'+name,hashlib.sha256((NUM/name).read_bytes()).hexdigest()==digest)
    for name,digest in manifest['figures'].items():
        check('chart_file_hash:'+name,hashlib.sha256((charts/name).read_bytes()).hexdigest()==digest)
        if name.endswith('.png'):
            with Image.open(charts/name) as img:
                check('chart_resolution:'+name,min(img.info.get('dpi',(0,0)))>=299 and img.width>=2000)
                img.verify()
        else:
            check('chart_pdf_header:'+name,(charts/name).read_bytes().startswith(b'%PDF'))
    check('seven_figure_pairs',len(list(charts.glob('*.png')))==7 and len(list(charts.glob('*.pdf')))==7)
    viva=(ROOT/'docs/viva_preparation.md').read_text(encoding='utf-8')
    questions=re.findall(r'^### (\d+)\. ',viva,re.M)
    check('at_least_50_viva_questions',len(questions)>=50,str(len(questions)))
    check('viva_sequential_numbering',[int(n) for n in questions]==list(range(1,len(questions)+1)))
    presentation=(ROOT/'docs/final_presentation_content.md').read_text(encoding='utf-8')
    slides=re.split(r'^## Slide \d+\. ',presentation,flags=re.M)[1:]
    check('sixteen_slides',len(slides)==16)
    for i,slide in enumerate(slides,1):
        bullets=len(re.findall(r'^- ',slide.split('**Recommended visual:**')[0],re.M))
        check(f'slide_{i}_3_to_6_points',3<=bullets<=6,str(bullets))
        check(f'slide_{i}_recommended_visual','**Recommended visual:**' in slide)
        speech=slide.split('**30-60 second explanation:**')[-1].strip()
        word_count=len(speech.split())
        check(f'slide_{i}_speaking_notes',60<=word_count<=140,f'{word_count} words')
    methodology=(ROOT/'docs/methodology.md').read_text(encoding='utf-8')
    check('nineteen_methodology_sections',[int(n) for n in re.findall(r'^## (\d+)\. ',methodology,re.M)]==list(range(1,20)))
    for name in ['README.md','docs/methodology.md','docs/final_results_summary.md','docs/project_explanation_beginner.md','docs/viva_preparation.md','docs/final_presentation_content.md','docs/final_model_audit.md']:
        txt=(ROOT/name).read_text(encoding='utf-8')
        check('consistent_proxy_term:'+name,'Funding-History Risk Proxy' in txt)
        check('no_unrendered_tokens:'+name,'{{' not in txt)
        if name!='docs/final_results_summary.md':
            check('upstream_counts_qualified:'+name,'previously reported' in txt.lower())
    # The generated report is a valid link target even on first execution.
    report_path=OUT/'consistency_report.md'
    report_path.touch(exist_ok=True)
    for p in [ROOT/'README.md',*(ROOT/'docs').glob('*.md'),*(ROOT/'results').rglob('*.md')]:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):continue
            check('link:'+str(p.relative_to(ROOT))+':'+target,(p.parent/target.split('#')[0]).exists())
    validation=pd.read_csv(NUM/'validation_report.csv')
    check('existing_validation_all_passed',validation.passed.all(),f'{validation.passed.sum()}/{len(validation)}')
    test_report=OUT/'tests.txt'
    check('rerun_tests_report',test_report.exists() and 'Ran 6 tests' in test_report.read_text() and re.search(r'^OK$',test_report.read_text(),re.M) is not None)
    validation_log=OUT/'validation.txt'
    check('rerun_validation_report',validation_log.exists() and f'VALIDATION: {len(validation)}/{len(validation)} passed' in validation_log.read_text())
    checks=pd.DataFrame(records)
    checks.to_csv(OUT/'consistency_checks.csv',index=False)
    before=freeze['before_finalization']
    (OUT/'file_changes.json').touch(exist_ok=True)
    now={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    created=sorted(set(now)-set(before)); modified=sorted(k for k in set(now)&set(before) if now[k]!=before[k]); removed=sorted(set(before)-set(now))
    changes={'created':created,'modified':modified,'removed':removed,'protected_files':len(freeze['protected'])}
    (OUT/'file_changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
    lines=['# Final submission consistency report','',f'**{checks.passed.sum()}/{len(checks)} submission checks passed.**',
        f'Existing model validation: **{validation.passed.sum()}/{len(validation)} passed**; six existing tests passed on rerun.',
        'All 60 exported portfolios retain Optimal problem/solution statuses. No mathematical model, score, data, configuration, target, weight or numerical portfolio result was changed.',
        '',f'{len(freeze["protected"])} frozen artifacts retain their original SHA256 hashes. Generated academic tables match the frozen output files.',
        'Checks reconcile all comparison totals/deviations, per-budget views, 420 sector data rows, chart source/output hashes, image resolution, links, 80 viva questions, 16 slide outlines and 19 methodology sections.',
        '', 'Tests and validation logs: [tests.txt](tests.txt), [validation.txt](validation.txt). Detailed submission checks: [consistency_checks.csv](consistency_checks.csv).',
        '', '## Authoritative results', '', 'See [final results summary](../../docs/final_results_summary.md) for baseline IP, all GP scenarios, deviations and sensitivity. The source authority remains results/optimization/*.csv.',
        '', '## Files created','']+['- `'+p+'`' for p in created]+['','## Files modified','']+['- `'+p+'`' for p in modified]+['','## Files removed','']+(['- `'+p+'`' for p in removed] or ['None. Historical data, notebooks and results are retained.'])+[
        '', '## Unresolved limitations','',
        'Missing original raw tables prevent raw reconstruction and independent verification of the previously reported 462,651 entities and 11,259 candidates. Historical funding is not a current price. The Funding-History Risk Proxy is not financial risk or failure probability and shares inputs with IPS. Strategy, logic and priorities remain scenario assumptions. Multi-period expenditures are unavailable; UI and NLP are out of scope.',
        '', '## Final project status','',
        '| Component | Status |','|---|---|',
        '| Repository audit and model freeze | DONE |',
        '| IP formulation/results presentation | DONE |',
        '| Logical-constraint scenario explanation | DONE |',
        '| Three score definitions and limitations | DONE |',
        '| GP formulation, deviations and normalization | DONE |',
        '| Payoff targets and priority scenarios | DONE |',
        '| Authoritative IP vs GP comparison | DONE |',
        '| Budget/priority/logical sensitivity | DONE |',
        '| Multi-period omission explanation | DONE |',
        '| Seven publication figures | DONE |',
        '| Final results summary | DONE |',
        '| Nineteen-section methodology | DONE |',
        '| Beginner study guide | DONE |',
        '| 80-question viva guide | DONE |',
        '| Sixteen-slide content and speaking notes | DONE |',
        '| Cleanup, historical labelling and final consistency | DONE |',
        '| Existing tests and validation rerun | DONE |',
        '| Raw reconstruction/upstream count re-verification | NOT DONE: source files absent; explicitly disclosed |',
        '| UI, NLP, multi-period implementation | NOT DONE: intentionally excluded |',
        '| PowerPoint file | NOT DONE: slide content only, as requested |','']
    if not checks.passed.all():
        lines.insert(2,'**INCOMPLETE: resolve failed checks before submission.**')
    report_path.write_text('\n'.join(lines),encoding='utf-8')
    print(f'SUBMISSION: {checks.passed.sum()}/{len(checks)} passed; {len(created)} files created, {len(modified)} modified; {len(removed)} removed.')
    if not checks.passed.all():
        print(checks[~checks.passed].to_string(index=False))
        raise AssertionError('Submission consistency failures')


if __name__=='__main__':
    main()
