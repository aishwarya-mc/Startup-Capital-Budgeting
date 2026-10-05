"""Reproduce all optimization artifacts from the existing processed sample."""
import subprocess
import sys
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[1]
    out=root/'results/optimization'
    out.mkdir(exist_ok=True,parents=True)
    steps=['score_projects','integer_programming','goal_programming','compare_models',
           'sensitivity_analysis','plot_optimization','validate_results']
    with (out/'execution_report.txt').open('w',encoding='utf-8') as log:
        for step in steps:
            print(f'Running {step}...',flush=True)
            result=subprocess.run([sys.executable,str(root/'src'/f'{step}.py')],cwd=root,
                                  capture_output=True,text=True)
            log.write(f'\n{step} (exit {result.returncode})\n{result.stdout}\n{result.stderr}')
            log.flush()
            if result.returncode:
                print(result.stdout,result.stderr)
                raise RuntimeError(f'{step} failed; inspect execution_report.txt')
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-v'],
                              cwd=root,capture_output=True,text=True)
        (out/'test_report.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
        log.write(f'\nUnit tests (exit {result.returncode})\n{result.stdout}\n{result.stderr}')
        if result.returncode:
            raise RuntimeError('Tests failed; inspect test_report.txt')
    print('Complete: results/optimization/; validation_report.md and test_report.txt contain checks.')


if __name__=='__main__':
    main()
