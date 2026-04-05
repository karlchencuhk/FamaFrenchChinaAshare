from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_OUTPUT = PROJECT_ROOT / 'output'
OUT_DIR = PROJECT_ROOT / 'output_ff1993_aligned'
OUT_DIR.mkdir(exist_ok=True)
