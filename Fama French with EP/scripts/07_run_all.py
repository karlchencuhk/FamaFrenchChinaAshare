import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    '01_build_master_panel.py',
    '02_build_june_chars_and_membership.py',
    '03_make_table_ii.py',
    '04_make_table_i_size_beta_10x10.py',
    '05_make_table_v_size_beme_10x10.py',
    '05b_make_table_iv_beme_only.py',
    '06_make_table_iii_fama_macbeth.py',
]


def main():
    for s in SCRIPTS:
        p = ROOT / s
        print(f'Running {p.name} ...')
        subprocess.run(['/usr/bin/python3', str(p)], check=True)
    print('All done.')


if __name__ == '__main__':
    main()
