import csv
from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import to_float, assign_bins_rank, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_monthly_lookup():
    # from master panel
    fpath = cfg.OUTPUT_DIR / 'master_panel_199207_202512.csv'
    out = {}
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out[(row['Trdmnt'], row['Stkcd'])] = {
                'ret': to_float(row['Mretwd']),
                'excess_ret': to_float(row.get('stock_excess_ret')),
                'size': to_float(row['Msmvttl']),
            }
    return out


def load_membership_rows():
    rows = []
    fpath = cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv'
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                'Trdmnt': row['Trdmnt'],
                'Stkcd': row['Stkcd'],
                'form_year': int(row['form_year']),
                'size_tercile': int(row['size_tercile']),
                'bm_tercile': int(row['bm_tercile']),
                'char_port': row.get('char_port', f"SZ{row['size_tercile']}BM{row['bm_tercile']}"),
            })
    return rows


def build_beta_hml_quintiles_by_year_char_port(membership, betas):
    # For each formation year and characteristic portfolio (Size tercile x BM tercile),
    # sort stocks on pre-formation beta_hml into quintiles (1..5).
    # key in output: (form_year, Stkcd) -> beta_hml_q5
    by_group = defaultdict(list)
    seen = set()

    for row in membership:
        uniq = (row['form_year'], row['Stkcd'])
        if uniq in seen:
            continue
        seen.add(uniq)

        b = betas.get(uniq)
        if b is None:
            continue

        g = (row['form_year'], row['size_tercile'], row['bm_tercile'])
        by_group[g].append((row['Stkcd'], b['beta_hml']))

    out = {}
    for g, vals in by_group.items():
        hml_q = assign_bins_rank(vals, cuts=[0.2, 0.4, 0.6, 0.8])
        y = g[0]
        for stk, _ in vals:
            q = hml_q.get(stk)
            if q is None:
                continue
            out[(y, stk)] = q

    return out


def load_betas():
    b = {}
    fpath = cfg.OUTPUT_DIR / 'preformation_betas.csv'
    with open(fpath, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            fy = int(row['form_year'])
            stk = row['Stkcd']
            bs = to_float(row.get('beta_smb'))
            bh = to_float(row.get('beta_hml'))
            if bs is None or bh is None:
                continue
            b[(fy, stk)] = {
                'beta_smb': bs,
                'beta_hml': bh,
            }
    return b


def build_beta_bins_by_year(membership, betas):
    # independent yearly terciles for beta_smb and beta_hml
    by_year = defaultdict(list)
    for row in membership:
        key = (row['form_year'], row['Stkcd'])
        b = betas.get(key)
        if b is None:
            continue
        by_year[row['form_year']].append((row['Stkcd'], b['beta_smb'], b['beta_hml']))

    out = {}
    for y, vals in by_year.items():
        smb_items = [(stk, bs) for stk, bs, _ in vals]
        hml_items = [(stk, bh) for stk, _, bh in vals]
        smb_bin = assign_bins_rank(smb_items, cuts=[1 / 3, 2 / 3])
        hml_bin = assign_bins_rank(hml_items, cuts=[1 / 3, 2 / 3])

        for stk, _, _ in vals:
            sbin = smb_bin.get(stk)
            hbin = hml_bin.get(stk)
            if sbin is None or hbin is None:
                continue
            out[(y, stk)] = {'beta_smb_bin': sbin, 'beta_hml_bin': hbin}

    return out


def aggregate_portfolio_returns(membership_ext, monthly_lookup):
    # outputs monthly VW returns for 3x3 grids
    size_rows = []
    bm_rows = []

    by_month_size = defaultdict(list)
    by_month_bm = defaultdict(list)

    for row in membership_ext:
        m = row['Trdmnt']
        by_month_size[(m, row['size_tercile'], row['beta_smb_bin'])].append(row['Stkcd'])
        by_month_bm[(m, row['bm_tercile'], row['beta_hml_bin'])].append(row['Stkcd'])

    months = sorted({r['Trdmnt'] for r in membership_ext}, key=cfg.month_to_int)

    # size x beta_smb
    for m in months:
        pm = cfg.prev_month(m)
        for s in (1, 2, 3):
            for b in (1, 2, 3):
                members = by_month_size.get((m, s, b), [])
                num = 0.0
                den = 0.0
                n_used = 0
                for stk in members:
                    cur = monthly_lookup.get((m, stk))
                    prev = monthly_lookup.get((pm, stk))
                    if not cur:
                        continue
                    r = cur['ret']
                    if r is None:
                        continue
                    w = prev['size'] if prev and prev['size'] and prev['size'] > 0 else None
                    if w is None:
                        w = cur['size'] if cur['size'] and cur['size'] > 0 else None
                    if w is None:
                        continue
                    den += w
                    num += w * r
                    n_used += 1
                rv = (num / den) if den > 0 else None
                size_rows.append({
                    'Trdmnt': m,
                    'size_tercile': s,
                    'beta_smb_bin': b,
                    'portfolio': f'SZ{s}_BSMB{b}',
                    'vw_return': '' if rv is None else rv,
                    'n_stocks': n_used,
                })

    # bm x beta_hml
    for m in months:
        pm = cfg.prev_month(m)
        for bm in (1, 2, 3):
            for b in (1, 2, 3):
                members = by_month_bm.get((m, bm, b), [])
                num = 0.0
                den = 0.0
                n_used = 0
                for stk in members:
                    cur = monthly_lookup.get((m, stk))
                    prev = monthly_lookup.get((pm, stk))
                    if not cur:
                        continue
                    r = cur['ret']
                    if r is None:
                        continue
                    w = prev['size'] if prev and prev['size'] and prev['size'] > 0 else None
                    if w is None:
                        w = cur['size'] if cur['size'] and cur['size'] > 0 else None
                    if w is None:
                        continue
                    den += w
                    num += w * r
                    n_used += 1
                rv = (num / den) if den > 0 else None
                bm_rows.append({
                    'Trdmnt': m,
                    'bm_tercile': bm,
                    'beta_hml_bin': b,
                    'portfolio': f'BM{bm}_BHML{b}',
                    'vw_return': '' if rv is None else rv,
                    'n_stocks': n_used,
                })

    return size_rows, bm_rows


def build_45port_hml_quintile_table(membership_ext_45, monthly_lookup):
    by_month = defaultdict(list)
    for row in membership_ext_45:
        by_month[(row['Trdmnt'], row['size_tercile'], row['bm_tercile'], row['beta_hml_q5'])].append(row['Stkcd'])

    months = sorted({r['Trdmnt'] for r in membership_ext_45}, key=cfg.month_to_int)
    monthly_rows = []

    for m in months:
        pm = cfg.prev_month(m)
        for s in (1, 2, 3):
            for bm in (1, 2, 3):
                char_port = f'SZ{s}BM{bm}'
                for q in (1, 2, 3, 4, 5):
                    members = by_month.get((m, s, bm, q), [])
                    num = 0.0
                    den = 0.0
                    n_used = 0
                    for stk in members:
                        cur = monthly_lookup.get((m, stk))
                        prev = monthly_lookup.get((pm, stk))
                        if not cur:
                            continue
                        r = cur['excess_ret']
                        if r is None:
                            continue
                        w = prev['size'] if prev and prev['size'] and prev['size'] > 0 else None
                        if w is None:
                            w = cur['size'] if cur['size'] and cur['size'] > 0 else None
                        if w is None:
                            continue
                        den += w
                        num += w * r
                        n_used += 1

                    rv = (num / den) if den > 0 else None
                    monthly_rows.append({
                        'Trdmnt': m,
                        'size_tercile': s,
                        'bm_tercile': bm,
                        'char_port': char_port,
                        'beta_hml_q5': q,
                        'portfolio': f'{char_port}_BHML{q}',
                        'vw_excess_return': '' if rv is None else rv,
                        'n_stocks': n_used,
                    })

    # Aggregate to mean excess return per portfolio (45 rows)
    grouped = defaultdict(list)
    n_months_map = defaultdict(int)
    for row in monthly_rows:
        key = (row['size_tercile'], row['bm_tercile'], row['char_port'], row['beta_hml_q5'])
        v = to_float(row['vw_excess_return'])
        if v is not None:
            grouped[key].append(v)
            n_months_map[key] += 1

    mean_rows = []
    for s in (1, 2, 3):
        for bm in (1, 2, 3):
            char_port = f'SZ{s}BM{bm}'
            for q in (1, 2, 3, 4, 5):
                key = (s, bm, char_port, q)
                vals = grouped.get(key, [])
                mu = (sum(vals) / len(vals)) if vals else None
                mean_rows.append({
                    'size_tercile': s,
                    'bm_tercile': bm,
                    'char_port': char_port,
                    'beta_hml_q5': q,
                    'mean_excess_monthly_pct': '' if mu is None else mu * 100.0,
                    'n_months': n_months_map.get(key, 0),
                })

    return monthly_rows, mean_rows


def main():
    print('Step 4/8: building Daniel-Titman 3x3 portfolio returns...')

    monthly_lookup = load_monthly_lookup()
    membership = load_membership_rows()
    betas = load_betas()

    beta_bins = build_beta_bins_by_year(membership, betas)
    beta_hml_q5 = build_beta_hml_quintiles_by_year_char_port(membership, betas)

    membership_ext = []
    membership_ext_45 = []
    for row in membership:
        key = (row['form_year'], row['Stkcd'])
        bb = beta_bins.get(key)
        if bb is None:
            continue
        membership_ext.append({
            **row,
            'beta_smb_bin': bb['beta_smb_bin'],
            'beta_hml_bin': bb['beta_hml_bin'],
        })

        q5 = beta_hml_q5.get(key)
        if q5 is not None:
            membership_ext_45.append({
                **row,
                'beta_hml_q5': q5,
            })

    size_rows, bm_rows = aggregate_portfolio_returns(membership_ext, monthly_lookup)
    dt45_monthly_rows, dt45_mean_rows = build_45port_hml_quintile_table(membership_ext_45, monthly_lookup)

    write_csv(
        cfg.OUTPUT_DIR / 'dt_membership_with_betas.csv',
        ['Trdmnt', 'Stkcd', 'form_year', 'size_tercile', 'bm_tercile', 'char_port', 'beta_smb_bin', 'beta_hml_bin'],
        membership_ext,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'dt_size_3x3_monthly.csv',
        ['Trdmnt', 'size_tercile', 'beta_smb_bin', 'portfolio', 'vw_return', 'n_stocks'],
        size_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'dt_bm_3x3_monthly.csv',
        ['Trdmnt', 'bm_tercile', 'beta_hml_bin', 'portfolio', 'vw_return', 'n_stocks'],
        bm_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'dt_char_hml5_45_monthly.csv',
        ['Trdmnt', 'size_tercile', 'bm_tercile', 'char_port', 'beta_hml_q5', 'portfolio', 'vw_excess_return', 'n_stocks'],
        dt45_monthly_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'table_dt_45port_mean_excess.csv',
        ['size_tercile', 'bm_tercile', 'char_port', 'beta_hml_q5', 'mean_excess_monthly_pct', 'n_months'],
        dt45_mean_rows,
    )

    print('Done:', cfg.OUTPUT_DIR / 'dt_membership_with_betas.csv')
    print('Done:', cfg.OUTPUT_DIR / 'dt_size_3x3_monthly.csv')
    print('Done:', cfg.OUTPUT_DIR / 'dt_bm_3x3_monthly.csv')
    print('Done:', cfg.OUTPUT_DIR / 'dt_char_hml5_45_monthly.csv')
    print('Done:', cfg.OUTPUT_DIR / 'table_dt_45port_mean_excess.csv')


if __name__ == '__main__':
    main()
