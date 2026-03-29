import csv
import math
from collections import defaultdict
from pathlib import Path
import importlib.util


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, '') else None


def solve_linear_system(a, b):
    # Gaussian elimination for small systems
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]

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
        for c in range(col, n + 1):
            m[col][c] /= div

        for r in range(n):
            if r == col:
                continue
            fac = m[r][col]
            if fac == 0:
                continue
            for c in range(col, n + 1):
                m[r][c] -= fac * m[col][c]

    return [m[i][n] for i in range(n)]


def cs_ols(y, xcols):
    # y: list float, xcols: list of lists of float (k regressors)
    n = len(y)
    k = len(xcols)
    if n <= k + 1:
        return None

    # design includes intercept
    p = k + 1
    xtx = [[0.0 for _ in range(p)] for _ in range(p)]
    xty = [0.0 for _ in range(p)]

    for i in range(n):
        row = [1.0] + [xcols[j][i] for j in range(k)]
        yi = y[i]
        for a in range(p):
            xty[a] += row[a] * yi
            for b in range(p):
                xtx[a][b] += row[a] * row[b]

    beta = solve_linear_system(xtx, xty)
    if beta is None:
        return None
    return beta


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

    g0 = gamma(0)
    s = g0
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


def load_data():
    master = {}
    with open(cfg.OUTPUT_DIR / 'master_panel_200001_202512.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row['Trdmnt'], row['Stkcd'])
            master[key] = to_float(row['stock_excess_ret'])

    by_month = defaultdict(list)
    with open(cfg.OUTPUT_DIR / 'membership_jul_to_jun.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            m = row['Trdmnt']
            if cfg.month_to_int(m) < cfg.month_to_int(cfg.RETURN_START):
                continue
            if cfg.month_to_int(m) > cfg.month_to_int(cfg.RETURN_END):
                continue

            stk = row['Stkcd']
            y = master.get((m, stk))
            if y is None:
                continue

            by_month[m].append({
                'y': y,
                'beta': to_float(row['beta']),
                'ln_size': to_float(row['ln_size']),
                'ln_be_me': to_float(row['ln_be_me']),
            })
    return by_month


def main():
    by_month = load_data()
    months = sorted(by_month.keys(), key=cfg.month_to_int)

    models = [
        ('M1_beta', ['beta']),
        ('M2_ln_size', ['ln_size']),
        ('M3_ln_be_me', ['ln_be_me']),
        ('M4_beta_ln_size', ['beta', 'ln_size']),
        ('M5_beta_ln_be_me', ['beta', 'ln_be_me']),
        ('M6_ln_size_ln_be_me', ['ln_size', 'ln_be_me']),
        ('M7_all3', ['beta', 'ln_size', 'ln_be_me']),
    ]

    monthly_slopes = []
    coef_ts = defaultdict(lambda: defaultdict(list))  # model -> coef_name -> series

    for m in months:
        data = by_month[m]
        for model_name, vars_ in models:
            y = []
            xcols = [[] for _ in vars_]
            for row in data:
                vals = [row[v] for v in vars_]
                if any(v is None for v in vals):
                    continue
                y.append(row['y'])
                for i, v in enumerate(vals):
                    xcols[i].append(v)

            b = cs_ols(y, xcols)
            if b is None:
                continue

            # b[0] intercept
            monthly_slopes.append([m, model_name, 'intercept', b[0], len(y)])
            coef_ts[model_name]['intercept'].append(b[0])
            for i, v in enumerate(vars_, start=1):
                monthly_slopes.append([m, model_name, v, b[i], len(y)])
                coef_ts[model_name][v].append(b[i])

    out_monthly = cfg.OUTPUT_DIR / 'fm_monthly_slopes.csv'
    with open(out_monthly, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Trdmnt', 'model', 'coefficient', 'lambda', 'n_stocks'])
        for row in monthly_slopes:
            w.writerow([row[0], row[1], row[2], f'{row[3]:.10f}', row[4]])

    out_table = cfg.OUTPUT_DIR / 'table_iii_fama_macbeth.csv'
    with open(out_table, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['model', 'coefficient', 'avg_lambda', 'nw12_tstat'])
        for model_name, _ in models:
            for coef_name in ['intercept', 'beta', 'ln_size', 'ln_be_me']:
                s = coef_ts[model_name].get(coef_name, [])
                if not s:
                    continue
                mu, tstat = nw_tstat_mean(s, lag=cfg.NW_LAG)
                w.writerow([
                    model_name,
                    coef_name,
                    '' if mu is None else f'{mu:.10f}',
                    '' if tstat is None else f'{tstat:.4f}',
                ])

    print('Done:', out_monthly)
    print('Done:', out_table)


if __name__ == '__main__':
    main()
