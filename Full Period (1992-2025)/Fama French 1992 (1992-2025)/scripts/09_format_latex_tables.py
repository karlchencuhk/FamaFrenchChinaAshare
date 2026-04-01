"""
FF1992 LaTeX table formatter — booktabs / journal-quality style
================================================================
Produces academic_tables.tex suitable for direct inclusion in a paper.

LaTeX packages required in your preamble:
    \\usepackage{booktabs}
    \\usepackage{threeparttable}
    \\usepackage{caption}

Formatting features
-------------------
* booktabs rules  (\\toprule / \\midrule / \\cmidrule / \\bottomrule)
* \\threeparttable footnotes with significance legend
* \\label{tab:...} for cross-referencing
* Table III: Stata-style regression layout
      columns = model specifications (1)–(7)
      rows    = variables; t-statistics in parentheses on the row below
* Significance stars on all t-tested quantities
* Panel separators via \\multicolumn labels inside a single tabular
"""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / 'output'


# ── low-level helpers ─────────────────────────────────────────────────────────

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f(x, d=3):
    """Format to d decimal places; return empty string for missing values."""
    return '' if x in (None, '') else f'{float(x):.{d}f}'


def f3(x):  return f(x, 3)
def f4(x):  return f(x, 4)


def star(t):
    """Return significance stars based on |t|-statistic."""
    if t in (None, ''):
        return ''
    t = abs(float(t))
    if t >= 2.576:  return '$^{***}$'
    if t >= 1.960:  return '$^{**}$'
    if t >= 1.645:  return '$^{*}$'
    return ''


def esc(s):
    return str(s).replace('%', '\\%').replace('_', '\\_')


# ── table-building helpers ────────────────────────────────────────────────────

def tabular_booktabs(colspec, header, rows):
    """
    Build a booktabs tabular block.
    Special sentinel strings in *rows*:
      'MIDRULE'     → inserts \\midrule
      'ADDLINESPACE' → inserts \\addlinespace[0.4em]
    """
    lines = []
    lines.append(f'\\begin{{tabular}}{{{colspec}}}')
    lines.append('\\toprule')
    lines.append(' & '.join(header) + ' \\\\')
    lines.append('\\midrule')
    for r in rows:
        if r == 'MIDRULE':
            lines.append('\\midrule')
        elif r == 'ADDLINESPACE':
            lines.append('\\addlinespace[0.4em]')
        else:
            lines.append(' & '.join(r) + ' \\\\')
    lines.append('\\bottomrule')
    lines.append('\\end{tabular}')
    return lines


def wrap_table(caption, label, size_cmd, tabular_lines,
               notes=None, placement='htbp'):
    """Wrap tabular lines in table / threeparttable."""
    L = []
    L.append(f'\\begin{{table}}[{placement}]')
    L.append('\\centering')
    L.append(f'\\caption{{{caption}}}')
    L.append(f'\\label{{{label}}}')
    L.append(size_cmd)
    if notes:
        L.append('\\begin{threeparttable}')
    L += tabular_lines
    if notes:
        L.append('\\begin{tablenotes}[flushleft]')
        L.append('\\footnotesize')
        for n in notes:
            L.append(f'\\item {n}')
        L.append('\\end{tablenotes}')
        L.append('\\end{threeparttable}')
    L.append('\\end{table}')
    return '\n'.join(L)


# ── Table I ───────────────────────────────────────────────────────────────────

def table_i_tex():
    rows = read_csv(OUT / 'table_i_size_beta_10x10.csv')
    ret   = defaultdict(dict)
    pbeta = defaultdict(dict)
    avgsz = defaultdict(dict)
    for r in rows:
        s = int(r['size_decile'])
        b = int(r['beta_decile_within_size'])
        ret[s][b]   = f3(r['avg_monthly_return_pct'])
        pbeta[s][b] = f4(r['post_ranking_beta'])
        # display avg size in RMB millions (original unit: RMB thousands)
        avgsz[s][b] = f(float(r['avg_size']) / 1_000, 1) if r['avg_size'] else ''

    ncols = 11   # 1 label + 10 beta columns
    hdr   = ['Size $\\backslash$ $\\beta$'] + [f'B{j}' for j in range(1, 11)]

    body = []
    # Panel A
    body.append([f'\\multicolumn{{{ncols}}}{{l}}'
                 '{\\textit{Panel A: Average monthly returns (\\%)}}'])
    body.append('MIDRULE')
    for s in range(1, 11):
        body.append([f'S{s}'] + [ret[s].get(j, '') for j in range(1, 11)])
    body.append('MIDRULE')

    # Panel B
    body.append([f'\\multicolumn{{{ncols}}}{{l}}'
                 '{\\textit{Panel B: Post-ranking betas}}'])
    body.append('MIDRULE')
    for s in range(1, 11):
        body.append([f'S{s}'] + [pbeta[s].get(j, '') for j in range(1, 11)])
    body.append('MIDRULE')

    # Panel C
    body.append([f'\\multicolumn{{{ncols}}}{{l}}'
                 '{\\textit{Panel C: Average market equity (RMB millions)}}'])
    body.append('MIDRULE')
    for s in range(1, 11):
        body.append([f'S{s}'] + [avgsz[s].get(j, '') for j in range(1, 11)])

    tab = tabular_booktabs('l' + 'r' * 10, hdr, body)
    notes = [
        'Portfolios are formed in June of each year by independent double-sorts on '
        'size (market equity, ME) into 10 deciles and pre-ranking beta into 10 '
        'deciles within each size group.',
        'Size decile 1 (S1) is smallest; beta decile 1 (B1) is lowest beta.',
        'Post-ranking betas are estimated using 24–60 monthly returns after '
        'portfolio formation.',
        'Market equity is measured in RMB millions.',
    ]
    return wrap_table(
        caption='Table I: Average monthly returns, post-ranking betas, and average '
                'market equity for portfolios double-sorted on size and pre-ranking beta',
        label='tab:size_beta_10x10',
        size_cmd='\\footnotesize',
        tabular_lines=tab,
        notes=notes,
        placement='p{\\textwidth}',
    )


# ── Table II ──────────────────────────────────────────────────────────────────

def table_ii_tex():
    srows = read_csv(OUT / 'table_ii_size_only.csv')
    brows = read_csv(OUT / 'table_ii_beta_only.csv')
    left  = {r['portfolio']: r for r in srows}
    right = {r['portfolio']: r for r in brows}

    # Build tabular manually to support panel headers
    tab_lines = []
    tab_lines.append('\\begin{tabular}{lrrrr}')
    tab_lines.append('\\toprule')

    tab_lines.append('\\multicolumn{5}{l}{\\textit{Panel A: Portfolios formed on size (ME)}} \\\\')
    tab_lines.append('\\midrule')
    tab_lines.append('Decile & Average Return (\\%) & Post-$\\beta$ & $\\ln(ME)$ & $\\ln(BE/ME)$ \\\\')
    tab_lines.append('\\midrule')
    for i in range(1, 11):
        sr = left.get(f'S{i}', {})
        row = [
            str(i),
            f3(sr.get('avg_monthly_return_pct', '')),
            f4(sr.get('post_ranking_beta', '')),
            f4(sr.get('avg_ln_me', '')),
            f4(sr.get('avg_ln_be_me', '')),
        ]
        tab_lines.append(' & '.join(row) + ' \\\\')

    tab_lines.append('\\midrule')
    tab_lines.append('\\multicolumn{5}{l}{\\textit{Panel B: Portfolios formed on pre-ranking beta}} \\\\')
    tab_lines.append('\\midrule')
    tab_lines.append('Decile & Average Return (\\%) & Post-$\\beta$ & $\\ln(ME)$ & $\\ln(BE/ME)$ \\\\')
    tab_lines.append('\\midrule')
    for i in range(1, 11):
        br = right.get(f'B{i}', {})
        row = [
            str(i),
            f3(br.get('avg_monthly_return_pct', '')),
            f4(br.get('post_ranking_beta', '')),
            f4(br.get('avg_ln_me', '')),
            f4(br.get('avg_ln_be_me', '')),
        ]
        tab_lines.append(' & '.join(row) + ' \\\\')

    tab_lines.append('\\bottomrule')
    tab_lines.append('\\end{tabular}')

    notes = [
        'Portfolios are formed in June of each year on a single characteristic.',
        'Panel A: decile 1 has the smallest market equity (ME).',
        'Panel B: decile 1 has the lowest pre-ranking beta.',
        '$\\ln(ME)$ and $\\ln(BE/ME)$ are portfolio averages of firm-level June characteristics used in the monthly memberships.',
    ]
    return wrap_table(
        caption='Table II: Univariate portfolio characteristics for size-sorted and '
            'pre-ranking-beta-sorted deciles',
        label='tab:size_beta_univariate',
        size_cmd='\\small',
        tabular_lines=tab_lines,
        notes=notes,
    )


# ── Table III  (Stata-style FM regression) ────────────────────────────────────

def table_iii_tex():
    rows = read_csv(OUT / 'table_iii_fama_macbeth.csv')

    model_order = [
        'M1_beta', 'M2_ln_size', 'M3_ln_be_me',
        'M4_beta_ln_size', 'M5_beta_ln_be_me',
        'M6_ln_size_ln_be_me', 'M7_all3',
    ]
    coef_order = ['intercept', 'beta', 'ln_size', 'ln_be_me']
    coef_label = {
        'intercept': 'Intercept',
        'beta':      '$\\beta$',
        'ln_size':   '$\\ln(ME)$',
        'ln_be_me':  '$\\ln(BE/ME)$',
    }
    n_models = len(model_order)

    # index: d[model][coef] = (avg_lambda, nw12_tstat)
    d = defaultdict(dict)
    n_obs = {}
    for r in rows:
        m, c = r['model'], r['coefficient']
        d[m][c] = (r['avg_lambda'], r['nw12_tstat'])

    # number of monthly cross-sections — read from first row per model
    # (not stored separately; use row count proxy — omit N row for now)

    # Build column header: (1) … (7) over model labels
    short_label = {
        'M1_beta':               '(1)',
        'M2_ln_size':            '(2)',
        'M3_ln_be_me':           '(3)',
        'M4_beta_ln_size':       '(4)',
        'M5_beta_ln_be_me':      '(5)',
        'M6_ln_size_ln_be_me':   '(6)',
        'M7_all3':               '(7)',
    }

    tab_lines = []
    tab_lines.append('\\begin{tabular}{l' + 'c' * n_models + '}')
    tab_lines.append('\\toprule')
    tab_lines.append(' & ' + ' & '.join(short_label[m] for m in model_order) + ' \\\\')
    tab_lines.append('\\midrule')

    for c in coef_order:
        # coefficient row
        coef_cells = []
        for m in model_order:
            if c in d[m]:
                lam, t = d[m][c]
                sig = star(t)
                coef_cells.append(f'{f4(lam)}{sig}')
            else:
                coef_cells.append('')
        tab_lines.append(coef_label[c] + ' & ' + ' & '.join(coef_cells) + ' \\\\')

        # t-stat row (parentheses, smaller font)
        tstat_cells = []
        for m in model_order:
            if c in d[m]:
                _, t = d[m][c]
                tstat_cells.append(f'({f3(t)})')
            else:
                tstat_cells.append('')
        tab_lines.append('{\\footnotesize} & ' +
                         ' & '.join(f'{{\\footnotesize {tc}}}' for tc in tstat_cells) + ' \\\\')
        tab_lines.append('\\addlinespace[0.3em]')

    tab_lines.append('\\bottomrule')
    tab_lines.append('\\end{tabular}')

    notes = [
        'Each column reports time-series averages of monthly Fama--MacBeth '
        '(1973) cross-sectional regression slopes.',
        'Newey--West (1987) $t$-statistics with 12 lags are in parentheses.',
        '$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.',
        'Returns are measured as raw monthly returns. '
        '$\\ln(ME)$ is log market equity at June-end; '
        '$\\ln(BE/ME)$ is log book-to-market measured in December of the prior year.',
    ]
    return wrap_table(
        caption='Table III: Fama--MacBeth cross-sectional regressions --- '
                'average slopes from monthly regressions of stock returns '
                'on beta, size, and book-to-market',
        label='tab:fama_macbeth',
        size_cmd='\\small',
        tabular_lines=tab_lines,
        notes=notes,
    )


# ── Table IV ──────────────────────────────────────────────────────────────────

def table_iv_tex():
    rows = read_csv(OUT / 'table_iv_beme_only.csv')
    body = []
    for r in rows:
        dec = r['portfolio'].replace('M', '')
        body.append([dec,
                     f3(r['avg_monthly_return_pct']),
                     f4(r.get('post_ranking_beta', '')),
                     f4(r.get('avg_ln_me', '')),
                     f4(r.get('avg_ln_be_me', ''))])

    tab = tabular_booktabs('crrrr',
                           ['BE/ME Decile', 'Avg Monthly Return (\\%)', 'Post-$\\beta$', '$\\ln(ME)$', '$\\ln(BE/ME)$'],
                           body)
    notes = [
        'Portfolios are formed in June of each year by sorting all stocks into '
        '10 equal groups on book-to-market equity (BE/ME).',
        'Decile 1 (M1) has the lowest BE/ME; decile 10 has the highest.',
        '$\\ln(ME)$ and $\\ln(BE/ME)$ are portfolio averages of firm-level June characteristics used in monthly memberships.',
    ]
    return wrap_table(
        caption='Table IV: Characteristics of portfolios formed on BE/ME alone',
        label='tab:beme_univariate',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table V ───────────────────────────────────────────────────────────────────

def table_v_tex():
    rows = read_csv(OUT / 'table_v_size_beme_10x10.csv')
    ret = defaultdict(dict)
    for r in rows:
        s = int(r['size_decile'])
        m = int(r['beme_decile_within_size'])
        ret[s][m] = f3(r['avg_monthly_return_pct'])

    ncols = 11
    hdr   = ['Size $\\backslash$ BE/ME'] + [f'M{j}' for j in range(1, 11)]

    body = []
    body.append([f'\\multicolumn{{{ncols}}}{{l}}'
                 '{\\textit{Panel A: Average monthly returns (\\%)}}'])
    body.append('MIDRULE')
    for s in range(1, 11):
        body.append([f'S{s}'] + [ret[s].get(j, '') for j in range(1, 11)])

    tab = tabular_booktabs('l' + 'r' * 10, hdr, body)
    notes = [
        'Portfolios are formed in June of each year by independent double-sorts '
        'on size (ME) into 10 deciles and book-to-market (BE/ME) into 10 deciles '
        'within each size group.',
        'Size decile 1 (S1) is smallest; BE/ME decile 1 (M1) is lowest BE/ME.',
    ]
    return wrap_table(
        caption='Table V: Average monthly returns (\\%) for portfolios '
                'double-sorted on size and book-to-market equity',
        label='tab:size_beme_10x10',
        size_cmd='\\footnotesize',
        tabular_lines=tab,
        notes=notes,
        placement='p{\\textwidth}',
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    preamble = [
        '% ============================================================',
        '% Auto-generated LaTeX tables  —  Fama-French 1992 replication',
        '% ============================================================',
        '% Required packages (add to your document preamble):',
        '%   \\usepackage{booktabs}',
        '%   \\usepackage{threeparttable}',
        '%   \\usepackage{caption}',
        '',
    ]

    content = preamble + [
        table_i_tex(),   '',
        table_ii_tex(),  '',
        table_iii_tex(), '',
        table_iv_tex(),  '',
        table_v_tex(),   '',
    ]

    out_tex = OUT / 'academic_tables.tex'
    out_tex.write_text('\n'.join(content), encoding='utf-8')
    print('Done:', out_tex)


if __name__ == '__main__':
    main()
