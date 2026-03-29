from pathlib import Path
import csv
import math
from collections import defaultdict

ROOT = Path('/Users/kahouchen/Downloads/Fama French China')
OUT_DIR = ROOT / 'output'
OUT_DIR.mkdir(exist_ok=True)

STOCK_PATH = ROOT / 'Monthly Stock Price  Returns121529524' / 'TRD_Mnth_SSE_A_SZSE_A.txt'
BS_PATH = ROOT / 'Balance Sheet110248807' / 'FS_Combas.csv'
MKT_PATH = ROOT / 'Aggregated Monthly Market Returns141530201' / 'TRD_Cnmont.csv'
RF_PATH = ROOT / 'Risk_Free_Rate' / 'IR3TIB01CNM156N.csv'

OUT_PATH = OUT_DIR / 'ff1992_chars_200001_202512.csv'
SUMMARY_PATH = OUT_DIR / 'ff1992_chars_200001_202512_summary.txt'

START = '2000-01'
END = '2025-12'
BETA_WINDOW = 60
BETA_MIN_OBS = 24


def month_to_int(m: str) -> int:
    y, mo = m.split('-')
    return int(y) * 12 + int(mo)


def load_rf_monthly_effective(path: Path) -> dict:
    rf = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            d = row.get('observation_date')
            val = row.get('IR3TIB01CNM156N')
            if not d or not val:
                continue
            m = d[:7]
            ann = float(val) / 100.0
            rf[m] = (1.0 + ann) ** (1.0 / 12.0) - 1.0
    return rf


def load_market_returns(path: Path) -> dict:
    mkt = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Markettype') != '5':
                continue
            m = row.get('Trdmnt')
            rv = row.get('Cmretwdtl')
            if not m or not rv:
                continue
            mkt[m] = float(rv)
    return mkt


def load_stock_data(path: Path, end_i: int):
    stock_ret = defaultdict(dict)
    stock_size = defaultdict(dict)
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            mt = row.get('Markettype')
            if mt not in ('1', '4'):
                continue
            m = row.get('Trdmnt')
            if not m:
                continue
            mi = month_to_int(m)
            if mi > end_i:
                continue
            stk = row.get('Stkcd')
            if not stk:
                continue
            stk = stk.zfill(6)
            rv = row.get('Mretwd')
            if rv:
                stock_ret[stk][m] = float(rv)
            sv = row.get('Msmvttl')
            if sv:
                stock_size[stk][m] = float(sv)
    return stock_ret, stock_size


def load_book_equity(path: Path):
    book_equity = defaultdict(dict)
    with open(path, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Typrep') != 'A':
                continue
            acc = row.get('Accper')
            if not acc or not acc.endswith('-12-31'):
                continue
            stk = row.get('Stkcd')
            if not stk:
                continue
            stk = stk.zfill(6)
            y = int(acc[:4])
            be = row.get('A003100000') or row.get('A003000000')
            if not be:
                continue
            book_equity[stk][y] = float(be)
    return book_equity


def main():
    start_i = month_to_int(START)
    end_i = month_to_int(END)

    print('Loading RF...')
    rf = load_rf_monthly_effective(RF_PATH)
    print('RF months:', len(rf))

    print('Loading market...')
    mkt = load_market_returns(MKT_PATH)
    print('Market months:', len(mkt))

    print('Loading stock data...')
    stock_ret, stock_size = load_stock_data(STOCK_PATH, end_i)
    print('Stocks with size:', len(stock_size))

    print('Loading book equity...')
    book_equity = load_book_equity(BS_PATH)
    print('Stocks with BE:', len(book_equity))

    print('Building panel...')
    rows_written = 0
    beta_non_missing = 0
    beme_non_missing = 0
    rf_non_missing = 0

    with open(OUT_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'Stkcd', 'Trdmnt', 'beta_60m', 'size_msmvttl', 'ln_size', 'book_equity', 'be_me',
            'stock_ret', 'rf_monthly_eff', 'stock_excess_ret', 'market_ret', 'market_excess_ret'
        ])

        for i, stk in enumerate(sorted(stock_size.keys()), start=1):
            ret_map = stock_ret.get(stk, {})
            size_map = stock_size.get(stk, {})

            tmonths = [m for m in size_map if start_i <= month_to_int(m) <= end_i]
            if not tmonths:
                continue
            tmonths.sort(key=month_to_int)

            obs = []
            for hm, sr in ret_map.items():
                hmi = month_to_int(hm)
                if hmi > end_i:
                    continue
                rm = mkt.get(hm)
                rfm = rf.get(hm)
                if rm is None or rfm is None:
                    continue
                obs.append((hmi, rm - rfm, sr - rfm))
            obs.sort(key=lambda x: x[0])

            nobs = len(obs)
            pref_x = [0.0] * (nobs + 1)
            pref_y = [0.0] * (nobs + 1)
            pref_xx = [0.0] * (nobs + 1)
            pref_xy = [0.0] * (nobs + 1)

            for j, (_, x, y) in enumerate(obs, start=1):
                pref_x[j] = pref_x[j - 1] + x
                pref_y[j] = pref_y[j - 1] + y
                pref_xx[j] = pref_xx[j - 1] + x * x
                pref_xy[j] = pref_xy[j - 1] + x * y

            l = 0
            r = 0

            for m in tmonths:
                mi = month_to_int(m)
                lo = mi - BETA_WINDOW
                hi = mi - 1

                while l < nobs and obs[l][0] < lo:
                    l += 1
                while r < nobs and obs[r][0] <= hi:
                    r += 1

                n = r - l
                beta = None
                if n >= BETA_MIN_OBS:
                    sx = pref_x[r] - pref_x[l]
                    sy = pref_y[r] - pref_y[l]
                    sxx = pref_xx[r] - pref_xx[l]
                    sxy = pref_xy[r] - pref_xy[l]
                    varx = sxx - (sx * sx) / n
                    if varx > 0:
                        covxy = sxy - (sx * sy) / n
                        beta = covxy / varx
                        beta_non_missing += 1

                size = size_map[m]
                ln_size = math.log(size) if size > 0 else None

                y, mo = map(int, m.split('-'))
                be_year = y - 1 if mo >= 7 else y - 2
                be = book_equity.get(stk, {}).get(be_year)
                beme = (be / size) if (be is not None and size > 0) else None
                if beme is not None:
                    beme_non_missing += 1

                sr_now = ret_map.get(m)
                rf_now = rf.get(m)
                rm_now = mkt.get(m)
                if rf_now is not None:
                    rf_non_missing += 1
                s_ex = (sr_now - rf_now) if (sr_now is not None and rf_now is not None) else None
                m_ex = (rm_now - rf_now) if (rm_now is not None and rf_now is not None) else None

                w.writerow([
                    stk,
                    m,
                    '' if beta is None else f'{beta:.10f}',
                    f'{size:.6f}',
                    '' if ln_size is None else f'{ln_size:.10f}',
                    '' if be is None else f'{be:.6f}',
                    '' if beme is None else f'{beme:.10f}',
                    '' if sr_now is None else f'{sr_now:.10f}',
                    '' if rf_now is None else f'{rf_now:.10f}',
                    '' if s_ex is None else f'{s_ex:.10f}',
                    '' if rm_now is None else f'{rm_now:.10f}',
                    '' if m_ex is None else f'{m_ex:.10f}',
                ])
                rows_written += 1

            if i % 500 == 0:
                print(f'Processed stocks: {i}, rows: {rows_written}')

    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write('FF1992 characteristics build summary\n')
        f.write(f'period: {START} to {END}\n')
        f.write('universe: SSE & SZSE A-share only (Markettype 1,4)\n')
        f.write('statement type: Typrep=A only\n')
        f.write('beta: rolling 60 months OLS with intercept, min obs=24\n')
        f.write('BE/ME lag: July t to June t+1 uses BE from fiscal year t-1\n')
        f.write('RF conversion: effective monthly from annualized rate: (1+r)^1/12 - 1\n')
        f.write(f'rows_written: {rows_written}\n')
        f.write(f'beta_non_missing: {beta_non_missing}\n')
        f.write(f'beme_non_missing: {beme_non_missing}\n')
        f.write(f'rf_non_missing_cells: {rf_non_missing}\n')

    print('DONE')
    print('Output:', OUT_PATH)
    print('Summary:', SUMMARY_PATH)
    print('Rows written:', rows_written)
    print('Beta non-missing:', beta_non_missing)
    print('BE/ME non-missing:', beme_non_missing)


if __name__ == '__main__':
    main()
