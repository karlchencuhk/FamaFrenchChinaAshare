from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import iter_clean_csv, to_float, assign_bins_rank, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_rf_monthly_effective():
    rf = {}
    rf_date = {}
    for row in iter_clean_csv(cfg.RF_FILE):
        d = row.get('Clsdt')
        val = to_float(row.get('Nrrmtdt'))
        if not d or val is None:
            continue
        m = d[:7]
        prev_d = rf_date.get(m)
        if prev_d is None or d > prev_d:
            rf_date[m] = d
            rf[m] = val / 100.0
    return rf


def load_market_returns():
    mkt = {}
    for row in iter_clean_csv(cfg.MKT_FILE):
        if row.get('Markettype') != '5':
            continue
        m = row.get('Trdmnt')
        rv = to_float(row.get('Cmretwdtl'))
        if m and rv is not None:
            mkt[m] = rv
    return mkt


def load_stock_panel():
    stock_ret = {}
    stock_size = {}

    s_i = cfg.month_to_int('1990-12')
    e_i = cfg.month_to_int(cfg.RETURN_END)

    for row in iter_clean_csv(cfg.STOCK_FILE):
        mt = row.get('Markettype')
        if mt not in ('1', '4'):
            continue

        m = row.get('Trdmnt')
        if not m:
            continue
        mi = cfg.month_to_int(m)
        if mi < s_i or mi > e_i:
            continue

        stk = (row.get('Stkcd') or '').zfill(6)
        if not stk:
            continue

        rv = to_float(row.get('Mretwd'))
        sv = to_float(row.get('Msmvttl'))
        if rv is None or sv is None or sv <= 0:
            continue

        stock_ret[(m, stk)] = rv
        stock_size[(m, stk)] = sv

    return stock_ret, stock_size


def load_book_equity_december_a():
    be = defaultdict(dict)
    for row in iter_clean_csv(cfg.BS_FILE):
        if row.get('Typrep') != 'A':
            continue
        acc = row.get('Accper')
        if not acc or not acc.endswith('-12-31'):
            continue

        stk = (row.get('Stkcd') or '').zfill(6)
        if not stk:
            continue

        y = int(acc[:4])
        bv = to_float(row.get('A003100000'))
        if bv is None:
            bv = to_float(row.get('A003000000'))
        if bv is None:
            continue

        be[stk][y] = bv

    return be


def value_weighted_return(stocks, month, stock_ret, stock_size):
    pm = cfg.prev_month(month)
    num = 0.0
    den = 0.0
    n_used = 0
    for stk in stocks:
        r = stock_ret.get((month, stk))
        if r is None:
            continue
        w = stock_size.get((pm, stk))
        if w is None or w <= 0:
            w = stock_size.get((month, stk))
        if w is None or w <= 0:
            continue
        den += w
        num += w * r
        n_used += 1
    if den <= 0:
        return None, 0
    return num / den, n_used


def build_formation_memberships(stock_size, be_map):
    member_2x3 = defaultdict(dict)
    member_char_3x3 = defaultdict(dict)
    june_chars = []

    for y in range(1992, 2026):
        june = f'{y:04d}-06'
        dec_prev = f'{y - 1:04d}-12'

        size_items = []
        bm_items = []
        rec = {}

        for (m, stk), june_size in stock_size.items():
            if m != june:
                continue
            dec_size = stock_size.get((dec_prev, stk))
            be = be_map.get(stk, {}).get(y - 1)
            if dec_size is None or dec_size <= 0:
                continue
            if be is None or be <= 0:
                continue

            bm = be / dec_size
            if bm <= 0:
                continue

            rec[stk] = {
                'form_year': y,
                'Stkcd': stk,
                'size_june': june_size,
                'size_dec_prev': dec_size,
                'book_equity': be,
                'be_me': bm,
            }
            size_items.append((stk, june_size))
            bm_items.append((stk, bm))

        if not rec:
            continue

        size_2 = assign_bins_rank(size_items, cuts=[0.5])
        bm_3_for_ff = assign_bins_rank(bm_items, cuts=[0.3, 0.7])

        size_3 = assign_bins_rank(size_items, cuts=[1 / 3, 2 / 3])
        bm_3 = assign_bins_rank(bm_items, cuts=[1 / 3, 2 / 3])

        for stk, row in rec.items():
            s2 = size_2.get(stk)
            b3ff = bm_3_for_ff.get(stk)
            s3 = size_3.get(stk)
            b3 = bm_3.get(stk)

            if s2 is not None and b3ff is not None:
                size_lbl = 'S' if s2 == 1 else 'B'
                bm_lbl = {1: 'L', 2: 'M', 3: 'H'}[b3ff]
                member_2x3[y][stk] = size_lbl + bm_lbl

            if s3 is not None and b3 is not None:
                member_char_3x3[y][stk] = (s3, b3)

            june_chars.append({
                'form_year': y,
                'Stkcd': stk,
                'size_june': row['size_june'],
                'size_dec_prev': row['size_dec_prev'],
                'book_equity': row['book_equity'],
                'be_me': row['be_me'],
                'size_tercile': s3,
                'bm_tercile': b3,
                'char_port': '' if (s3 is None or b3 is None) else f'SZ{s3}BM{b3}',
                'ff_leg_2x3': member_2x3[y].get(stk, ''),
            })

    return member_2x3, member_char_3x3, june_chars


def build_ff3_factors(member_2x3, stock_ret, stock_size, rf, mkt):
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    legs = ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']

    leg_returns = {leg: {} for leg in legs}
    leg_counts = {leg: {} for leg in legs}

    factor_rows = []
    for m in months:
        fy = cfg.formation_year_for_return_month(m)
        members_2x3 = member_2x3.get(fy, {})

        by_leg = defaultdict(list)
        for stk, leg in members_2x3.items():
            by_leg[leg].append(stk)

        for leg in legs:
            rv, n_used = value_weighted_return(by_leg.get(leg, []), m, stock_ret, stock_size)
            leg_returns[leg][m] = rv
            leg_counts[leg][m] = n_used

        sl = leg_returns['SL'].get(m)
        sm = leg_returns['SM'].get(m)
        sh = leg_returns['SH'].get(m)
        bl = leg_returns['BL'].get(m)
        bm = leg_returns['BM'].get(m)
        bh = leg_returns['BH'].get(m)

        smb = None
        if None not in (sl, sm, sh, bl, bm, bh):
            smb = (sh + sm + sl) / 3.0 - (bh + bm + bl) / 3.0

        hml = None
        if None not in (sh, bh, sl, bl):
            hml = (sh + bh) / 2.0 - (sl + bl) / 2.0

        rf_m = rf.get(m)
        rm = mkt.get(m)
        mkt_rf = (rm - rf_m) if (rm is not None and rf_m is not None) else None

        factor_rows.append({
            'Trdmnt': m,
            'RF': '' if rf_m is None else rf_m,
            'RM': '' if rm is None else rm,
            'MKT_RF': '' if mkt_rf is None else mkt_rf,
            'SMB': '' if smb is None else smb,
            'HML': '' if hml is None else hml,
            'SL': '' if sl is None else sl,
            'SM': '' if sm is None else sm,
            'SH': '' if sh is None else sh,
            'BL': '' if bl is None else bl,
            'BM': '' if bm is None else bm,
            'BH': '' if bh is None else bh,
            'N_SL': leg_counts['SL'].get(m, 0),
            'N_SM': leg_counts['SM'].get(m, 0),
            'N_SH': leg_counts['SH'].get(m, 0),
            'N_BL': leg_counts['BL'].get(m, 0),
            'N_BM': leg_counts['BM'].get(m, 0),
            'N_BH': leg_counts['BH'].get(m, 0),
        })

    return factor_rows


def build_membership_jul_to_jun(member_char_3x3, june_chars):
    june_map = {(int(r['form_year']), r['Stkcd']): r for r in june_chars}
    rows = []
    for m in cfg.all_months(cfg.RETURN_START, cfg.RETURN_END):
        fy = cfg.formation_year_for_return_month(m)
        for stk, (s3, b3) in member_char_3x3.get(fy, {}).items():
            j = june_map.get((fy, stk), {})
            rows.append({
                'Trdmnt': m,
                'Stkcd': stk,
                'form_year': fy,
                'size_tercile': s3,
                'bm_tercile': b3,
                'char_port': f'SZ{s3}BM{b3}',
                'size_june': j.get('size_june', ''),
                'be_me': j.get('be_me', ''),
            })
    return rows


def main():
    print('Step 2/8: building June characteristics, monthly membership, and FF3 factors...')

    rf = load_rf_monthly_effective()
    mkt = load_market_returns()
    stock_ret, stock_size = load_stock_panel()
    be_map = load_book_equity_december_a()

    member_2x3, member_char_3x3, june_chars = build_formation_memberships(stock_size, be_map)
    factors = build_ff3_factors(member_2x3, stock_ret, stock_size, rf, mkt)
    membership = build_membership_jul_to_jun(member_char_3x3, june_chars)

    write_csv(
        cfg.OUTPUT_DIR / 'june_characteristics.csv',
        ['form_year', 'Stkcd', 'size_june', 'size_dec_prev', 'book_equity', 'be_me', 'size_tercile', 'bm_tercile', 'char_port', 'ff_leg_2x3'],
        june_chars,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv',
        ['Trdmnt', 'Stkcd', 'form_year', 'size_tercile', 'bm_tercile', 'char_port', 'size_june', 'be_me'],
        membership,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'ff3_factors_monthly.csv',
        ['Trdmnt', 'RF', 'RM', 'MKT_RF', 'SMB', 'HML', 'SL', 'SM', 'SH', 'BL', 'BM', 'BH', 'N_SL', 'N_SM', 'N_SH', 'N_BL', 'N_BM', 'N_BH'],
        factors,
    )

    print('Done:', cfg.OUTPUT_DIR / 'june_characteristics.csv')
    print('Done:', cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv')
    print('Done:', cfg.OUTPUT_DIR / 'ff3_factors_monthly.csv')


if __name__ == '__main__':
    main()
