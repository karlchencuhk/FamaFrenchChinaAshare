import csv
from collections import defaultdict
from pathlib import Path
import importlib.util

_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, '') else None


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def build_table1_size_bm_grid():
    rows = read_csv(cfg.SRC_OUTPUT / 'ff3_port25_monthly.csv')
    acc = defaultdict(lambda: {'ret': [], 'n': []})

    for r in rows:
        s = int(r['size_quintile'])
        b = int(r['bm_quintile'])
        ex = to_float(r.get('excess_return'))
        n = to_float(r.get('n_stocks'))
        if ex is not None:
            acc[(s, b)]['ret'].append(ex)
        if n is not None:
            acc[(s, b)]['n'].append(n)

    out = []
    for s in range(1, 6):
        for b in range(1, 6):
            d = acc[(s, b)]
            mu = (sum(d['ret']) / len(d['ret'])) if d['ret'] else None
            n_avg = (sum(d['n']) / len(d['n'])) if d['n'] else None
            out.append({
                'size_quintile': s,
                'bm_quintile': b,
                'avg_excess_return_pct': '' if mu is None else mu * 100.0,
                'avg_n_stocks': '' if n_avg is None else n_avg,
            })

    write_csv(
        cfg.OUT_DIR / 'table_1_ff1993_size_bm_5x5.csv',
        ['size_quintile', 'bm_quintile', 'avg_excess_return_pct', 'avg_n_stocks'],
        out,
    )


def build_table2_factor_summary():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_1_factor_summary.csv')
    out = []
    for r in rows:
        out.append({
            'factor': r['factor'],
            'mean_monthly_pct': r['mean_monthly_pct'],
            'std_monthly_pct': r['std_monthly_pct'],
            'nw12_tstat_mean': r['nw12_tstat_mean'],
            'annualized_mean_pct': r['annualized_mean_pct'],
            'annualized_vol_pct': r['annualized_vol_pct'],
            'n_months': r['n_months'],
        })
    write_csv(
        cfg.OUT_DIR / 'table_2_ff1993_factor_summary.csv',
        ['factor', 'mean_monthly_pct', 'std_monthly_pct', 'nw12_tstat_mean', 'annualized_mean_pct', 'annualized_vol_pct', 'n_months'],
        out,
    )


def build_table6_stock_regressions():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_5_25port_ff3_regressions.csv')
    write_csv(
        cfg.OUT_DIR / 'table_6a_ff1993_stock_regressions.csv',
        ['portfolio', 'size_quintile', 'bm_quintile', 'alpha_pct', 'nw12_t_alpha', 'beta_mkt', 'nw12_t_mkt', 'beta_smb', 'nw12_t_smb', 'beta_hml', 'nw12_t_hml', 'r2', 'n_months'],
        rows,
    )


def build_table9_alpha_analogue():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_5_25port_ff3_regressions.csv')
    summary = read_csv(cfg.SRC_OUTPUT / 'table_6_alpha_diagnostics.csv')
    pe = read_csv(cfg.SRC_OUTPUT / 'table_7_pricing_errors.csv')

    out_a = []
    for r in rows:
        out_a.append({
            'portfolio': r['portfolio'],
            'alpha_pct': r['alpha_pct'],
            'nw12_t_alpha': r['nw12_t_alpha'],
            'abs_alpha_pct': '' if r['alpha_pct'] in (None, '') else abs(float(r['alpha_pct'])),
        })

    write_csv(
        cfg.OUT_DIR / 'table_9a_ff1993_alpha_by_portfolio.csv',
        ['portfolio', 'alpha_pct', 'nw12_t_alpha', 'abs_alpha_pct'],
        out_a,
    )

    summ_map = {r['metric']: r['value'] for r in summary}
    rmse = ''
    mae = ''
    for r in pe:
        if r.get('portfolio') == 'SUMMARY':
            rmse = r.get('rmse_pct', '')
            mae = r.get('mae_pct', '')
            break

    out_c = [
        {'metric': 'n_portfolios', 'value': summ_map.get('n_portfolios', '')},
        {'metric': 'n_sig_10pct', 'value': summ_map.get('n_sig_10pct', '')},
        {'metric': 'n_sig_5pct', 'value': summ_map.get('n_sig_5pct', '')},
        {'metric': 'n_sig_1pct', 'value': summ_map.get('n_sig_1pct', '')},
        {'metric': 'mean_alpha_pct', 'value': summ_map.get('mean_alpha_pct', '')},
        {'metric': 'mean_abs_alpha_pct', 'value': summ_map.get('mean_abs_alpha_pct', '')},
        {'metric': 'max_abs_alpha_pct', 'value': summ_map.get('max_abs_alpha_pct', '')},
        {'metric': 'rmse_pct', 'value': rmse},
        {'metric': 'mae_pct', 'value': mae},
        {'metric': 'joint_test_note', 'value': 'GRS not implemented; diagnostics shown as FF1993 Table 9 analogue.'},
    ]

    write_csv(
        cfg.OUT_DIR / 'table_9c_ff1993_alpha_diagnostics.csv',
        ['metric', 'value'],
        out_c,
    )


def main():
    build_table1_size_bm_grid()
    build_table2_factor_summary()
    build_table6_stock_regressions()
    build_table9_alpha_analogue()
    print('Done:', cfg.OUT_DIR)


if __name__ == '__main__':
    main()
