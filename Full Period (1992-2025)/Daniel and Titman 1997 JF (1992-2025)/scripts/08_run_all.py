import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    '01_build_master_panel.py',
    '02_build_characteristics_and_factors.py',
    '03_estimate_preformation_betas.py',
    '04_make_dt_portfolios.py',
    '05_make_dt_tests.py',
    '05b_make_fama_macbeth_chars_loadings.py',
    '06_format_academic_tables.py',
    '07_format_latex_tables.py',
]


def main():
    for s in SCRIPTS:
        p = ROOT / s
        print(f'Running {p.name} ...')
        subprocess.run(['/usr/bin/python3', str(p)], check=True)
    print('All done.')


if __name__ == '__main__':
    main()
