import csv
from pathlib import Path
import importlib.util

from ff_utils import build_portfolio_time_series, load_master_lookup, ols_beta


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def portfolio_summary(port_prefix, port_col, out_file):
    ret_ts, ex_ts, avg_size = build_portfolio_time_series(port_col)
    _, market_ex = load_master_lookup()

    # portfolio-level characteristic averages from formation file
    char_acc = {}
    with open(cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            p = row.get(port_col) or ''
            if not p:
                continue
            if p not in char_acc:
                char_acc[p] = {'ln_size': [], 'ln_be_me': []}

            ln_size = row.get('ln_size')
            ln_be_me = row.get('ln_be_me')
            if ln_size not in (None, ''):
                char_acc[p]['ln_size'].append(float(ln_size))
            if ln_be_me not in (None, ''):
                char_acc[p]['ln_be_me'].append(float(ln_be_me))

    ports = [f'{port_prefix}{i}' for i in range(1, 11)]
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'portfolio',
            'avg_monthly_return_pct',
            'post_ranking_beta',
            'avg_ln_me',
            'avg_ln_be_me',
            'avg_size',
        ])

        for p in ports:
            ts_r = ret_ts.get(p, {})
            ts_ex = ex_ts.get(p, {})

            avg_ret = None
            if ts_r:
                vals = list(ts_r.values())
                avg_ret = 100.0 * (sum(vals) / len(vals))

            xs = []
            ys = []
            for m in sorted(ts_ex.keys(), key=cfg.month_to_int):
                mx = market_ex.get(m)
                if mx is None:
                    continue
                xs.append(mx)
                ys.append(ts_ex[m])
            pbeta = ols_beta(xs, ys, min_obs=24)

            p_chars = char_acc.get(p, {})
            ln_me_vals = p_chars.get('ln_size', [])
            ln_beme_vals = p_chars.get('ln_be_me', [])
            avg_ln_me = (sum(ln_me_vals) / len(ln_me_vals)) if ln_me_vals else None
            avg_ln_be_me = (sum(ln_beme_vals) / len(ln_beme_vals)) if ln_beme_vals else None

            w.writerow([
                p,
                '' if avg_ret is None else f'{avg_ret:.3f}',
                '' if pbeta is None else f'{pbeta:.4f}',
                '' if avg_ln_me is None else f'{avg_ln_me:.4f}',
                '' if avg_ln_be_me is None else f'{avg_ln_be_me:.4f}',
                '' if p not in avg_size else f"{avg_size[p]:.2f}",
            ])


def main():
    out_size = cfg.OUTPUT_DIR / 'table_ii_size_only.csv'
    out_beta = cfg.OUTPUT_DIR / 'table_ii_beta_only.csv'

    portfolio_summary('S', 'port_size', out_size)
    portfolio_summary('B', 'port_beta', out_beta)

    print('Done:', out_size)
    print('Done:', out_beta)


if __name__ == '__main__':
    main()
