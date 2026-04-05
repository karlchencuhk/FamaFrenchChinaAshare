import csv
import math
from collections import defaultdict
from pathlib import Path
import importlib.util


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


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
    with open(cfg.MKT_FILE, newline='', encoding='utf-8-sig') as f:
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
    stock_mkt_type = {}
    stocks_by_month = defaultdict(list)

    s_i = cfg.month_to_int('1990-12')
    e_i = cfg.month_to_int(cfg.RETURN_END)

    with open(cfg.STOCK_FILE, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
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
            stock_mkt_type[(m, stk)] = mt
            stocks_by_month[m].append(stk)

    return stock_ret, stock_size, stock_mkt_type, stocks_by_month


def load_book_equity_calendar_year():
    # fiscal year-end anytime in calendar year y -> BE_y
    # choose latest available fiscal-year-end date within that year
    be_map = defaultdict(dict)  # stk -> year -> be
    date_map = defaultdict(dict)  # stk -> year -> accper str

    with open(cfg.BS_FILE, newline='', encoding='utf-8-sig') as f:
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


def build_formation_membership(stock_size, be_map, stock_mkt_type):
    # For each formation year t (June t), independent size and BM sorts
    # Size: ME June t (median split)
    # BM: BE(t-1) / ME Dec(t-1), 30/40/30 split
    # Also build independent 5x5 sorts for test portfolios

    member_2x3 = defaultdict(dict)  # year -> stk -> leg code (SL, SM, SH, BL, BM, BH)
    member_5x5 = defaultdict(dict)  # year -> stk -> (size_q, bm_q)
    june_chars = []

    for y in range(1992, 2026):
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
                'mkt_type': mkt_type,
            }

        if not rec:
            continue

        sse_firms = {stk: r for stk, r in rec.items() if r['mkt_type'] == '1'}
        if not sse_firms:
            continue

        sse_me_values = sorted([r['size_june'] for r in sse_firms.values()])
        n_sse = len(sse_me_values)
        size_breakpoints = [
            sse_me_values[min(n_sse - 1, int(p * n_sse))]
            for p in [0.2, 0.4, 0.6, 0.8]
        ]

        for stk, r in rec.items():
            r['size5'] = assign_quintile_from_breakpoints(r['size_june'], size_breakpoints)

        bm_items = [(stk, r['be_me']) for stk, r in rec.items()]
        size_items_all = [(stk, r['size_june']) for stk, r in rec.items()]

        size_2 = assign_bins_rank(size_items_all, cuts=[0.5])
        bm_3 = assign_bins_rank(bm_items, cuts=[0.3, 0.7])
        bm_5 = assign_bins_rank(bm_items, cuts=[0.2, 0.4, 0.6, 0.8])

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

    return member_2x3, member_5x5, june_chars


# -----------------------------
# Returns / factors
# -----------------------------
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


def build_monthly_series(member_2x3, member_5x5, stock_ret, stock_size, rf, mkt):
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)

    legs = ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']
    leg_returns = {leg: {} for leg in legs}
    leg_counts = {leg: {} for leg in legs}

    port25_returns = {(i, j): {} for i in range(1, 6) for j in range(1, 6)}
    port25_counts = {(i, j): {} for i in range(1, 6) for j in range(1, 6)}

    factor_rows = []

    for m in months:
        fy = cfg.formation_year_for_return_month(m)
        members_2x3 = member_2x3.get(fy, {})
        members_5x5 = member_5x5.get(fy, {})

        by_leg = defaultdict(list)
        for stk, leg in members_2x3.items():
            by_leg[leg].append(stk)

        by_25 = defaultdict(list)
        for stk, (sq, bq) in members_5x5.items():
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

    return factor_rows, leg_returns, leg_counts, port25_returns, port25_counts


# -----------------------------
# Table builders (CSV rows)
# -----------------------------
def make_table_1_factor_summary(factor_rows):
    facs = ['MKT_RF', 'SMB', 'HML']
    out = []
    for f in facs:
        s = [r[f] for r in factor_rows if r[f] is not None]
        mu, t = nw_tstat_mean(s, lag=cfg.NW_LAG)
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
        _, t = nw_tstat_mean(s, lag=cfg.NW_LAG)
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
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
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
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)

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

            res = ols_with_nw(y, [x1, x2, x3], lag=cfg.NW_LAG)
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


def make_table_6_alpha_diagnostics(reg_rows):
    alphas = [r['alpha_pct'] for r in reg_rows if r.get('alpha_pct') is not None]
    tvals = [r['nw12_t_alpha'] for r in reg_rows if r.get('nw12_t_alpha') is not None]

    if not alphas:
        return []

    out = []
    out.append({'metric': 'n_portfolios', 'value': len(alphas)})
    out.append({'metric': 'mean_alpha_pct', 'value': sum(alphas) / len(alphas)})
    out.append({'metric': 'mean_abs_alpha_pct', 'value': sum(abs(a) for a in alphas) / len(alphas)})
    out.append({'metric': 'max_abs_alpha_pct', 'value': max(abs(a) for a in alphas)})

    if tvals:
        out.append({'metric': 'n_sig_10pct', 'value': sum(1 for t in tvals if abs(t) >= 1.645)})
        out.append({'metric': 'n_sig_5pct', 'value': sum(1 for t in tvals if abs(t) >= 1.960)})
        out.append({'metric': 'n_sig_1pct', 'value': sum(1 for t in tvals if abs(t) >= 2.576)})

    return out


def make_table_7_pricing_errors(reg_rows, port25_returns, rf, factor_rows):
    fac_means = {
        'MKT_RF': mean([r['MKT_RF'] for r in factor_rows if r['MKT_RF'] is not None]),
        'SMB': mean([r['SMB'] for r in factor_rows if r['SMB'] is not None]),
        'HML': mean([r['HML'] for r in factor_rows if r['HML'] is not None]),
    }

    reg_map = {(r['size_quintile'], r['bm_quintile']): r for r in reg_rows}
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)

    out = []
    errs = []
    for i in range(1, 6):
        for j in range(1, 6):
            s = []
            for m in months:
                rv = port25_returns[(i, j)].get(m)
                rf_m = rf.get(m)
                if rv is None or rf_m is None:
                    continue
                s.append(rv - rf_m)
            actual = mean(s)
            reg = reg_map.get((i, j))
            if reg is None:
                continue

            fitted = (
                reg['beta_mkt'] * fac_means['MKT_RF']
                + reg['beta_smb'] * fac_means['SMB']
                + reg['beta_hml'] * fac_means['HML']
            )
            pe = None if (actual is None or fitted is None) else (actual - fitted)
            if pe is not None:
                errs.append(pe)

            out.append({
                'portfolio': f'S{i}B{j}',
                'size_quintile': i,
                'bm_quintile': j,
                'actual_avg_excess_pct': None if actual is None else actual * 100.0,
                'fitted_avg_excess_pct': None if fitted is None else fitted * 100.0,
                'pricing_error_pct': None if pe is None else pe * 100.0,
            })

    rmse = None
    mae = None
    if errs:
        rmse = math.sqrt(sum(e * e for e in errs) / len(errs))
        mae = sum(abs(e) for e in errs) / len(errs)

    out.append({
        'portfolio': 'SUMMARY',
        'size_quintile': '',
        'bm_quintile': '',
        'actual_avg_excess_pct': '',
        'fitted_avg_excess_pct': '',
        'pricing_error_pct': '',
        'rmse_pct': '' if rmse is None else rmse * 100.0,
        'mae_pct': '' if mae is None else mae * 100.0,
    })

    return out


def make_table_8_factor_premia_significance(factor_rows):
    facs = ['MKT_RF', 'SMB', 'HML']
    out = []
    for f in facs:
        s = [r[f] for r in factor_rows if r[f] is not None]
        mu, t = nw_tstat_mean(s, lag=cfg.NW_LAG)
        out.append({
            'factor': f,
            'mean_monthly_pct': None if mu is None else mu * 100.0,
            'nw12_tstat': t,
            'signif': significance_from_t(t),
            'n_months': len(s),
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
    member_2x3, member_5x5, june_chars = build_formation_membership(stock_size, be_map, stock_mkt_type)

    print('Building monthly factor and portfolio series...')
    factor_rows, leg_returns, leg_counts, port25_returns, port25_counts = build_monthly_series(
        member_2x3, member_5x5, stock_ret, stock_size, rf, mkt
    )

    print('Building 8 output tables...')
    t1 = make_table_1_factor_summary(factor_rows)
    t2 = make_table_2_factor_corr(factor_rows)
    t3 = make_table_3_six_portfolio_summary(factor_rows)
    t4 = make_table_4_port25_avg_excess(port25_returns, rf)
    t5 = make_table_5_regressions(port25_returns, rf, factor_rows)
    t6 = make_table_6_alpha_diagnostics(t5)
    t7 = make_table_7_pricing_errors(t5, port25_returns, rf, factor_rows)
    t8 = make_table_8_factor_premia_significance(factor_rows)

    print('Writing CSV outputs...')
    # audit files
    write_csv(
        cfg.OUTPUT_DIR / 'ff3_june_characteristics.csv',
        ['form_year', 'Stkcd', 'size_june', 'size_dec_prev', 'book_equity', 'be_me', 'size2', 'bm3', 'leg_2x3', 'size5', 'bm5'],
        june_chars,
    )

    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    leg_rows = []
    for m in months:
        row = {'Trdmnt': m}
        for leg in ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']:
            row[leg] = leg_returns[leg].get(m)
            row[f'N_{leg}'] = leg_counts[leg].get(m)
        leg_rows.append(row)
    write_csv(
        cfg.OUTPUT_DIR / 'ff3_leg_returns.csv',
        ['Trdmnt', 'SL', 'SM', 'SH', 'BL', 'BM', 'BH', 'N_SL', 'N_SM', 'N_SH', 'N_BL', 'N_BM', 'N_BH'],
        leg_rows,
    )

    write_csv(
        cfg.OUTPUT_DIR / 'ff3_factors_monthly.csv',
        ['Trdmnt', 'RF', 'RM', 'MKT_RF', 'SMB', 'HML', 'SL', 'SM', 'SH', 'BL', 'BM', 'BH', 'N_SL', 'N_SM', 'N_SH', 'N_BL', 'N_BM', 'N_BH'],
        factor_rows,
    )

    port25_rows = []
    for m in months:
        rf_m = rf.get(m)
        for i in range(1, 6):
            for j in range(1, 6):
                rv = port25_returns[(i, j)].get(m)
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
        cfg.OUTPUT_DIR / 'ff3_port25_monthly.csv',
        ['Trdmnt', 'size_quintile', 'bm_quintile', 'portfolio', 'vw_return', 'excess_return', 'n_stocks'],
        port25_rows,
    )

    # 8 core tables
    write_csv(
        cfg.OUTPUT_DIR / 'table_1_factor_summary.csv',
        ['factor', 'n_months', 'mean_monthly_pct', 'std_monthly_pct', 'nw12_tstat_mean', 'sharpe_monthly', 'autocorr1', 'annualized_mean_pct', 'annualized_vol_pct'],
        t1,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_2_factor_correlation.csv',
        ['row_factor', 'MKT_RF', 'SMB', 'HML'],
        t2,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_3_six_portfolio_summary.csv',
        ['portfolio', 'n_months', 'avg_monthly_return_pct', 'std_monthly_pct', 'nw12_tstat_mean', 'avg_n_stocks'],
        t3,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_4_25port_avg_excess_returns.csv',
        ['size_quintile', 'bm_quintile', 'avg_excess_return_pct', 'n_months'],
        t4,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_5_25port_ff3_regressions.csv',
        ['portfolio', 'size_quintile', 'bm_quintile', 'alpha_pct', 'beta_mkt', 'beta_smb', 'beta_hml', 'nw12_t_alpha', 'nw12_t_mkt', 'nw12_t_smb', 'nw12_t_hml', 'r2', 'n_months'],
        t5,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_6_alpha_diagnostics.csv',
        ['metric', 'value'],
        t6,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_7_pricing_errors.csv',
        ['portfolio', 'size_quintile', 'bm_quintile', 'actual_avg_excess_pct', 'fitted_avg_excess_pct', 'pricing_error_pct', 'rmse_pct', 'mae_pct'],
        t7,
    )
    write_csv(
        cfg.OUTPUT_DIR / 'table_8_factor_premia_significance.csv',
        ['factor', 'mean_monthly_pct', 'nw12_tstat', 'signif', 'n_months'],
        t8,
    )

    print('Done. Outputs written to:', cfg.OUTPUT_DIR)


if __name__ == '__main__':
    main()
