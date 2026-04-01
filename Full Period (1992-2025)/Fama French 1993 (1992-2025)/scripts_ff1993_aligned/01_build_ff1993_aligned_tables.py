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


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


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

    L = min(lag, n - 1)
    S = [[0.0 for _ in range(k)] for _ in range(k)]

    for t in range(n):
        et = resid[t]
        xt = X[t]
        for i in range(k):
            for j in range(k):
                S[i][j] += et * et * xt[i] * xt[j]

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

    V = matmul(matmul(XtX_inv, S), XtX_inv)
    se = []
    for i in range(k):
        vii = V[i][i]
        se.append(math.sqrt(vii) if vii > 0 else None)

    tstats = [beta[i] / se[i] if se[i] not in (None, 0) else None for i in range(k)]
    return {'beta': beta, 't_nw': tstats, 'r2': r2, 'n': n}


def build_table1_size_bm_grid():
    rows = read_csv(cfg.SRC_OUTPUT / 'ff3_port25_monthly.csv')
    acc = defaultdict(lambda: {'ret': [], 'n': []})

    for r in rows:
        s = int(r['size_quintile'])
        b = int(r['bm_quintile'])
        ex = to_float(r.get('excess_return'))
        n = to_float(r.get('n_stocks'))
        if ex is not None:
            acc[(s, b)]['ret'].append(ex)
        if n is not None:
            acc[(s, b)]['n'].append(n)

    out = []
    for s in range(1, 6):
        for b in range(1, 6):
            d = acc[(s, b)]
            mu = (sum(d['ret']) / len(d['ret'])) if d['ret'] else None
            n_avg = (sum(d['n']) / len(d['n'])) if d['n'] else None
            out.append({
                'size_quintile': s,
                'bm_quintile': b,
                'avg_excess_return_pct': '' if mu is None else mu * 100.0,
                'avg_n_stocks': '' if n_avg is None else n_avg,
            })

    write_csv(
        cfg.OUT_DIR / 'table_1_ff1993_size_bm_5x5.csv',
        ['size_quintile', 'bm_quintile', 'avg_excess_return_pct', 'avg_n_stocks'],
        out,
    )


def build_table2_factor_summary():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_1_factor_summary.csv')
    out = []
    for r in rows:
        out.append({
            'factor': r['factor'],
            'mean_monthly_pct': r['mean_monthly_pct'],
            'std_monthly_pct': r['std_monthly_pct'],
            'nw12_tstat_mean': r['nw12_tstat_mean'],
            'annualized_mean_pct': r['annualized_mean_pct'],
            'annualized_vol_pct': r['annualized_vol_pct'],
            'n_months': r['n_months'],
        })
    write_csv(
        cfg.OUT_DIR / 'table_2_ff1993_factor_summary.csv',
        ['factor', 'mean_monthly_pct', 'std_monthly_pct', 'nw12_tstat_mean', 'annualized_mean_pct', 'annualized_vol_pct', 'n_months'],
        out,
    )


def build_table6_stock_regressions():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_5_25port_ff3_regressions.csv')
    write_csv(
        cfg.OUT_DIR / 'table_6a_ff1993_stock_regressions.csv',
        ['portfolio', 'size_quintile', 'bm_quintile', 'alpha_pct', 'nw12_t_alpha', 'beta_mkt', 'nw12_t_mkt', 'beta_smb', 'nw12_t_smb', 'beta_hml', 'nw12_t_hml', 'r2', 'n_months'],
        rows,
    )


def build_table9_alpha_analogue():
    rows = read_csv(cfg.SRC_OUTPUT / 'table_5_25port_ff3_regressions.csv')
    summary = read_csv(cfg.SRC_OUTPUT / 'table_6_alpha_diagnostics.csv')
    pe = read_csv(cfg.SRC_OUTPUT / 'table_7_pricing_errors.csv')

    out_a = []
    for r in rows:
        out_a.append({
            'portfolio': r['portfolio'],
            'alpha_pct': r['alpha_pct'],
            'nw12_t_alpha': r['nw12_t_alpha'],
            'abs_alpha_pct': '' if r['alpha_pct'] in (None, '') else abs(float(r['alpha_pct'])),
        })

    write_csv(
        cfg.OUT_DIR / 'table_9a_ff1993_alpha_by_portfolio.csv',
        ['portfolio', 'alpha_pct', 'nw12_t_alpha', 'abs_alpha_pct'],
        out_a,
    )

    summ_map = {r['metric']: r['value'] for r in summary}
    rmse = ''
    mae = ''
    for r in pe:
        if r.get('portfolio') == 'SUMMARY':
            rmse = r.get('rmse_pct', '')
            mae = r.get('mae_pct', '')
            break

    out_c = [
        {'metric': 'n_portfolios', 'value': summ_map.get('n_portfolios', '')},
        {'metric': 'n_sig_10pct', 'value': summ_map.get('n_sig_10pct', '')},
        {'metric': 'n_sig_5pct', 'value': summ_map.get('n_sig_5pct', '')},
        {'metric': 'n_sig_1pct', 'value': summ_map.get('n_sig_1pct', '')},
        {'metric': 'mean_alpha_pct', 'value': summ_map.get('mean_alpha_pct', '')},
        {'metric': 'mean_abs_alpha_pct', 'value': summ_map.get('mean_abs_alpha_pct', '')},
        {'metric': 'max_abs_alpha_pct', 'value': summ_map.get('max_abs_alpha_pct', '')},
        {'metric': 'rmse_pct', 'value': rmse},
        {'metric': 'mae_pct', 'value': mae},
        {'metric': 'joint_test_note', 'value': 'GRS not implemented; diagnostics shown as FF1993 Table 9 analogue.'},
    ]

    write_csv(
        cfg.OUT_DIR / 'table_9c_ff1993_alpha_diagnostics.csv',
        ['metric', 'value'],
        out_c,
    )


def build_table9_capm_only():
    port_rows = read_csv(cfg.SRC_OUTPUT / 'ff3_port25_monthly.csv')
    fac_rows = read_csv(cfg.SRC_OUTPUT / 'ff3_factors_monthly.csv')

    mkt = {r['Trdmnt']: to_float(r.get('MKT_RF')) for r in fac_rows}

    by_port = defaultdict(list)
    for r in port_rows:
        p = r['portfolio']
        mo = r['Trdmnt']
        ex = to_float(r.get('excess_return'))
        mx = mkt.get(mo)
        if ex is None or mx is None:
            continue
        by_port[p].append((ex, mx))

    out = []
    for i in range(1, 6):
        for j in range(1, 6):
            p = f'S{i}B{j}'
            pairs = by_port.get(p, [])
            y = [a for a, _ in pairs]
            x = [b for _, b in pairs]
            res = ols_with_nw(y, [x], lag=12)
            if res is None:
                continue
            out.append({
                'portfolio': p,
                'size_quintile': i,
                'bm_quintile': j,
                'alpha_pct': res['beta'][0] * 100.0,
                'nw12_t_alpha': res['t_nw'][0],
                'beta_mkt': res['beta'][1],
                'nw12_t_mkt': res['t_nw'][1],
                'r2': res['r2'],
                'n_months': res['n'],
            })

    write_csv(
        cfg.OUT_DIR / 'table_9a_ff1993_capm_only_by_portfolio.csv',
        ['portfolio', 'size_quintile', 'bm_quintile', 'alpha_pct', 'nw12_t_alpha', 'beta_mkt', 'nw12_t_mkt', 'r2', 'n_months'],
        out,
    )

    tvals = [to_float(r['nw12_t_alpha']) for r in out if r.get('nw12_t_alpha') not in (None, '')]
    alphas = [to_float(r['alpha_pct']) for r in out if r.get('alpha_pct') not in (None, '')]
    out_c = [
        {'metric': 'model', 'value': 'CAPM-only'},
        {'metric': 'n_portfolios', 'value': len(alphas)},
        {'metric': 'n_sig_10pct', 'value': sum(1 for t in tvals if abs(t) >= 1.645)},
        {'metric': 'n_sig_5pct', 'value': sum(1 for t in tvals if abs(t) >= 1.960)},
        {'metric': 'n_sig_1pct', 'value': sum(1 for t in tvals if abs(t) >= 2.576)},
        {'metric': 'mean_alpha_pct', 'value': '' if not alphas else sum(alphas) / len(alphas)},
        {'metric': 'mean_abs_alpha_pct', 'value': '' if not alphas else sum(abs(a) for a in alphas) / len(alphas)},
        {'metric': 'max_abs_alpha_pct', 'value': '' if not alphas else max(abs(a) for a in alphas)},
    ]
    write_csv(
        cfg.OUT_DIR / 'table_9c_ff1993_capm_only_diagnostics.csv',
        ['metric', 'value'],
        out_c,
    )


def main():
    build_table1_size_bm_grid()
    build_table2_factor_summary()
    build_table6_stock_regressions()
    build_table9_alpha_analogue()
    build_table9_capm_only()
    print('Done:', cfg.OUT_DIR)


if __name__ == '__main__':
    main()
