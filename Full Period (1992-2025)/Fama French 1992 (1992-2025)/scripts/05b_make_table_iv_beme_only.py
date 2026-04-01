import csv
from collections import defaultdict
from pathlib import Path
import importlib.util

from ff_utils import load_master_lookup, ols_beta


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, '') else None


def main():
    master, market_ex = load_master_lookup()

    members = defaultdict(list)  # (month, portfolio) -> stocks
    avg_size_acc = defaultdict(list)
    char_acc = defaultdict(lambda: {'ln_size': [], 'ln_be_me': []})

    with open(cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            d = row.get('beme_decile')
            if d in (None, ''):
                continue
            p = f'M{int(d)}'
            m = row['Trdmnt']
            stk = row['Stkcd']
            members[(m, p)].append(stk)
            s = to_float(row.get('size'))
            if s is not None and s > 0:
                avg_size_acc[p].append(s)

            ln_size = to_float(row.get('ln_size'))
            ln_be_me = to_float(row.get('ln_be_me'))
            if ln_size is not None:
                char_acc[p]['ln_size'].append(ln_size)
            if ln_be_me is not None:
                char_acc[p]['ln_be_me'].append(ln_be_me)

    ret_ts = defaultdict(dict)
    ex_ts = defaultdict(dict)
    months = sorted({m for m, _ in members.keys()}, key=cfg.month_to_int)
    for m in months:
        pm = cfg.prev_month(m)
        for p in [f'M{i}' for i in range(1, 11)]:
            stocks = members.get((m, p), [])
            if not stocks:
                continue
            num = 0.0
            num_ex = 0.0
            den = 0.0
            for stk in stocks:
                cur = master.get((m, stk))
                prv = master.get((pm, stk))
                if not cur:
                    continue
                r = cur['ret']
                ex = cur['stock_ex']
                if r is None:
                    continue
                w = prv['size'] if prv and prv['size'] and prv['size'] > 0 else None
                if w is None:
                    w = cur['size'] if cur['size'] and cur['size'] > 0 else None
                if w is None:
                    continue
                num += w * r
                if ex is not None:
                    num_ex += w * ex
                den += w
            if den > 0:
                ret_ts[p][m] = num / den
                ex_ts[p][m] = num_ex / den

    out_file = cfg.OUTPUT_DIR / 'table_iv_beme_only.csv'
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
        for p in [f'M{i}' for i in range(1, 11)]:
            ts = ret_ts.get(p, {})
            avg_ret = ''
            if ts:
                avg_ret = f"{100.0 * (sum(ts.values()) / len(ts)):.3f}"

            xs = []
            ys = []
            for m in sorted(ex_ts.get(p, {}).keys(), key=cfg.month_to_int):
                mx = market_ex.get(m)
                if mx is None:
                    continue
                xs.append(mx)
                ys.append(ex_ts[p][m])
            pbeta = ols_beta(xs, ys, min_obs=24)

            avg_ln_me = ''
            ln_me_vals = char_acc[p]['ln_size']
            if ln_me_vals:
                avg_ln_me = f"{sum(ln_me_vals) / len(ln_me_vals):.4f}"

            avg_ln_be_me = ''
            ln_beme_vals = char_acc[p]['ln_be_me']
            if ln_beme_vals:
                avg_ln_be_me = f"{sum(ln_beme_vals) / len(ln_beme_vals):.4f}"

            avg_size = ''
            vals = avg_size_acc.get(p, [])
            if vals:
                avg_size = f"{sum(vals)/len(vals):.2f}"
            w.writerow([
                p,
                avg_ret,
                '' if pbeta is None else f"{pbeta:.4f}",
                avg_ln_me,
                avg_ln_be_me,
                avg_size,
            ])

    print('Done:', out_file)


if __name__ == '__main__':
    main()
