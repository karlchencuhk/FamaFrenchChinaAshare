import csv
import math


def to_float(x):
    if x in (None, ''):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def clean_row(row):
    out = {}
    for k, v in row.items():
        kk = (k or '').replace('\ufeff', '').strip().strip('"')
        vv = '' if v is None else v.strip().strip('"')
        out[kk] = vv
    return out


def iter_clean_csv(path, encoding='utf-8-sig'):
    with open(path, newline='', encoding=encoding) as f:
        r = csv.DictReader(f)
        for row in r:
            yield clean_row(row)


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
    v = sum((x - mu) ** 2 for x in vals) / (n - 1)
    return math.sqrt(v)


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

    S = gamma(0)
    L = min(lag, t - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (L + 1)
        S += 2.0 * w * gamma(l)

    var_mu = S / t
    if var_mu <= 0:
        return mu, None

    se = math.sqrt(var_mu)
    tstat = mu / se if se > 0 else None
    return mu, tstat


def significance_from_t(t):
    if t is None:
        return ''
    a = abs(t)
    if a >= 2.576:
        return '***'
    if a >= 1.960:
        return '**'
    if a >= 1.645:
        return '*'
    return ''


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


def ols(y, x_cols):
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

    return {
        'beta': beta,
        'n': n,
    }


def assign_bins_rank(values, cuts):
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


def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
