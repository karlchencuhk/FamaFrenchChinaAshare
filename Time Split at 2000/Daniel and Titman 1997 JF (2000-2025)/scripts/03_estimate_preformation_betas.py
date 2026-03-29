import csv
from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import to_float, ols, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_master_lookup():
    fpath = cfg.OUTPUT_DIR / 'master_panel_200001_202512.csv'
    stock_ex = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row['Trdmnt'], row['Stkcd'])
            stock_ex[key] = to_float(row['stock_excess_ret'])
    return stock_ex


def load_factor_lookup():
    fpath = cfg.OUTPUT_DIR / 'ff3_factors_monthly.csv'
    fac = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            fac[row['Trdmnt']] = {
                'MKT_RF': to_float(row['MKT_RF']),
                'SMB': to_float(row['SMB']),
                'HML': to_float(row['HML']),
            }
    return fac


def load_june_stocks_by_year():
    by_year = defaultdict(list)
    fpath = cfg.OUTPUT_DIR / 'june_characteristics.csv'
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            y = int(row['form_year'])
            by_year[y].append(row['Stkcd'])
    return by_year


def main():
    print('Step 3/8: estimating pre-formation betas...')

    stock_ex = load_master_lookup()
    fac = load_factor_lookup()
    june_by_year = load_june_stocks_by_year()

    out_rows = []
    cov_rows = []

    for y in range(1992, 2026):
        june = f'{y:04d}-06'
        end_i = cfg.month_to_int(june)
        start_i = end_i - (cfg.BETA_WINDOW - 1)
        months = [cfg.int_to_month(i) for i in range(start_i, end_i + 1)]

        stocks = june_by_year.get(y, [])
        n_total = len(stocks)
        n_ok = 0

        for stk in stocks:
            ys = []
            x_mkt = []
            x_smb = []
            x_hml = []
            for m in months:
                r = stock_ex.get((m, stk))
                f = fac.get(m)
                if f is None:
                    continue
                mkt = f['MKT_RF']
                smb = f['SMB']
                hml = f['HML']
                if r is None or mkt is None or smb is None or hml is None:
                    continue
                ys.append(r)
                x_mkt.append(mkt)
                x_smb.append(smb)
                x_hml.append(hml)

            n_obs = len(ys)
            if n_obs < cfg.BETA_MIN_OBS:
                out_rows.append({
                    'form_year': y,
                    'Stkcd': stk,
                    'window_start': months[0],
                    'window_end': months[-1],
                    'n_obs': n_obs,
                    'alpha': '',
                    'beta_mkt': '',
                    'beta_smb': '',
                    'beta_hml': '',
                })
                continue

            res = ols(ys, [x_mkt, x_smb, x_hml])
            if res is None:
                out_rows.append({
                    'form_year': y,
                    'Stkcd': stk,
                    'window_start': months[0],
                    'window_end': months[-1],
                    'n_obs': n_obs,
                    'alpha': '',
                    'beta_mkt': '',
                    'beta_smb': '',
                    'beta_hml': '',
                })
                continue

            b0, b1, b2, b3 = res['beta']
            out_rows.append({
                'form_year': y,
                'Stkcd': stk,
                'window_start': months[0],
                'window_end': months[-1],
                'n_obs': n_obs,
                'alpha': b0,
                'beta_mkt': b1,
                'beta_smb': b2,
                'beta_hml': b3,
            })
            n_ok += 1

        cov_rows.append({
            'form_year': y,
            'n_stocks_june_chars': n_total,
            'n_stocks_with_betas': n_ok,
            'beta_window_months': cfg.BETA_WINDOW,
            'beta_min_obs': cfg.BETA_MIN_OBS,
        })

    write_csv(
        cfg.OUTPUT_DIR / 'preformation_betas.csv',
        ['form_year', 'Stkcd', 'window_start', 'window_end', 'n_obs', 'alpha', 'beta_mkt', 'beta_smb', 'beta_hml'],
        out_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'beta_estimation_coverage.csv',
        ['form_year', 'n_stocks_june_chars', 'n_stocks_with_betas', 'beta_window_months', 'beta_min_obs'],
        cov_rows,
    )

    print('Done:', cfg.OUTPUT_DIR / 'preformation_betas.csv')
    print('Done:', cfg.OUTPUT_DIR / 'beta_estimation_coverage.csv')


if __name__ == '__main__':
    main()
