import csv
import math
from collections import defaultdict
from pathlib import Path
import importlib.util


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_rf_monthly_effective():
    rf = {}
    rf_date = {}
    with open(cfg.RF_FILE, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            d = row.get('Clsdt')
            val = row.get('Nrrmtdt')
            if not d or not val:
                continue
            m = d[:7]
            try:
                rf_m = float(val) / 100.0
            except ValueError:
                continue

            # Keep the latest available quote in each month.
            prev_d = rf_date.get(m)
            if prev_d is None or d > prev_d:
                rf_date[m] = d
                rf[m] = rf_m
    return rf


def load_market_returns():
    mkt = {}
    with open(cfg.MKT_FILE, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Markettype') != '5':
                continue
            m = row.get('Trdmnt')
            rv = row.get('Cmretwdtl')
            if m and rv:
                mkt[m] = float(rv)
    return mkt


def load_book_equity_a_statement():
    be = defaultdict(dict)
    with open(cfg.BS_FILE, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Typrep') != 'A':
                continue
            acc = row.get('Accper')
            if not acc or not acc.endswith('-12-31'):
                continue
            stk = (row.get('Stkcd') or '').zfill(6)
            if not stk:
                continue
            y = int(acc[:4])
            v = row.get('A003100000') or row.get('A003000000')
            if v:
                be[stk][y] = float(v)
    return be


def assigned_be_year(month: str) -> int:
    y, mo = map(int, month.split('-'))
    return y - 1 if mo >= 7 else y - 2


def main():
    print('Loading RF...')
    rf = load_rf_monthly_effective()
    print('Loading market return...')
    mkt = load_market_returns()
    print('Loading annual BE (A statement)...')
    be_map = load_book_equity_a_statement()

    # CSMAR-style market value fields are often stored in "thousand CNY".
    # Empirically, treating Msmvttl as thousand CNY yields plausible shares outstanding
    # (market value / price). We therefore scale to CNY here so that ME and BE are comparable.
    ME_SCALE_TO_CNY = 1000.0

    keep_start = '1990-12'
    keep_end = cfg.RETURN_END
    s_i = cfg.month_to_int(keep_start)
    e_i = cfg.month_to_int(keep_end)

    out_file = cfg.OUTPUT_DIR / 'master_panel_200001_202512.csv'
    out_cov = cfg.OUTPUT_DIR / 'sample_coverage.csv'

    n = 0
    with open(cfg.STOCK_FILE, newline='', encoding='utf-8-sig') as fin, open(out_file, 'w', newline='', encoding='utf-8') as fout:
        r = csv.DictReader(fin)
        w = csv.writer(fout)
        w.writerow([
            'Stkcd', 'Trdmnt', 'Mretwd', 'Msmvttl', 'Markettype',
            'rf_monthly_eff', 'market_ret', 'stock_excess_ret', 'market_excess_ret',
            'book_equity', 'be_me', 'ln_size', 'ln_be_me', 'be_year'
        ])

        for row in r:
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

            sr = row.get('Mretwd')
            size = row.get('Msmvttl')
            if not size:
                continue

            size_f = float(size) * ME_SCALE_TO_CNY
            sr_f = float(sr) if sr else None
            rf_f = rf.get(m)
            mr_f = mkt.get(m)

            s_ex = (sr_f - rf_f) if (sr_f is not None and rf_f is not None) else None
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

            w.writerow([
                stk, m,
                '' if sr_f is None else f'{sr_f:.10f}',
                f'{size_f:.6f}',
                mt,
                '' if rf_f is None else f'{rf_f:.10f}',
                '' if mr_f is None else f'{mr_f:.10f}',
                '' if s_ex is None else f'{s_ex:.10f}',
                '' if m_ex is None else f'{m_ex:.10f}',
                '' if be is None else f'{be:.6f}',
                '' if beme is None else f'{beme:.10f}',
                '' if ln_size is None else f'{ln_size:.10f}',
                '' if ln_beme is None else f'{ln_beme:.10f}',
                by,
            ])
            n += 1

    # simple coverage table in target return window
    month_counts = defaultdict(int)
    with open(out_file, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            m = row['Trdmnt']
            if cfg.month_to_int(cfg.RETURN_START) <= cfg.month_to_int(m) <= cfg.month_to_int(cfg.RETURN_END):
                month_counts[m] += 1

    with open(out_cov, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Trdmnt', 'n_stocks_with_size'])
        for m in sorted(month_counts.keys(), key=cfg.month_to_int):
            w.writerow([m, month_counts[m]])

    print('Done:', out_file)
    print('Rows written:', n)


if __name__ == '__main__':
    main()
