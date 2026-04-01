import subprocess
from pathlib import Path

SCRIPTS = [
    '01_build_ff1993_aligned_tables.py',
    '02_format_ff1993_aligned_tables.py',
]


def main():
    root = Path(__file__).resolve().parent
    for s in SCRIPTS:
        p = root / s
        print('Running:', p.name)
        subprocess.run(['python3', str(p)], check=True)
    print('All done.')


if __name__ == '__main__':
    main()
