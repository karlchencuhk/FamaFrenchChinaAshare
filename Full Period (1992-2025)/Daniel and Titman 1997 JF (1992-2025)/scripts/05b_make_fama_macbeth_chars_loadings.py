import csv
import math
from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import to_float, ols, nw_tstat_mean, significance_from_t, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_master_lookup():
    fpath = cfg.OUTPUT_DIR / 'master_panel_199207_202512.csv'
    out = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row['Trdmnt'], row['Stkcd'])
            out[key] = {
                'stock_excess_ret': to_float(row.get('stock_excess_ret')),
            }
    return out


def load_membership_lookup():
    # June-formation characteristics carried from Jul(t) to Jun(t+1)
    fpath = cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv'
    out = defaultdict(list)
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            size_june = to_float(row.get('size_june'))
            be_me = to_float(row.get('be_me'))
            if size_june is None or size_june <= 0 or be_me is None or be_me <= 0:
                continue
            out[row['Trdmnt']].append({
                'Stkcd': row['Stkcd'],
                'ln_size': math.log(size_june),
                'ln_be_me': math.log(be_me),
                'form_year': int(row['form_year']),
            })
    return out


def load_preformation_betas():
    fpath = cfg.OUTPUT_DIR / 'preformation_betas.csv'
    out = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            form_year = int(row['form_year'])
            stk = row['Stkcd']
            b_smb = to_float(row.get('beta_smb'))
            b_hml = to_float(row.get('beta_hml'))
            if b_smb is None or b_hml is None:
                continue
            out[(form_year, stk)] = {
                'beta_smb': b_smb,
                'beta_hml': b_hml,
            }
    return out


def main():
    print('Step 6/9: running Fama-MacBeth (chars + loadings) for Daniel-Titman...')

    master = load_master_lookup()
    memb_by_month = load_membership_lookup()
    betas = load_preformation_betas()
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)

    monthly_rows = []
    series = defaultdict(list)

    for m in months:
        ys = []
        x_ln_size = []
        x_ln_bm = []
        x_b_smb = []
        x_b_hml = []

        for rec in memb_by_month.get(m, []):
            stk = rec['Stkcd']
            ret = master.get((m, stk), {}).get('stock_excess_ret')
            b = betas.get((rec['form_year'], stk))
            if ret is None or b is None:
                continue

            ys.append(ret)
            x_ln_size.append(rec['ln_size'])
            x_ln_bm.append(rec['ln_be_me'])
            x_b_smb.append(b['beta_smb'])
            x_b_hml.append(b['beta_hml'])

        if len(ys) < 10:
            continue

        res = ols(ys, [x_ln_size, x_ln_bm, x_b_smb, x_b_hml])
        if res is None:
            continue

        b0, b1, b2, b3, b4 = res['beta']
        monthly_rows.append({
            'Trdmnt': m,
            'n_stocks': len(ys),
            'lambda_0': b0,
            'lambda_ln_size': b1,
            'lambda_ln_be_me': b2,
            'lambda_beta_smb': b3,
            'lambda_beta_hml': b4,
        })

        series['intercept'].append(b0)
        series['ln_size'].append(b1)
        series['ln_be_me'].append(b2)
        series['beta_smb'].append(b3)
        series['beta_hml'].append(b4)

    summary_rows = []
    n_months = len(monthly_rows)
    avg_n = (sum(r['n_stocks'] for r in monthly_rows) / n_months) if n_months > 0 else None
    order = ['intercept', 'ln_size', 'ln_be_me', 'beta_smb', 'beta_hml']
    for c in order:
        mu, t = nw_tstat_mean(series[c], lag=cfg.NW_LAG)
        summary_rows.append({
            'model': 'DT_FM_chars_and_loadings',
            'coef': c,
            'avg_slope': '' if mu is None else mu,
            'n_months': n_months,
            'nw12_tstat': '' if t is None else t,
            'signif': significance_from_t(t),
            'avg_n_stocks': '' if avg_n is None else avg_n,
        })

    write_csv(
        cfg.OUTPUT_DIR / 'dt_fm_monthly_slopes.csv',
        ['Trdmnt', 'n_stocks', 'lambda_0', 'lambda_ln_size', 'lambda_ln_be_me', 'lambda_beta_smb', 'lambda_beta_hml'],
        monthly_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'table_dt_fama_macbeth_chars_loadings.csv',
        ['model', 'coef', 'avg_slope', 'n_months', 'nw12_tstat', 'signif', 'avg_n_stocks'],
        summary_rows,
    )

    print('Done:', cfg.OUTPUT_DIR / 'dt_fm_monthly_slopes.csv')
    print('Done:', cfg.OUTPUT_DIR / 'table_dt_fama_macbeth_chars_loadings.csv')


if __name__ == '__main__':
    main()
