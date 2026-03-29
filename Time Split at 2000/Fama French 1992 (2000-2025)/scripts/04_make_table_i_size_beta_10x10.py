import csv
from pathlib import Path
import importlib.util

from ff_utils import build_portfolio_time_series, load_master_lookup, ols_beta


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def main():
    ret_ts, ex_ts, avg_size = build_portfolio_time_series('port_size_beta')
    _, market_ex = load_master_lookup()

    out_file = cfg.OUTPUT_DIR / 'table_i_size_beta_10x10.csv'
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'size_decile', 'beta_decile_within_size', 'portfolio',
            'avg_monthly_return_pct', 'post_ranking_beta', 'avg_size'
        ])

        for s in range(1, 11):
            for b in range(1, 11):
                p = f'S{s}B{b}'
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

                w.writerow([
                    s, b, p,
                    '' if avg_ret is None else f'{avg_ret:.3f}',
                    '' if pbeta is None else f'{pbeta:.4f}',
                    '' if p not in avg_size else f"{avg_size[p]:.2f}",
                ])

    print('Done:', out_file)


if __name__ == '__main__':
    main()
