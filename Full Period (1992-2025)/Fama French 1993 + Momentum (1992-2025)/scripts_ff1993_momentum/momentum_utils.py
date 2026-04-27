import csv
import math
from collections import defaultdict
import importlib.util
from pathlib import Path

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, "") else None


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
    lags = min(lag, t - 1)
    for l in range(1, lags + 1):
        w = 1.0 - l / (lags + 1)
        s += 2.0 * w * gamma(l)

    var_mu = s / t
    if var_mu <= 0:
        return mu, None
    se = math.sqrt(var_mu)
    return mu, (mu / se if se > 0 else None)


def cumulative_max_drawdown(returns):
    # Standard max drawdown on compounded wealth path.
    # Returns drawdown as negative decimal in [-1, 0].
    cumulative = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        if r is None:
            continue
        cumulative *= (1.0 + r)
        if cumulative > peak:
            peak = cumulative
        dd = (cumulative - peak) / peak
        if dd < max_dd:
            max_dd = dd
        if max_dd < -1.0:
            max_dd = -1.0
    return max_dd


def load_stock_panel():
    stock_ret = {}
    stock_size = {}
    by_stock_months = defaultdict(list)
    by_month_stocks = defaultdict(list)

    s_i = cfg.month_to_int(cfg.HISTORY_START)
    e_i = cfg.month_to_int(cfg.RETURN_END)

    with open(cfg.STOCK_FILE, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        for row in r:
            m = row.get("Trdmnt")
            stk = (row.get("Stkcd") or "").zfill(6)
            if not m or not stk:
                continue
            mi = cfg.month_to_int(m)
            if mi < s_i or mi > e_i:
                continue
            ret = to_float(row.get("Mretwd"))
            size = to_float(row.get("Msmvttl"))
            if ret is None or size is None or size <= 0:
                continue

            size = size * cfg.ME_SCALE_TO_CNY
            stock_ret[(m, stk)] = ret
            stock_size[(m, stk)] = size
            by_stock_months[stk].append(m)
            by_month_stocks[m].append(stk)

    for stk, months in by_stock_months.items():
        months.sort(key=cfg.month_to_int)
    return stock_ret, stock_size, by_stock_months, by_month_stocks


def compute_score_for_stock(stock_ret, stk, formation_month, j, skip):
    end_i = cfg.month_to_int(formation_month) - skip
    start_i = end_i - j + 1
    if start_i > end_i:
        return None

    gross = 1.0
    for mi in range(start_i, end_i + 1):
        m = cfg.int_to_month(mi)
        r = stock_ret.get((m, stk))
        if r is None:
            return None
        gross *= (1.0 + r)
    return gross - 1.0


def compute_momentum_scores(stock_ret, by_month_stocks, formation_month, j, skip=1):
    scores = {}
    stocks = by_month_stocks.get(formation_month, [])
    for stk in stocks:
        sc = compute_score_for_stock(stock_ret, stk, formation_month, j, skip)
        if sc is not None:
            scores[stk] = sc
    return scores


def pick_winners_losers(scores, deciles=10):
    ranked = sorted(scores.items(), key=lambda x: (x[1], x[0]))
    n = len(ranked)
    if n == 0:
        return [], []
    k = max(1, n // deciles)
    losers = [stk for stk, _ in ranked[:k]]
    winners = [stk for stk, _ in ranked[-k:]]
    return winners, losers


def value_weighted_return(stocks, month, stock_ret, stock_size):
    pm = cfg.prev_month(month)
    num = 0.0
    den = 0.0
    for stk in stocks:
        r = stock_ret.get((month, stk))
        if r is None:
            continue
        w = stock_size.get((pm, stk))
        if w is None or w <= 0:
            w = stock_size.get((month, stk))
        if w is None or w <= 0:
            continue
        num += w * r
        den += w
    if den <= 0:
        return None
    return num / den


def formation_weights(stocks, formation_month, stock_size):
    # fixed formation-month ME weights
    raw = {}
    den = 0.0
    for stk in stocks:
        me = stock_size.get((formation_month, stk))
        if me is None or me <= 0:
            continue
        raw[stk] = me
        den += me
    if den <= 0:
        return {}
    return {stk: me / den for stk, me in raw.items()}


def weighted_month_return_from_weights(weights, month, stock_ret):
    # use formation weights, renormalize on available returns in month t
    num = 0.0
    den = 0.0
    for stk, w in weights.items():
        r = stock_ret.get((month, stk))
        if r is None:
            continue
        num += w * r
        den += w
    if den <= 0:
        return None
    return num / den


def equal_weighted_return(stocks, month, stock_ret):
    vals = []
    for stk in stocks:
        r = stock_ret.get((month, stk))
        if r is not None:
            vals.append(r)
    return mean(vals)


def basket_return(stocks, month, stock_ret, stock_size, weighting):
    if weighting == "equal_weighted":
        return equal_weighted_return(stocks, month, stock_ret)
    return value_weighted_return(stocks, month, stock_ret, stock_size)


def compute_umd_for_strategy(months, stock_ret, stock_size, by_month_stocks, j, k, skip=1):
    # Cohort formed at month f uses formation-month ME weights.
    # Monthly series at t is average of K overlapping cohorts formed at t, t-1, ..., t-K+1.
    cohorts = {}
    winner_now = {}
    loser_now = {}
    umd = {}

    for m in months:
        scores = compute_momentum_scores(stock_ret, by_month_stocks, m, j, skip)
        winners, losers = pick_winners_losers(scores, deciles=cfg.MOM_DECILES)
        if cfg.MOM_WEIGHTING == "equal_weighted":
            cohorts[m] = (winners, losers)
        else:
            ww = formation_weights(winners, m, stock_size)
            lw = formation_weights(losers, m, stock_size)
            cohorts[m] = (ww, lw)

    for m in months:
        winner_legs = []
        loser_legs = []
        m_i = cfg.month_to_int(m)
        for lag in range(k):
            f_i = m_i - lag
            f_m = cfg.int_to_month(f_i)
            cohort = cohorts.get(f_m)
            if cohort is None:
                continue
            win_obj, lose_obj = cohort
            if cfg.MOM_WEIGHTING == "equal_weighted":
                wr = equal_weighted_return(win_obj, m, stock_ret)
                lr = equal_weighted_return(lose_obj, m, stock_ret)
            else:
                wr = weighted_month_return_from_weights(win_obj, m, stock_ret)
                lr = weighted_month_return_from_weights(lose_obj, m, stock_ret)
            if wr is not None:
                winner_legs.append(wr)
            if lr is not None:
                loser_legs.append(lr)

        wret = mean(winner_legs)
        lret = mean(loser_legs)
        winner_now[m] = wret
        loser_now[m] = lret
        umd[m] = (wret - lret) if (wret is not None and lret is not None) else None

    return umd, winner_now, loser_now


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
    n = len(y)
    k = len(x_cols) + 1
    if n <= k + 1:
        return None
    x = [[1.0] + [x_cols[j][i] for j in range(len(x_cols))] for i in range(n)]
    xtx = [[0.0 for _ in range(k)] for _ in range(k)]
    xty = [0.0 for _ in range(k)]
    for t in range(n):
        row = x[t]
        for i in range(k):
            xty[i] += row[i] * y[t]
            for j in range(k):
                xtx[i][j] += row[i] * row[j]
    xtx_inv = invert_matrix(xtx)
    if xtx_inv is None:
        return None

    beta = [sum(xtx_inv[i][j] * xty[j] for j in range(k)) for i in range(k)]
    resid = []
    for t in range(n):
        fit = sum(x[t][j] * beta[j] for j in range(k))
        resid.append(y[t] - fit)

    ybar = mean(y)
    tss = sum((v - ybar) ** 2 for v in y)
    rss = sum(e * e for e in resid)
    r2 = (1.0 - rss / tss) if tss > 0 else None

    lags = min(lag, n - 1)
    s = [[0.0 for _ in range(k)] for _ in range(k)]
    for t in range(n):
        e = resid[t]
        for i in range(k):
            for j in range(k):
                s[i][j] += e * e * x[t][i] * x[t][j]
    for l in range(1, lags + 1):
        w = 1.0 - l / (lags + 1)
        for t in range(l, n):
            et = resid[t]
            el = resid[t - l]
            for i in range(k):
                for j in range(k):
                    s[i][j] += w * et * el * (x[t][i] * x[t - l][j] + x[t - l][i] * x[t][j])

    vcv = [[0.0 for _ in range(k)] for _ in range(k)]
    for i in range(k):
        for j in range(k):
            vcv[i][j] = sum(
                xtx_inv[i][a] * sum(s[a][b] * xtx_inv[b][j] for b in range(k))
                for a in range(k)
            )
    se = [math.sqrt(vcv[i][i]) if vcv[i][i] > 0 else None for i in range(k)]
    tstats = [beta[i] / se[i] if se[i] not in (None, 0) else None for i in range(k)]
    return {"beta": beta, "t_nw": tstats, "r2": r2, "n": n}
