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


def load_master_lookup():
    fpath = cfg.OUTPUT_DIR / 'master_panel_200001_202512.csv'
    out = {}
    market_ex = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row['Trdmnt'], row['Stkcd'])
            out[key] = {
                'ret': to_float(row['Mretwd']),
                'size': to_float(row['Msmvttl']),
                'stock_ex': to_float(row['stock_excess_ret']),
            }
            mx = to_float(row['market_excess_ret'])
            if mx is not None and row['Trdmnt'] not in market_ex:
                market_ex[row['Trdmnt']] = mx
    return out, market_ex


def load_membership_rows():
    fpath = cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv'
    rows = []
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def ols_beta(xs, ys, min_obs=24):
    n = len(xs)
    if n < min_obs:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = 0.0
    sxy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx
        sxx += dx * dx
        sxy += dx * (y - my)
    if sxx <= 0:
        return None
    return sxy / sxx


def build_portfolio_time_series(port_col):
    master, _ = load_master_lookup()
    rows = load_membership_rows()

    by_month_port = defaultdict(list)
    avg_size_acc = defaultdict(list)

    for row in rows:
        p = row.get(port_col) or ''
        if not p:
            continue
        m = row['Trdmnt']
        stk = row['Stkcd']
        by_month_port[(m, p)].append(stk)

        size_form = to_float(row.get('size'))
        if size_form is not None and size_form > 0:
            avg_size_acc[p].append(size_form)

    ret_ts = defaultdict(dict)
    ex_ts = defaultdict(dict)

    months = sorted({m for m, _ in by_month_port.keys()}, key=cfg.month_to_int)
    for m in months:
        pm = cfg.prev_month(m)
        ports = sorted({p for mm, p in by_month_port.keys() if mm == m})
        for p in ports:
            members = by_month_port[(m, p)]
            num_ret = 0.0
            num_ex = 0.0
            den = 0.0
            for stk in members:
                cur = master.get((m, stk))
                prev = master.get((pm, stk))
                if not cur:
                    continue
                r = cur['ret']
                ex = cur['stock_ex']
                w = prev['size'] if prev and prev['size'] and prev['size'] > 0 else None
                if w is None:
                    w = cur['size'] if cur['size'] and cur['size'] > 0 else None
                if w is None or r is None:
                    continue
                den += w
                num_ret += w * r
                if ex is not None:
                    num_ex += w * ex
            if den > 0:
                ret_ts[p][m] = num_ret / den
                ex_ts[p][m] = num_ex / den

    avg_size = {}
    for p, vals in avg_size_acc.items():
        if vals:
            avg_size[p] = sum(vals) / len(vals)

    return ret_ts, ex_ts, avg_size
