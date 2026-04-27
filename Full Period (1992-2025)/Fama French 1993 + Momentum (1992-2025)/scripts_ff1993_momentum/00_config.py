from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]

BASE_FF3_DIR = REPO_ROOT / "Full Period (1992-2025)" / "Fama French 1993 (1992-2025)"
BASE_FF3_OUTPUT = BASE_FF3_DIR / "output"

RAW_DATA_DIR = REPO_ROOT / "Raw Data"
STOCK_FILE = RAW_DATA_DIR / "Monthly Stock Price  Returns121529524" / "TRD_Mnth_SSE_A_SZSE_A.txt"

OUTPUT_DIR = PROJECT_ROOT / "output_ff1993_momentum"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Sample windows (same as FF1993)
RETURN_START = "1992-07"
RETURN_END = "2025-12"
HISTORY_START = "1990-01"

# Momentum strategy parameters to test
MOM_FORMATION_MONTHS = [3, 6, 9, 12]
MOM_HOLDING_MONTHS = [1, 3, 6, 9, 12]
MOM_SKIP_MONTH = 1  # Skip one month between formation and holding
MOM_STRATEGIES = [
    (3, 1), (3, 3), (3, 6),
    (6, 1), (6, 3), (6, 6),
    (9, 3), (9, 6), (9, 9),
    (12, 1), (12, 3), (12, 6), (12, 12),
]

# UMD construction parameters
MOM_DECILES = 10  # top and bottom deciles
MOM_WEIGHTING = "value_weighted"
ME_SCALE_TO_CNY = 1000.0
NW_LAG = 12


def month_to_int(m: str) -> int:
    y, mo = m.split("-")
    return int(y) * 12 + (int(mo) - 1)


def int_to_month(v: int) -> str:
    y = v // 12
    m = (v % 12) + 1
    return f"{y:04d}-{m:02d}"


def prev_month(m: str) -> str:
    return int_to_month(month_to_int(m) - 1)


def all_months(start_m: str, end_m: str):
    s = month_to_int(start_m)
    e = month_to_int(end_m)
    return [int_to_month(i) for i in range(s, e + 1)]
