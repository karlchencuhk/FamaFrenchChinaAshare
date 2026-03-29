from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT.parents[0]
OUTPUT_DIR = PROJECT_ROOT / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Raw data
STOCK_FILE = DATA_ROOT / 'Monthly Stock Price  Returns121529524' / 'TRD_Mnth_SSE_A_SZSE_A.txt'
BS_FILE = DATA_ROOT / 'Balance Sheet110248807' / 'FS_Combas.csv'
MKT_FILE = DATA_ROOT / 'Aggregated Monthly Market Returns141530201' / 'TRD_Cnmont.csv'
RF_FILE = DATA_ROOT / 'Risk-Free Rate135436249' / 'TRD_Nrrate.csv'

# Sample controls
RETURN_START = '2010-04'
RETURN_END = '2025-12'
BETA_WINDOW = 60
BETA_MIN_OBS = 24
NW_LAG = 12


def month_to_int(m: str) -> int:
    y, mo = m.split('-')
    return int(y) * 12 + (int(mo) - 1)


def int_to_month(v: int) -> str:
    y = v // 12
    m = (v % 12) + 1
    return f'{y:04d}-{m:02d}'


def prev_month(m: str) -> str:
    return int_to_month(month_to_int(m) - 1)


def formation_year_for_return_month(m: str) -> int:
    y, mo = map(int, m.split('-'))
    return y if mo >= 7 else y - 1


def all_months(start_m: str, end_m: str):
    s = month_to_int(start_m)
    e = month_to_int(end_m)
    return [int_to_month(i) for i in range(s, e + 1)]
