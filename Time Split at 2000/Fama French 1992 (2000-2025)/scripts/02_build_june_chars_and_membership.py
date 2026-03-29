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


def decile_map(value_items):
    # value_items: list[(key, value)]
    pairs = sorted(value_items, key=lambda x: (x[1], x[0]))
    n = len(pairs)
    out = {}
    if n == 0:
        return out
    for i, (k, _) in enumerate(pairs, start=1):
        d = int((i - 1) * 10 / n) + 1
        if d > 10:
            d = 10
        out[k] = d
    return out


def load_master_maps():
    master_file = cfg.OUTPUT_DIR / 'master_panel_200001_202512.csv'
    stock_ex = defaultdict(dict)
    stock_size = defaultdict(dict)
    market_ex = {}

    with open(master_file, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            stk = row['Stkcd']
            m = row['Trdmnt']
            stock_size[stk][m] = float(row['Msmvttl'])

            sx = to_float(row['stock_excess_ret'])
            if sx is not None:
                stock_ex[stk][m] = sx

            mx = to_float(row['market_excess_ret'])
            if mx is not None and m not in market_ex:
                market_ex[m] = mx

    return stock_ex, stock_size, market_ex


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


def rolling_beta_at_month(stock_ex_map, market_ex_map, end_month, window=60, min_obs=24):
    end_i = cfg.month_to_int(end_month)
    start_i = end_i - window + 1

    xs = []
    ys = []
    for m, y in stock_ex_map.items():
        mi = cfg.month_to_int(m)
        if start_i <= mi <= end_i:
            x = market_ex_map.get(m)
            if x is not None:
                xs.append(x)
                ys.append(y)

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


def main():
    stock_ex, stock_size, market_ex = load_master_maps()
    be_map = load_book_equity_a_statement()

    june_chars = {}  # (form_year, stk) -> dict

    for y in range(1999, 2026):
        form_month = f'{y:04d}-06'
        size_items = []
        beta_items = []
        beme_items = []

        rows = {}
        for stk, smap in stock_size.items():
            size = smap.get(form_month)
            if size is None or size <= 0:
                continue

            beta = rolling_beta_at_month(
                stock_ex.get(stk, {}),
                market_ex,
                form_month,
                window=cfg.BETA_WINDOW,
                min_obs=cfg.BETA_MIN_OBS,
            )

            be = be_map.get(stk, {}).get(y - 1)
            beme = None
            ln_beme = None
            if be is not None and size > 0:
                beme = be / size
                if beme > 0:
                    import math
                    ln_beme = math.log(beme)

            row = {
                'form_year': y,
                'form_month': form_month,
                'Stkcd': stk,
                'size': size,
                'ln_size': __import__('math').log(size),
                'beta': beta,
                'book_equity': be,
                'be_me': beme,
                'ln_be_me': ln_beme,
                'size_decile': None,
                'beta_decile': None,
                'beme_decile': None,
                'size_beta_decile': None,
                'size_beme_decile': None,
            }
            rows[stk] = row
            size_items.append((stk, size))
            if beta is not None:
                beta_items.append((stk, beta))
            if ln_beme is not None:
                beme_items.append((stk, ln_beme))

        size_dec = decile_map(size_items)
        beta_dec = decile_map(beta_items)
        beme_dec = decile_map(beme_items)

        # conditional deciles within size groups
        by_size_beta = defaultdict(list)
        by_size_beme = defaultdict(list)

        for stk, row in rows.items():
            sd = size_dec.get(stk)
            row['size_decile'] = sd
            row['beta_decile'] = beta_dec.get(stk)
            row['beme_decile'] = beme_dec.get(stk)

            if sd is not None and row['beta'] is not None:
                by_size_beta[sd].append((stk, row['beta']))
            if sd is not None and row['ln_be_me'] is not None:
                by_size_beme[sd].append((stk, row['ln_be_me']))

        size_beta_dec = {}
        for sd, vals in by_size_beta.items():
            tmp = decile_map(vals)
            for stk, d in tmp.items():
                size_beta_dec[(sd, stk)] = d

        size_beme_dec = {}
        for sd, vals in by_size_beme.items():
            tmp = decile_map(vals)
            for stk, d in tmp.items():
                size_beme_dec[(sd, stk)] = d

        for stk, row in rows.items():
            sd = row['size_decile']
            row['size_beta_decile'] = size_beta_dec.get((sd, stk)) if sd is not None else None
            row['size_beme_decile'] = size_beme_dec.get((sd, stk)) if sd is not None else None
            june_chars[(y, stk)] = row

    june_file = cfg.OUTPUT_DIR / 'june_characteristics.csv'
    with open(june_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'form_year', 'form_month', 'Stkcd', 'beta', 'size', 'ln_size',
            'book_equity', 'be_me', 'ln_be_me',
            'size_decile', 'beta_decile', 'beme_decile', 'size_beta_decile', 'size_beme_decile'
        ])
        for k in sorted(june_chars.keys()):
            row = june_chars[k]
            w.writerow([
                row['form_year'], row['form_month'], row['Stkcd'],
                '' if row['beta'] is None else f"{row['beta']:.10f}",
                f"{row['size']:.6f}",
                f"{row['ln_size']:.10f}",
                '' if row['book_equity'] is None else f"{row['book_equity']:.6f}",
                '' if row['be_me'] is None else f"{row['be_me']:.10f}",
                '' if row['ln_be_me'] is None else f"{row['ln_be_me']:.10f}",
                '' if row['size_decile'] is None else row['size_decile'],
                '' if row['beta_decile'] is None else row['beta_decile'],
                '' if row['beme_decile'] is None else row['beme_decile'],
                '' if row['size_beta_decile'] is None else row['size_beta_decile'],
                '' if row['size_beme_decile'] is None else row['size_beme_decile'],
            ])

    membership_file = cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv'
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    with open(membership_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'Trdmnt', 'form_year', 'Stkcd',
            'beta', 'size', 'ln_size', 'be_me', 'ln_be_me',
            'size_decile', 'beta_decile', 'beme_decile',
            'port_size', 'port_beta', 'port_size_beta', 'port_size_beme'
        ])

        for m in months:
            fy = cfg.formation_year_for_return_month(m)
            for (y, stk), row in june_chars.items():
                if y != fy:
                    continue
                sd = row['size_decile']
                bd = row['beta_decile']
                md = row['beme_decile']
                sbd = row['size_beta_decile']
                smd = row['size_beme_decile']

                port_size = f'S{sd}' if sd is not None else ''
                port_beta = f'B{bd}' if bd is not None else ''
                port_size_beta = f'S{sd}B{sbd}' if (sd is not None and sbd is not None) else ''
                port_size_beme = f'S{sd}M{smd}' if (sd is not None and smd is not None) else ''

                w.writerow([
                    m, fy, stk,
                    '' if row['beta'] is None else f"{row['beta']:.10f}",
                    f"{row['size']:.6f}",
                    f"{row['ln_size']:.10f}",
                    '' if row['be_me'] is None else f"{row['be_me']:.10f}",
                    '' if row['ln_be_me'] is None else f"{row['ln_be_me']:.10f}",
                    '' if sd is None else sd,
                    '' if bd is None else bd,
                    '' if md is None else md,
                    port_size, port_beta, port_size_beta, port_size_beme,
                ])

    print('Done:', june_file)
    print('Done:', membership_file)


if __name__ == '__main__':
    main()
