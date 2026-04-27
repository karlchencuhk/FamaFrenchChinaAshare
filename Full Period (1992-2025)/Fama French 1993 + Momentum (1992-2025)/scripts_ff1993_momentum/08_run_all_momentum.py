import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_momentum_optimization.py",
    "02_build_umd_factor.py",
    "03_build_ff4_factors.py",
    "04_run_ff4_regressions.py",
    "05_alpha_diagnostics.py",
    "06_subperiod_analysis.py",
    "07_format_academic_tables.py",
]


def main():
    for s in SCRIPTS:
        p = ROOT / s
        print(f"Running {p.name} ...")
        subprocess.run(["/usr/bin/python3", str(p)], check=True)
    print("All done.")


if __name__ == "__main__":
    main()
