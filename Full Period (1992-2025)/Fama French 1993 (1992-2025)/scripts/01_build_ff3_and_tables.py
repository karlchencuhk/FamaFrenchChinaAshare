import csv
import math
from collections import defaultdict
import os
import config_master as cfg


# -----------------------------
# Basic helpers
# -----------------------------
def to_float(x):
    return float(x) if x not in (None, '') else None


def mean(xs):
    vals = [x for x in xs if x is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def stdev_sample(xs):
    vals = [x for x in xs if x is not None]
    n = len(vals)
    if n <= 1:
        return None
    mu = sum(vals) / n
    var = sum((x - mu) ** 2 for x in vals) / (n - 1)
    return math.sqrt(var)


def corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n <= 1:
        return None
    xvals = [p[0] for p in pairs]
    yvals = [p[1] for p in pairs]
    mx = sum(xvals) / n
    my = sum(yvals) / n
    sxx = sum((x - mx) ** 2 for x in xvals)
    syy = sum((y - my) ** 2 for y in yvals)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def autocorr1(xs):
    vals = [x for x in xs if x is not None]
    if len(vals) < 3:
        return None
    return corr(vals[1:], vals[:-1])


def nw_tstat_mean(series, lag=12):
    x = [v for v in series if v is not None]
    t = len(x)
    if t < 5:
        return None, None

    mu = sum(x) / t

    def gamma(l):
        s = 0.0
        for i in range(l, t):
            s += (x[i] - mu) * (x[i - l] - mu)
        return s / t

    s = gamma(0)
    L = min(lag, t - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (L + 1)
        s += 2.0 * w * gamma(l)

    var_mu = s / t
    if var_mu <= 0:
        return mu, None

    se = math.sqrt(var_mu)
    tstat = mu / se if se > 0 else None
    return mu, tstat


def significance_from_t(t):
    if t is None:
        return ''
    at = abs(t)
    if at >= 2.576:
        return '***'
    if at >= 1.960:
        return '**'
    if at >= 1.645:
        return '*'
    return ''


# -----------------------------
# Matrix helpers for OLS + NW
# -----------------------------
def transpose(a):
    return [list(row) for row in zip(*a)]


def matmul(a, b):
    out = [[0.0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for k in range(len(b)):
            aik = a[i][k]
            if aik == 0:
                continue
            for j in range(len(b[0])):
                out[i][j] += aik * b[k][j]
    return out


def matvec(a, x):
    return [sum(a[i][j] * x[j] for j in range(len(x))) for i in range(len(a))]


def invert_matrix(a):
    n = len(a)
    m = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(a)]

    for col in range(n):
        piv = col
        for r in range(col + 1, n):
            if abs(m[r][col]) > abs(m[piv][col]):
                piv = r
        if abs(m[piv][col]) < 1e-12:
            return None
        if piv != col:
            m[col], m[piv] = m[piv], m[col]

        div = m[col][col]
        for c in range(col, 2 * n):
            m[col][c] /= div

        for r in range(n):
            if r == col:
                continue
            fac = m[r][col]
            if fac == 0:
                continue
            for c in range(col, 2 * n):
                m[r][c] -= fac * m[col][c]

    return [row[n:] for row in m]


def ols_with_nw(y, x_cols, lag=12):
    # y: list[float], x_cols: list[list[float]] for regressors only (no intercept)
    n = len(y)
    k = len(x_cols) + 1
    if n <= k + 1:
        return None

    X = [[1.0] + [x_cols[j][i] for j in range(len(x_cols))] for i in range(n)]
    Xt = transpose(X)
    XtX = matmul(Xt, X)
    XtX_inv = invert_matrix(XtX)
    if XtX_inv is None:
        return None

    Xty = [sum(Xt[i][t] * y[t] for t in range(n)) for i in range(k)]
    beta = matvec(XtX_inv, Xty)

    fitted = [sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    resid = [y[i] - fitted[i] for i in range(n)]

    ybar = sum(y) / n
    tss = sum((yi - ybar) ** 2 for yi in y)
    rss = sum(e * e for e in resid)
    r2 = None
    if tss > 0:
        r2 = 1.0 - rss / tss

    # Newey-West covariance for coefficients
    L = min(lag, n - 1)
    S = [[0.0 for _ in range(k)] for _ in range(k)]

    # lag 0
    for t in range(n):
        et = resid[t]
        xt = X[t]
        for i in range(k):
            for j in range(k):
                S[i][j] += et * et * xt[i] * xt[j]

    # positive lags
    for l in range(1, L + 1):
        w = 1.0 - l / (L + 1)
        for t in range(l, n):
            et = resid[t]
            etl = resid[t - l]
            xt = X[t]
            xtl = X[t - l]
            for i in range(k):
                for j in range(k):
                    S[i][j] += w * et * etl * (xt[i] * xtl[j] + xtl[i] * xt[j])

    # scale by n (same convention as xtx using sum)
    V = matmul(matmul(XtX_inv, S), XtX_inv)
    se = []
    for i in range(k):
        vii = V[i][i]
        se.append(math.sqrt(vii) if vii > 0 else None)

    tstats = [beta[i] / se[i] if se[i] not in (None, 0) else None for i in range(k)]

    return {
        'beta': beta,
        'se_nw': se,
        't_nw': tstats,
        'r2': r2,
        'n': n,
    }


# -----------------------------
# Data loading
# -----------------------------
def load_rf_monthly_effective():
    rf = {}
    rf_date = {}
    with open(cfg.RF_FILE, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            d = row.get('Clsdt')
            val = row.get('Nrrmtdt')
            if not d or not val:
                continue
            m = d[:7]
            try:
                rf_m = float(val) / 100.0
            except ValueError:
                continue

            # Keep the latest available quote in each month.
            prev_d = rf_date.get(m)
            if prev_d is None or d > prev_d:
                rf_date[m] = d
                rf[m] = rf_m
    return rf


def load_market_returns():
    mkt = {}
    with open(cfg.MKT_RETURNS_PATH, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Markettype') != '5':
                continue
            m = row.get('Trdmnt')
            rv = row.get('Cmretwdtl')
            if m and rv:
                mkt[m] = float(rv)
    return mkt


def load_stock_panel():
    # monthly stock returns and market equity
    stock_ret = {}
    stock_size = {}
    stock_mkt_type = {}  # To store Markettype
    stocks_by_month = defaultdict(list)

    # Hardcoded for now, can be moved to config
    RETURN_START = '1992-07'
    RETURN_END = '2025-12'

    s_i = month_to_int('1990-12')
    e_i = month_to_int(RETURN_END)

    with open(cfg.MKT_PRICES_PATH, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            mt = row.get('Markettype')
            if mt not in ('1', '4'):
                continue
            m = row.get('Trdmnt')
            if not m:
                continue
            mi = month_to_int(m)
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
            stock_mkt_type[(m, stk)] = mt  # Store market type
            stocks_by_month[m].append(stk)

    return stock_ret, stock_size, stock_mkt_type, stocks_by_month


def load_book_equity_calendar_year():
    # fiscal year-end anytime in calendar year y -> BE_y
    # choose latest available fiscal-year-end date within that year
    be_map = defaultdict(dict)  # stk -> year -> be
    date_map = defaultdict(dict)  # stk -> year -> accper str

    with open(cfg.BS_PATH, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get('Typrep') != 'A':
                continue
            acc = row.get('Accper')
            if not acc or len(acc) < 10:
                continue

            stk = (row.get('Stkcd') or '').zfill(6)
            if not stk:
                continue

            y = int(acc[:4])
            v = row.get('A003100000') or row.get('A003000000')
            bv = to_float(v)
            if bv is None:
                continue

            old_date = date_map[stk].get(y)
            if old_date is None or acc > old_date:
                date_map[stk][y] = acc
                be_map[stk][y] = bv

    return be_map


# -----------------------------
# Date helpers
# -----------------------------
def month_to_int(m):
    y, mo = map(int, m.split('-'))
    return y * 12 + mo - 1

def prev_month(m):
    y, mo = map(int, m.split('-'))
    if mo == 1:
        return f'{y-1:04d}-12'
    return f'{y:04d}-{mo-1:02d}'

def formation_year_for_return_month(m):
    y, mo = map(int, m.split('-'))
    return y if mo >= 7 else y - 1

def all_months(start, end):
    si = month_to_int(start)
    ei = month_to_int(end)
    out = []
    for i in range(si, ei + 1):
        y = i // 12
        m = i % 12 + 1
        out.append(f'{y:04d}-{m:02d}')
    return out


# -----------------------------
# Breakpoint / sorting logic
# -----------------------------
def assign_bins_rank(values, cuts):
    # values: list[(key, value)], ascending rank bins
    # cuts: cumulative proportions, e.g. [0.5] -> 2 bins; [0.3,0.7] -> 3 bins
    pairs = sorted(values, key=lambda x: (x[1], x[0]))
    n = len(pairs)
    out = {}
    if n == 0:
        return out

    thresholds = []
    for c in cuts:
        idx = max(1, int(math.ceil(c * n)))
        thresholds.append(idx)

    for i, (k, _) in enumerate(pairs, start=1):
        b = 1
        for th in thresholds:
            if i > th:
                b += 1
        out[k] = b
    return out


def assign_quintile_from_breakpoints(value, breakpoints):
    if value <= breakpoints[0]:
        return 1
    elif value <= breakpoints[1]:
        return 2
    elif value <= breakpoints[2]:
        return 3
    elif value <= breakpoints[3]:
        return 4
    else:
        return 5

def build_formation_memberships_and_factors(stock_size, be_map, stock_mkt_type):
    # For each formation year t (June t), independent size and BM sorts
    # Size: ME June t (median split)
    # BM: BE(t-1) / ME Dec(t-1), 30/40/30 split
    # Also build independent 5x5 sorts for test portfolios

    member_2x3 = defaultdict(dict)  # year -> stk -> leg code (SL, SM, SH, BL, BM, BH)
    member_5x5 = defaultdict(dict)  # year -> stk -> (size_q, bm_q)
    june_chars = []
    annual_portfolio_stats = []

    for y in range(cfg.START_YEAR, cfg.END_YEAR + 1):
        june = f'{y:04d}-06'
        dec_prev = f'{y - 1:04d}-12'

        rec = {}
        
        # candidate stocks need June size and Dec-1 size and positive BE
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

            mkt_type = stock_mkt_type.get((june, stk))

            rec[stk] = {
                'form_year': y,
                'Stkcd': stk,
                'size_june': june_size,
                'size_dec_prev': dec_size,
                'book_equity': be,
                'be_me': bm,
                'mkt_type': mkt_type
            }

        if not rec:
            continue

        # NYSE-style breakpoints for size
        sse_firms = {stk: r for stk, r in rec.items() if r['mkt_type'] == '1'}
        
        if not sse_firms:
            continue

        sse_me_values = [r['size_june'] for r in sse_firms.values()]
        
        size_breakpoints = [
            sorted(sse_me_values)[int(p * len(sse_me_values))]
            for p in [0.2, 0.4, 0.6, 0.8]
        ]

        # Assign all firms to size quintiles based on SSE breakpoints
        for stk, r in rec.items():
            r['size5'] = assign_quintile_from_breakpoints(r['size_june'], size_breakpoints)

        # Traditional B/M sort within each size quintile
        bm_items = []
        for stk, r in rec.items():
            bm_items.append((stk, r['be_me']))
        
        bm_3 = assign_bins_rank(bm_items, cuts=[0.3, 0.7])
        bm_5 = assign_bins_rank(bm_items, cuts=[0.2, 0.4, 0.6, 0.8])

        # For 2x3 sort, we still need a simple median size split on all firms
        size_items_all = [(stk, r['size_june']) for stk, r in rec.items()]
        size_2 = assign_bins_rank(size_items_all, cuts=[0.5])

        # For portfolio characteristics table
        total_mkt_me_june = sum(r['size_june'] for r in rec.values())
        port_stats = defaultdict(lambda: {'sum_me': 0, 'n_firms': 0})

        for stk, row in rec.items():
            s2 = size_2.get(stk)
            b3 = bm_3.get(stk)
            s5 = row.get('size5')
            b5 = bm_5.get(stk)

            if s2 is not None and b3 is not None:
                size_lbl = 'S' if s2 == 1 else 'B'
                bm_lbl = {1: 'L', 2: 'M', 3: 'H'}[b3]
                member_2x3[y][stk] = size_lbl + bm_lbl

            if s5 is not None and b5 is not None:
                member_5x5[y][stk] = (s5, b5)
                port_stats[(s5, b5)]['sum_me'] += row['size_june']
                port_stats[(s5, b5)]['n_firms'] += 1

            june_chars.append({
                'form_year': y,
                'Stkcd': stk,
                'size_june': row['size_june'],
                'size_dec_prev': row['size_dec_prev'],
                'book_equity': row['book_equity'],
                'be_me': row['be_me'],
                'size2': s2,
                'bm3': b3,
                'leg_2x3': member_2x3[y].get(stk, ''),
                'size5': s5,
                'bm5': b5,
            })
        
        for (s5, b5), stats in port_stats.items():
            annual_portfolio_stats.append({
                'year': y,
                'size_quintile': s5,
                'bm_quintile': b5,
                'avg_me': stats['sum_me'] / stats['n_firms'] if stats['n_firms'] > 0 else 0,
                'sum_me': stats['sum_me'],
                'n_firms': stats['n_firms'],
                'total_mkt_me': total_mkt_me_june,
            })


    return member_2x3, member_5x5, june_chars, annual_portfolio_stats


# -----------------------------
# Returns / factors
# -----------------------------
def value_weighted_return(stocks, month, stock_ret, stock_size):
    pm = prev_month(month)
    num = 0.0
    den = 0.0
    n_used = 0
    for stk in stocks:
        r = stock_ret.get((month, stk))
        if r is None:
            continue
        w = stock_size.get((pm, stk))
        if w is None or w <= 0:
            # If previous month's size is not available, use current month's size
            w = stock_size.get((month, stk))
        if w is None or w <= 0:
            continue
        den += w
        num += w * r
        n_used += 1
    if den <= 0:
        return None, 0
    return num / den, n_used


def build_monthly_series(member_2x3, member_5x5, stock_ret, stock_size, rf, mkt):
    months = all_months('1992-07', '2025-12')

    legs = ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']
    leg_returns = {leg: {} for leg in legs}
    leg_counts = {leg: {} for leg in legs}

    port25_returns = {(i, j): {} for i in range(1, 6) for j in range(1, 6)}
    port25_counts = {(i, j): {} for i in range(1, 6) for j in range(1, 6)}

    factor_rows = []

    for m in months:
        fy = formation_year_for_return_month(m)
        members_2x3_for_year = member_2x3.get(fy, {})
        members_5x5_for_year = member_5x5.get(fy, {})

        by_leg = defaultdict(list)
        for stk, leg in members_2x3_for_year.items():
            by_leg[leg].append(stk)

        by_25 = defaultdict(list)
        for stk, (sq, bq) in members_5x5_for_year.items():
            by_25[(sq, bq)].append(stk)

        for leg in legs:
            rv, n_used = value_weighted_return(by_leg.get(leg, []), m, stock_ret, stock_size)
            leg_returns[leg][m] = rv
            leg_counts[leg][m] = n_used

        for i in range(1, 6):
            for j in range(1, 6):
                rv, n_used = value_weighted_return(by_25.get((i, j), []), m, stock_ret, stock_size)
                port25_returns[(i, j)][m] = rv
                port25_counts[(i, j)][m] = n_used

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
            'RF': rf_m,
            'RM': rm,
            'MKT_RF': mkt_rf,
            'SMB': smb,
            'HML': hml,
            'SL': sl,
            'SM': sm,
            'SH': sh,
            'BL': bl,
            'BM': bm,
            'BH': bh,
            'N_SL': leg_counts['SL'].get(m, 0),
            'N_SM': leg_counts['SM'].get(m, 0),
            'N_SH': leg_counts['SH'].get(m, 0),
            'N_BL': leg_counts['BL'].get(m, 0),
            'N_BM': leg_counts['BM'].get(m, 0),
            'N_BH': leg_counts['BH'].get(m, 0),
        })

    return factor_rows, port25_returns, port25_counts


# -----------------------------
# Table builders (CSV rows)
# -----------------------------
def build_portfolio_characteristics(annual_stats):
    ports = defaultdict(lambda: defaultdict(list))
    for s in annual_stats:
        k = (s['size_quintile'], s['bm_quintile'])
        ports[k]['avg_me'].append(s['avg_me'])
        ports[k]['n_firms'].append(s['n_firms'])
        if s['total_mkt_me'] > 0:
            pct_me = s['sum_me'] / s['total_mkt_me']
            ports[k]['pct_me'].append(pct_me)

    out = []
    all_keys = sorted(ports.keys())

    for size_q, bm_q in all_keys:
        k = (size_q, bm_q)
        if not ports[k]:
            continue
        
        avg_me = mean(ports[k]['avg_me'])
        avg_n = mean(ports[k]['n_firms'])
        avg_pct = mean(ports[k]['pct_me'])

        out.append({
            'size_quintile': size_q,
            'bm_quintile': bm_q,
            'avg_me_rmb_mm': avg_me,
            'avg_n_firms': avg_n,
            'avg_me_pct_of_total': avg_pct * 100.0 if avg_pct is not None else None
        })
    return out


def make_table_1_factor_summary(factor_rows):
    facs = ['MKT_RF', 'SMB', 'HML']
    out = []
    for f in facs:
        s = [r[f] for r in factor_rows if r[f] is not None]
        mu, t = nw_tstat_mean(s, lag=12)
        sd = stdev_sample(s)
        sharpe = (mu / sd) if (mu is not None and sd not in (None, 0)) else None
        ac1 = autocorr1(s)
        out.append({
            'factor': f,
            'n_months': len(s),
            'mean_monthly_pct': None if mu is None else mu * 100.0,
            'std_monthly_pct': None if sd is None else sd * 100.0,
            'nw12_tstat_mean': t,
            'sharpe_monthly': sharpe,
            'autocorr1': ac1,
            'annualized_mean_pct': None if mu is None else mu * 12.0 * 100.0,
            'annualized_vol_pct': None if sd is None else sd * math.sqrt(12.0) * 100.0,
        })
    return out


def make_table_2_factor_corr(factor_rows):
    facs = ['MKT_RF', 'SMB', 'HML']
    series = {f: [r[f] for r in factor_rows] for f in facs}
    out = []
    for a in facs:
        row = {'row_factor': a}
        for b in facs:
            row[b] = corr(series[a], series[b])
        out.append(row)
    return out


def make_table_3_six_portfolio_summary(factor_rows):
    legs = ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']
    out = []
    for leg in legs:
        s = [r[leg] for r in factor_rows if r[leg] is not None]
        mu = mean(s)
        sd = stdev_sample(s)
        _, t = nw_tstat_mean(s, lag=12)
        n_avg = mean([r.get(f'N_{leg}') for r in factor_rows if r.get(f'N_{leg}') is not None])
        out.append({
            'portfolio': leg,
            'n_months': len(s),
            'avg_monthly_return_pct': None if mu is None else mu * 100.0,
            'std_monthly_pct': None if sd is None else sd * 100.0,
            'nw12_tstat_mean': t,
            'avg_n_stocks': n_avg,
        })
    return out


def make_table_4_port25_avg_excess(port25_returns, rf):
    out = []
    months = all_months('1992-07', '2025-12')
    for i in range(1, 6):
        for j in range(1, 6):
            s = []
            for m in months:
                r = port25_returns[(i, j)].get(m)
                rf_m = rf.get(m)
                if r is None or rf_m is None:
                    continue
                s.append(r - rf_m)
            mu = mean(s)
            out.append({
                'size_quintile': i,
                'bm_quintile': j,
                'avg_excess_return_pct': None if mu is None else mu * 100.0,
                'n_months': len(s),
            })
    return out


def make_table_5_regressions(port25_returns, rf, factor_rows):
    fac_map = {r['Trdmnt']: r for r in factor_rows}
    months = all_months('1992-07', '2025-12')

    out = []
    for i in range(1, 6):
        for j in range(1, 6):
            y = []
            x1 = []
            x2 = []
            x3 = []
            for m in months:
                r = port25_returns[(i, j)].get(m)
                rf_m = rf.get(m)
                fr = fac_map.get(m)
                if fr is None:
                    continue
                if r is None or rf_m is None:
                    continue
                if fr['MKT_RF'] is None or fr['SMB'] is None or fr['HML'] is None:
                    continue
                y.append(r - rf_m)
                x1.append(fr['MKT_RF'])
                x2.append(fr['SMB'])
                x3.append(fr['HML'])

            res = ols_with_nw(y, [x1, x2, x3], lag=12)
            if res is None:
                continue

            b0, b1, b2, b3 = res['beta']
            t0, t1, t2, t3 = res['t_nw']
            out.append({
                'portfolio': f'S{i}B{j}',
                'size_quintile': i,
                'bm_quintile': j,
                'alpha_pct': b0 * 100.0,
                'beta_mkt': b1,
                'beta_smb': b2,
                'beta_hml': b3,
                'nw12_t_alpha': t0,
                'nw12_t_mkt': t1,
                'nw12_t_smb': t2,
                'nw12_t_hml': t3,
                'r2': res['r2'],
                'n_months': res['n'],
            })
    return out


# -----------------------------
# Output writers
# -----------------------------
def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main():
    print('Loading sources...')
    rf = load_rf_monthly_effective()
    mkt = load_market_returns()
    stock_ret, stock_size, stock_mkt_type, _ = load_stock_panel()
    be_map = load_book_equity_calendar_year()

    print('Building formation memberships...')
    member_2x3, member_5x5, june_chars, annual_stats = build_formation_memberships_and_factors(stock_size, be_map, stock_mkt_type)

    print('Building monthly series...')
    series, port25, port25_counts = build_monthly_series(member_2x3, member_5x5, stock_ret, stock_size, rf, mkt)

    print('Writing portfolio characteristics...')
    char_table = build_portfolio_characteristics(annual_stats)
    if char_table:
        fnames = list(char_table[0].keys())
        write_csv(cfg.PORTFOLIO_CHARS_PATH, fnames, char_table)

    print('Writing factors...')
    if series:
        write_csv(cfg.FACTORS_PATH, series[0].keys(), series)

    print('Writing monthly 25-portfolio panel...')
    months = all_months('1992-07', '2025-12')
    port25_rows = []
    for m in months:
        rf_m = rf.get(m)
        for i in range(1, 6):
            for j in range(1, 6):
                rv = port25[(i, j)].get(m)
                n = port25_counts[(i, j)].get(m)
                ex = (rv - rf_m) if (rv is not None and rf_m is not None) else None
                port25_rows.append({
                    'Trdmnt': m,
                    'size_quintile': i,
                    'bm_quintile': j,
                    'portfolio': f'S{i}B{j}',
                    'vw_return': rv,
                    'excess_return': ex,
                    'n_stocks': n,
                })
    write_csv(
        os.path.join(cfg.OUTPUT_DIR, 'ff3_port25_monthly.csv'),
        ['Trdmnt', 'size_quintile', 'bm_quintile', 'portfolio', 'vw_return', 'excess_return', 'n_stocks'],
        port25_rows,
    )

    print('Writing tables...')
    # Table 1: Summary stats
    table1 = make_table_1_factor_summary(series)
    if table1:
        write_csv(os.path.join(cfg.OUTPUT_DIR, 'ff1993_table1_summary.csv'), table1[0].keys(), table1)

    # Table 2: Correlations
    table2 = make_table_2_factor_corr(series)
    if table2:
        write_csv(os.path.join(cfg.OUTPUT_DIR, 'ff1993_table2_correlations.csv'), table2[0].keys(), table2)

    # Table 3: Portfolio returns
    table3 = make_table_3_six_portfolio_summary(series)
    if table3:
        write_csv(os.path.join(cfg.OUTPUT_DIR, 'ff1993_table3_portfolios.csv'), table3[0].keys(), table3)

    # Table 4: 25 portfolio returns
    table4 = make_table_4_port25_avg_excess(port25, rf)
    if table4:
        write_csv(os.path.join(cfg.OUTPUT_DIR, 'ff1993_table4_25portfolios.csv'), table4[0].keys(), table4)
    
    # Table 5: Regressions
    table5 = make_table_5_regressions(port25, rf, series)
    if table5:
        write_csv(os.path.join(cfg.OUTPUT_DIR, 'ff1993_table5_regressions.csv'), table5[0].keys(), table5)

    print('Done.')


if __name__ == "__main__":
    main()
