import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    '01_build_ff3_and_tables.py',
    '02_format_academic_tables.py',
    '03_format_latex_tables.py',
]


def main():
    for s in SCRIPTS:
        p = ROOT / s
        print(f'Running {p.name} ...')
        subprocess.run(['/usr/bin/python3', str(p)], check=True)
    print('All done.')


if __name__ == '__main__':
    main()
