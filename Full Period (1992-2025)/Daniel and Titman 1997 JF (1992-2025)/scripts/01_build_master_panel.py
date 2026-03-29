import math
from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import iter_clean_csv, to_float, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_rf_monthly_effective():
    rf = {}
    rf_date = {}
    for row in iter_clean_csv(cfg.RF_FILE):
        d = row.get('Clsdt')
        val = row.get('Nrrmtdt')
        if not d:
            continue
        fv = to_float(val)
        if fv is None:
            continue
        m = d[:7]
        prev = rf_date.get(m)
        if prev is None or d > prev:
            rf_date[m] = d
            rf[m] = fv / 100.0
    return rf


def load_market_returns():
    mkt = {}
    for row in iter_clean_csv(cfg.MKT_FILE):
        if row.get('Markettype') != '5':
            continue
        m = row.get('Trdmnt')
        rv = to_float(row.get('Cmretwdtl'))
        if m and rv is not None:
            mkt[m] = rv
    return mkt


def load_book_equity_december_a():
    be = defaultdict(dict)
    for row in iter_clean_csv(cfg.BS_FILE):
        if row.get('Typrep') != 'A':
            continue
        acc = row.get('Accper')
        if not acc or not acc.endswith('-12-31'):
            continue
        stk = (row.get('Stkcd') or '').zfill(6)
        if not stk:
            continue
        y = int(acc[:4])
        v = to_float(row.get('A003100000'))
        if v is None:
            v = to_float(row.get('A003000000'))
        if v is None:
            continue
        be[stk][y] = v
    return be


def assigned_be_year(m):
    y, mo = map(int, m.split('-'))
    return y - 1 if mo >= 7 else y - 2


def main():
    print('Step 1/8: building master panel...')

    rf = load_rf_monthly_effective()
    mkt = load_market_returns()
    be_map = load_book_equity_december_a()

    keep_start = '1990-12'  # include pre-sample history for beta estimation
    keep_end = cfg.RETURN_END
    s_i = cfg.month_to_int(keep_start)
    e_i = cfg.month_to_int(keep_end)

    out_file = cfg.OUTPUT_DIR / 'master_panel_199207_202512.csv'
    out_cov = cfg.OUTPUT_DIR / 'sample_coverage.csv'

    rows = []
    n = 0
    for row in iter_clean_csv(cfg.STOCK_FILE):
        mt = row.get('Markettype')
        if mt not in ('1', '4'):
            continue

        m = row.get('Trdmnt')
        if not m:
            continue
        mi = cfg.month_to_int(m)
        if mi < s_i or mi > e_i:
            continue

        stk = (row.get('Stkcd') or '').zfill(6)
        if not stk:
            continue

        sr = to_float(row.get('Mretwd'))
        size_f = to_float(row.get('Msmvttl'))
        if size_f is None or size_f <= 0:
            continue

        rf_f = rf.get(m)
        mr_f = mkt.get(m)

        s_ex = (sr - rf_f) if (sr is not None and rf_f is not None) else None
        m_ex = (mr_f - rf_f) if (mr_f is not None and rf_f is not None) else None

        by = assigned_be_year(m)
        be = be_map.get(stk, {}).get(by)
        beme = None
        ln_beme = None
        if be is not None and size_f > 0:
            beme = be / size_f
            if beme > 0:
                ln_beme = math.log(beme)

        ln_size = math.log(size_f) if size_f > 0 else None

        rows.append({
            'Stkcd': stk,
            'Trdmnt': m,
            'Mretwd': '' if sr is None else f'{sr:.10f}',
            'Msmvttl': f'{size_f:.6f}',
            'Markettype': mt,
            'rf_monthly_eff': '' if rf_f is None else f'{rf_f:.10f}',
            'market_ret': '' if mr_f is None else f'{mr_f:.10f}',
            'stock_excess_ret': '' if s_ex is None else f'{s_ex:.10f}',
            'market_excess_ret': '' if m_ex is None else f'{m_ex:.10f}',
            'book_equity': '' if be is None else f'{be:.6f}',
            'be_me': '' if beme is None else f'{beme:.10f}',
            'ln_size': '' if ln_size is None else f'{ln_size:.10f}',
            'ln_be_me': '' if ln_beme is None else f'{ln_beme:.10f}',
            'be_year': by,
        })
        n += 1

    write_csv(
        out_file,
        [
            'Stkcd', 'Trdmnt', 'Mretwd', 'Msmvttl', 'Markettype',
            'rf_monthly_eff', 'market_ret', 'stock_excess_ret', 'market_excess_ret',
            'book_equity', 'be_me', 'ln_size', 'ln_be_me', 'be_year'
        ],
        rows,
    )

    month_counts = defaultdict(int)
    for r in rows:
        m = r['Trdmnt']
        if cfg.month_to_int(cfg.RETURN_START) <= cfg.month_to_int(m) <= cfg.month_to_int(cfg.RETURN_END):
            month_counts[m] += 1

    cov_rows = [{'Trdmnt': m, 'n_stocks_with_size': month_counts[m]} for m in sorted(month_counts, key=cfg.month_to_int)]
    write_csv(out_cov, ['Trdmnt', 'n_stocks_with_size'], cov_rows)

    print('Done:', out_file)
    print('Rows written:', n)


if __name__ == '__main__':
    main()
