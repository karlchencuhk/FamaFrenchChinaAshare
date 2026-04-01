import pandas as pd, json, re
from pathlib import Path

root = Path('/Users/kahouchen/Downloads/Fama French China')
fs_path = root / 'Raw Data/Net Profit161242547/FS_Comins.csv'
fs_des_path = root / 'Raw Data/Net Profit161242547/FS_Comins[DES][csv].txt'
trd_path = root / 'Raw Data/Monthly Stock Price  Returns121529524/TRD_Mnth_SSE_A_SZSE_A.txt'


def norm_cols(cols):
    return {c.lower(): c for c in cols}


def pick_col(cols_map, candidates):
    for c in candidates:
        if c.lower() in cols_map:
            return cols_map[c.lower()]
    return None


# FS_Comins
fs = pd.read_csv(fs_path, low_memory=False)
fs_cols = list(fs.columns)
cm = norm_cols(fs_cols)

col_stk = pick_col(cm, ['Stkcd'])
col_typrep = pick_col(cm, ['Typrep'])
col_accper = pick_col(cm, ['Accper'])
col_earn = pick_col(cm, ['B002000101'])

acc = pd.to_datetime(fs[col_accper], errors='coerce') if col_accper else pd.Series([pd.NaT] * len(fs))
year = acc.dt.year
is_dec31 = (acc.dt.month == 12) & (acc.dt.day == 31)

if col_typrep:
    typ_nonmiss = fs[col_typrep].notna()
    typA = fs[col_typrep].astype(str).str.upper().eq('A')
else:
    typ_nonmiss = pd.Series([False] * len(fs))
    typA = pd.Series([False] * len(fs))

years_nonmiss = sorted(pd.Series(year.dropna().astype(int).unique()).tolist())
min_year = min(years_nonmiss) if years_nonmiss else None
max_year = max(years_nonmiss) if years_nonmiss else None

share_typA = float((typA & typ_nonmiss).sum() / typ_nonmiss.sum()) if typ_nonmiss.sum() else None
A_rows = int(typA.sum())
A_dec_mask = typA & is_dec31
A_dec = int(A_dec_mask.sum())
share_A_dec = float(A_dec / A_rows) if A_rows else None

earn = pd.to_numeric(fs[col_earn], errors='coerce') if col_earn else pd.Series([pd.NA] * len(fs))
A_dec_miss = int(earn[A_dec_mask].isna().sum())
miss_rate = float(A_dec_miss / A_dec) if A_dec else None

if col_stk:
    key_df = pd.DataFrame({'stk': fs[col_stk], 'yr': year})
    key = key_df[A_dec_mask & key_df['yr'].notna()].copy()
    dup_mask = key.duplicated(subset=['stk', 'yr'], keep=False)
    dup_rows = int(dup_mask.sum())
    dup_keys = int(key[dup_mask].drop_duplicates(subset=['stk', 'yr']).shape[0])
    total_keys = int(key.drop_duplicates(subset=['stk', 'yr']).shape[0])
else:
    dup_rows = dup_keys = total_keys = None

valid_annual = A_dec_mask & earn.notna()
neg_frac = float((earn[valid_annual] < 0).sum() / valid_annual.sum()) if valid_annual.sum() else None

patterns = re.compile(r'(ann|pub|declare|disclos|report|apubl|audi|enddat|publish|notice|fann|accann)', re.I)
candidate_date_cols = [c for c in fs_cols if patterns.search(c)]
for c in fs_cols:
    if re.search(r'(date|dt|day)', c, re.I) and c not in candidate_date_cols:
        candidate_date_cols.append(c)

try:
    des_text = fs_des_path.read_text(encoding='utf-8', errors='ignore')
except Exception:
    des_text = fs_des_path.read_text(encoding='gbk', errors='ignore')

raw_des_hits = re.findall(
    r'(Ann\w+|Pub\w+|Fann\w+|Declare\w*|Publish\w*|公告\w*|披露\w*|发布日期|公告日期)',
    des_text,
    flags=re.I,
)
des_hits = sorted(set(raw_des_hits))

# TRD_Mnth_SSE_A_SZSE_A
trd = pd.read_csv(trd_path, low_memory=False)
trd_cols = list(trd.columns)
tm = norm_cols(trd_cols)

col_mkt = pick_col(tm, ['Markettype'])
col_trdmnt = pick_col(tm, ['Trdmnt'])
col_msmvttl = pick_col(tm, ['Msmvttl'])

trd_date = pd.to_datetime(trd[col_trdmnt], errors='coerce') if col_trdmnt else pd.Series([pd.NaT] * len(trd))
trd_year = trd_date.dt.year
trd_month = trd_date.dt.month
mkt = pd.to_numeric(trd[col_mkt], errors='coerce') if col_mkt else pd.Series([pd.NA] * len(trd))
msmv = pd.to_numeric(trd[col_msmvttl], errors='coerce') if col_msmvttl else pd.Series([pd.NA] * len(trd))

mask = mkt.isin([1, 4]) & (trd_month == 12)
dec = pd.DataFrame({'year': trd_year[mask], 'msmv': msmv[mask]}).dropna(subset=['year'])
if len(dec):
    g = dec.groupby('year')['msmv']
    by_year = pd.DataFrame({
        'dec_rows': g.size(),
        'dec_positive': g.apply(lambda s: (s > 0).sum())
    })
    by_year['share_positive'] = by_year['dec_positive'] / by_year['dec_rows']
    by_year = by_year.sort_index()

    coverage_summary = {
        'min_year': int(by_year.index.min()),
        'max_year': int(by_year.index.max()),
        'years': int(by_year.shape[0]),
        'mean_share_positive': float(by_year['share_positive'].mean()),
        'p10_share_positive': float(by_year['share_positive'].quantile(0.1)),
        'p50_share_positive': float(by_year['share_positive'].median()),
        'p90_share_positive': float(by_year['share_positive'].quantile(0.9)),
        'min_share_positive': float(by_year['share_positive'].min()),
    }

    sample = pd.concat([by_year.head(5), by_year.tail(5)]).reset_index().rename(columns={'index': 'year'})
    by_year_sample = sample.to_dict(orient='records')
else:
    coverage_summary = None
    by_year_sample = []

out = {
    'fs_schema': {
        'Stkcd': col_stk,
        'Typrep': col_typrep,
        'Accper': col_accper,
        'E_numerator_candidate_B002000101': col_earn,
        'columns_count': len(fs_cols)
    },
    'trd_schema': {
        'Markettype': col_mkt,
        'Trdmnt': col_trdmnt,
        'EP_denominator_candidate_Msmvttl': col_msmvttl,
        'columns_count': len(trd_cols)
    },
    'fs_quality': {
        'year_coverage_min': min_year,
        'year_coverage_max': max_year,
        'n_unique_years': len(years_nonmiss),
        'share_typrep_A': share_typA,
        'count_typrep_A': A_rows,
        'count_typrep_A_dec31': A_dec,
        'share_dec31_within_typrep_A': share_A_dec,
        'missing_rate_B002000101_in_A_dec31': miss_rate,
        'duplicates_rows_at_stkcd_fiscalyear_in_A_dec31': dup_rows,
        'duplicate_keys_at_stkcd_fiscalyear_in_A_dec31': dup_keys,
        'unique_keys_at_stkcd_fiscalyear_in_A_dec31': total_keys,
        'negative_earnings_fraction_nonmissing_A_dec31': neg_frac,
    },
    'announcement_date_check': {
        'fs_candidate_date_or_announcement_columns': candidate_date_cols,
        'descriptor_keyword_hits': des_hits[:50]
    },
    'trd_dec_msmvttl_coverage_markettype_1_4': {
        'summary': coverage_summary,
        'first_last_years_sample': by_year_sample
    }
}

print(json.dumps(out, ensure_ascii=False, indent=2))
