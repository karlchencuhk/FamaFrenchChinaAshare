import csv
from pathlib import Path
import importlib.util

from ff_utils import build_portfolio_time_series


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def main():
    ret_ts, _, avg_size = build_portfolio_time_series('port_size_beme')

    out_file = cfg.OUTPUT_DIR / 'table_v_size_beme_10x10.csv'
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'size_decile', 'beme_decile_within_size', 'portfolio',
            'avg_monthly_return_pct', 'avg_size'
        ])

        for s in range(1, 11):
            for m in range(1, 11):
                p = f'S{s}M{m}'
                ts_r = ret_ts.get(p, {})
                avg_ret = None
                if ts_r:
                    vals = list(ts_r.values())
                    avg_ret = 100.0 * (sum(vals) / len(vals))

                w.writerow([
                    s, m, p,
                    '' if avg_ret is None else f'{avg_ret:.3f}',
                    '' if p not in avg_size else f"{avg_size[p]:.2f}",
                ])

    print('Done:', out_file)


if __name__ == '__main__':
    main()
