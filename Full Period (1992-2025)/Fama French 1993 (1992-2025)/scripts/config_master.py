"""
Master configuration for the Fama-French 1993 replication project.
All scripts in this directory should import this file for path settings.
"""
import os

# --- Project Root ---
# Assumes the script is in a subdirectory of 'Full Period (1992-2025)/Fama French 1993 (1992-2025)'
PROJ_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..')

# --- Raw Data Paths ---
RAW_DATA_DIR = os.path.join(PROJ_ROOT, 'Raw Data')
BS_PATH = os.path.join(RAW_DATA_DIR, 'Balance Sheet110248807', 'FS_Combas.csv')
MKT_PRICES_PATH = os.path.join(RAW_DATA_DIR, 'Monthly Stock Price  Returns121529524', 'TRD_Mnth.csv')
MKT_RETURNS_PATH = os.path.join(RAW_DATA_DIR, 'Aggregated Monthly Market Returns141530201', 'TRD_Cnmont.csv')
RF_FILE = os.path.join(RAW_DATA_DIR, 'Risk-Free Rate135436249', 'TRD_Nrrate.csv')

# --- Output Paths ---
# Aligned output directory
OUTPUT_DIR = os.path.join(PROJ_ROOT, 'Full Period (1992-2025)', 'Fama French 1993 (1992-2025)', 'output_ff1993_aligned')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Path for the final characteristics table
PORTFOLIO_CHARS_PATH = os.path.join(OUTPUT_DIR, 'ff1993_portfolio_characteristics.csv')

# Path for the monthly portfolio membership and returns data
MEMBERSHIP_PATH = os.path.join(OUTPUT_DIR, 'ff1993_membership.csv')
MONTHLY_RETURNS_PATH = os.path.join(OUTPUT_DIR, 'ff1993_monthly_returns.csv')

# Path for the factor data
FACTORS_PATH = os.path.join(OUTPUT_DIR, 'ff1993_factors.csv')

# --- Time Period ---
START_DATE = '1992-01-01'
END_DATE = '2025-12-31'
START_YEAR = int(START_DATE[:4])
END_YEAR = int(END_DATE[:4])
