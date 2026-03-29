"""
FF1993 LaTeX table formatter — booktabs / journal-quality style
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
* Table 5: regression layout with t-stats in parentheses on separate rows,
           portfolios grouped by size quintile with \\midrule separators
* Significance stars on all t-tested quantities
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / 'output'


# ── helpers ───────────────────────────────────────────────────────────────────

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f(x, d=3):
    return '' if x in (None, '') else f'{float(x):.{d}f}'


def f3(x):  return f(x, 3)
def f4(x):  return f(x, 4)


def star(t):
    if t in (None, ''):
        return ''
    t = abs(float(t))
    if t >= 2.576:  return '$^{***}$'
    if t >= 1.960:  return '$^{**}$'
    if t >= 1.645:  return '$^{*}$'
    return ''


def tabular_booktabs(colspec, header, rows, midrule_after=None):
    """
    Build a booktabs tabular.  midrule_after = set of 0-based row indices
    after which to insert \\midrule.  Sentinel 'MIDRULE' also works inline.
    """
    lines = []
    lines.append(f'\\begin{{tabular}}{{{colspec}}}')
    lines.append('\\toprule')
    if isinstance(header[0], list):      # two-row header
        lines.append(' & '.join(header[0]) + ' \\\\')
        lines.append(' & '.join(header[1]) + ' \\\\')
    else:
        lines.append(' & '.join(header) + ' \\\\')
    lines.append('\\midrule')
    for i, r in enumerate(rows):
        if r == 'MIDRULE':
            lines.append('\\midrule')
        elif r == 'ADDLINESPACE':
            lines.append('\\addlinespace[0.4em]')
        else:
            lines.append(' & '.join(r) + ' \\\\')
        if midrule_after and i in midrule_after:
            lines.append('\\midrule')
    lines.append('\\bottomrule')
    lines.append('\\end{tabular}')
    return lines


def wrap_table(caption, label, size_cmd, tabular_lines, notes=None,
               placement='htbp'):
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


# ── Table 1  (factor summary statistics) ─────────────────────────────────────

def table_1_tex():
    rows = read_csv(OUT / 'table_1_factor_summary.csv')
    body = []
    for r in rows:
        t    = r['nw12_tstat_mean']
        sig  = star(t)
        mean = f3(r['mean_monthly_pct'])
        body.append([
            r['factor'].replace('_', '\\_'),
            r['n_months'],
            f'{mean}{sig}',
            f3(r['std_monthly_pct']),
            f3(t),
            f3(r['sharpe_monthly']),
            f3(r['autocorr1']),
            f3(r['annualized_mean_pct']),
            f3(r['annualized_vol_pct']),
        ])

    hdr = ['Factor', '$N$', 'Mean (\\%)', 'Std (\\%)', '$t$(Mean)',
           'Sharpe', 'AC(1)', 'Ann.\\ Mean (\\%)', 'Ann.\\ Vol (\\%)']
    tab = tabular_booktabs('lrrrrrrrr', hdr, body)
    notes = [
        'MKT\\textunderscore RF is the value-weighted market excess return. '
        'SMB (small minus big) and HML (high minus low) are the Fama--French '
        'size and value factors constructed from Chinese A-share stocks.',
        'Newey--West (1987) $t$-statistics with 12 lags.',
        '$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.',
    ]
    return wrap_table(
        caption='Table 1: Summary statistics for the three Fama--French factors',
        label='tab:factor_summary',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 2  (factor correlations) ───────────────────────────────────────────

def table_2_tex():
    rows = read_csv(OUT / 'table_2_factor_correlation.csv')
    body = [[r['row_factor'].replace('_', '\\_'),
             f3(r['MKT_RF']), f3(r['SMB']), f3(r['HML'])] for r in rows]
    tab = tabular_booktabs('lrrr',
                           ['Factor', 'MKT-RF', 'SMB', 'HML'],
                           body)
    notes = ['Pearson correlations computed over the full sample period.']
    return wrap_table(
        caption='Table 2: Pairwise correlations among the three factors',
        label='tab:factor_corr',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 3  (six 2×3 base portfolios) ───────────────────────────────────────

def table_3_tex():
    rows = read_csv(OUT / 'table_3_six_portfolio_summary.csv')
    body = []
    for r in rows:
        t   = r['nw12_tstat_mean']
        sig = star(t)
        body.append([
            r['portfolio'],
            r['n_months'],
            f'{f3(r["avg_monthly_return_pct"])}{sig}',
            f3(r['std_monthly_pct']),
            f3(t),
            f3(r['avg_n_stocks']),
        ])

    hdr = ['Portfolio', '$N$', 'Avg Ret (\\%)', 'Std (\\%)',
           '$t$(Mean)', 'Avg \\#Stocks']
    tab = tabular_booktabs('lrrrrr', hdr, body)
    notes = [
        'Portfolios are the six $2\\times3$ intersections of size (S = small, B = big) '
        'and book-to-market (L = low, M = medium, H = high).',
        'Newey--West (1987) $t$-statistics with 12 lags.',
        '$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.',
    ]
    return wrap_table(
        caption='Table 3: Summary statistics for the six $2\\times3$ base portfolios '
                'used to construct SMB and HML',
        label='tab:six_portfolios',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 4  (25 portfolio average excess returns — 5×5 grid) ────────────────

def table_4_tex():
    rows = read_csv(OUT / 'table_4_25port_avg_excess_returns.csv')
    grid = {(int(r['size_quintile']), int(r['bm_quintile'])):
            f3(r['avg_excess_return_pct']) for r in rows}

    ncols = 6
    hdr   = ['Size $\\backslash$ BM'] + [f'BM{j}' for j in range(1, 6)]
    body  = []
    for i in range(1, 6):
        body.append([f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)])

    tab = tabular_booktabs('l' + 'r' * 5, hdr, body)
    notes = [
        'Portfolios are the 25 intersections of five size quintiles and five '
        'book-to-market quintiles, both sorted independently each June.',
        'S1 = smallest size; BM1 = lowest book-to-market.',
        'Reported values are time-series averages of monthly excess returns (\\%).',
    ]
    return wrap_table(
        caption='Table 4: Average monthly excess returns (\\%) for '
                '$5\\times5$ size--book-to-market portfolios',
        label='tab:25port_excess_returns',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 5  (FF3 time-series regressions — Stata/journal style) ─────────────

def table_5_tex():
    rows = read_csv(OUT / 'table_5_25port_ff3_regressions.csv')

    # Sort by size_quintile then bm_quintile
    rows = sorted(rows, key=lambda r: (int(r['size_quintile']), int(r['bm_quintile'])))

    tab_lines = []
    tab_lines.append('\\begin{tabular}{lrrrrrr}')
    tab_lines.append('\\toprule')
    tab_lines.append('Portfolio & $\\alpha$ (\\%) & $b_{\\mathrm{MKT}}$ & '
                     '$b_{\\mathrm{SMB}}$ & $b_{\\mathrm{HML}}$ & $R^2$ & $N$ \\\\')
    tab_lines.append('\\midrule')

    prev_sq = None
    for r in rows:
        sq = int(r['size_quintile'])
        bq = int(r['bm_quintile'])

        # size-group separator
        if prev_sq is not None and sq != prev_sq:
            tab_lines.append('\\midrule')
        prev_sq = sq

        port = f'S{sq}B{bq}'

        # coefficient row
        a_sig  = star(r['nw12_t_alpha'])
        m_sig  = star(r['nw12_t_mkt'])
        s_sig  = star(r['nw12_t_smb'])
        h_sig  = star(r['nw12_t_hml'])

        tab_lines.append(
            f'{port} & '
            f'{f3(r["alpha_pct"])}{a_sig} & '
            f'{f4(r["beta_mkt"])}{m_sig} & '
            f'{f4(r["beta_smb"])}{s_sig} & '
            f'{f4(r["beta_hml"])}{h_sig} & '
            f'{f3(r["r2"])} & '
            f'{r["n_months"]} \\\\'
        )

        # t-stat row
        tab_lines.append(
            '{{\\footnotesize}} & '
            f'{{\\footnotesize ({f3(r["nw12_t_alpha"])})}} & '
            f'{{\\footnotesize ({f3(r["nw12_t_mkt"])})}} & '
            f'{{\\footnotesize ({f3(r["nw12_t_smb"])})}} & '
            f'{{\\footnotesize ({f3(r["nw12_t_hml"])})}} & & \\\\'
        )
        tab_lines.append('\\addlinespace[0.2em]')

    tab_lines.append('\\bottomrule')
    tab_lines.append('\\end{tabular}')

    notes = [
        'Time-series regressions: $R_{it} - R_{ft} = \\alpha_i + '
        'b_i(R_{mt}-R_{ft}) + s_i\\,\\mathrm{SMB}_t + h_i\\,\\mathrm{HML}_t + '
        '\\varepsilon_{it}$.',
        'Portfolios are the 25 $5\\times5$ size--BM intersections. '
        'S1 = smallest size; B1 = lowest book-to-market.',
        'Newey--West (1987) $t$-statistics with 12 lags in parentheses.',
        '$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.',
    ]
    return wrap_table(
        caption='Table 5: Fama--French three-factor time-series regressions '
                'for 25 size--BM portfolios',
        label='tab:ff3_regressions',
        size_cmd='\\small',
        tabular_lines=tab_lines,
        notes=notes,
        placement='p{\\textwidth}',
    )


# ── Table 6  (alpha diagnostics) ─────────────────────────────────────────────

def table_6_tex():
    rows = read_csv(OUT / 'table_6_alpha_diagnostics.csv')
    body = [[r['metric'].replace('_', '\\_'), f3(r['value'])] for r in rows]
    tab = tabular_booktabs('lr', ['Metric', 'Value'], body)
    notes = [
        'Diagnostics are computed across the 25 size--BM test portfolios.',
        'RMSE and MAE are in percentage points per month.',
    ]
    return wrap_table(
        caption='Table 6: Alpha diagnostics for the FF3 model across 25 test portfolios',
        label='tab:alpha_diagnostics',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 7  (pricing errors) ────────────────────────────────────────────────

def table_7_tex():
    all_rows = read_csv(OUT / 'table_7_pricing_errors.csv')
    # separate portfolio rows from the SUMMARY aggregates row
    port_rows    = [r for r in all_rows if r['size_quintile'] not in ('', None)]
    summary_rows = [r for r in all_rows if r['size_quintile'] in ('', None)]

    port_rows = sorted(port_rows, key=lambda r: (int(r['size_quintile']), int(r['bm_quintile'])))

    body = []
    prev_sq = None
    for r in port_rows:
        sq = int(r['size_quintile'])
        if prev_sq is not None and sq != prev_sq:
            body.append('MIDRULE')
        prev_sq = sq
        body.append([
            r['portfolio'],
            f3(r.get('actual_avg_excess_pct', '')),
            f3(r.get('fitted_avg_excess_pct', '')),
            f3(r.get('pricing_error_pct', '')),
        ])

    # Add summary row if present
    if summary_rows:
        body.append('MIDRULE')
        sr = summary_rows[0]
        body.append([
            'Summary',
            '',
            '',
            '',
        ])
        # show RMSE and MAE in a note instead

    tab = tabular_booktabs('lrrr',
                           ['Portfolio', 'Actual (\\%)', 'Fitted (\\%)', 'Error (\\%)'],
                           body)
    # pull out RMSE / MAE from summary row for the note
    rmse_note = ''
    if summary_rows:
        sr = summary_rows[0]
        rmse_note = (f'Cross-portfolio RMSE = {f3(sr.get("rmse_pct",""))}\\%, '
                     f'MAE = {f3(sr.get("mae_pct",""))}\\%.')
    notes = [
        'Actual = time-series average monthly excess return.',
        'Fitted = FF3 model-predicted average excess return.',
        'Error = Actual $-$ Fitted.',
        'Portfolios are grouped by size quintile; horizontal rules separate quintiles.',
    ]
    if rmse_note:
        notes.append(rmse_note)
    return wrap_table(
        caption='Table 7: Pricing errors --- actual vs.\\ FF3-fitted average '
                'excess returns for 25 portfolios',
        label='tab:pricing_errors',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── Table 8  (factor premia significance) ────────────────────────────────────

def table_8_tex():
    rows = read_csv(OUT / 'table_8_factor_premia_significance.csv')
    body = []
    for r in rows:
        t    = r['nw12_tstat']
        sig  = star(t)
        mean = f3(r['mean_monthly_pct'])
        body.append([
            r['factor'].replace('_', '\\_'),
            f'{mean}{sig}',
            f3(t),
            r['signif'] if r['signif'] else '---',
            r['n_months'],
        ])

    hdr = ['Factor', 'Mean (\\%)', '$t$-stat', 'Sig.', '$N$']
    tab = tabular_booktabs('lrrcr', hdr, body)
    notes = [
        'Newey--West (1987) $t$-statistics with 12 lags.',
        '$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.',
    ]
    return wrap_table(
        caption='Table 8: Statistical significance of factor risk premia',
        label='tab:factor_premia',
        size_cmd='\\small',
        tabular_lines=tab,
        notes=notes,
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    preamble = [
        '% ============================================================',
        '% Auto-generated LaTeX tables  —  Fama-French 1993 replication',
        '% ============================================================',
        '% Required packages (add to your document preamble):',
        '%   \\usepackage{booktabs}',
        '%   \\usepackage{threeparttable}',
        '%   \\usepackage{caption}',
        '',
    ]

    content = preamble + [
        table_1_tex(), '',
        table_2_tex(), '',
        table_3_tex(), '',
        table_4_tex(), '',
        table_5_tex(), '',
        table_6_tex(), '',
        table_7_tex(), '',
        table_8_tex(), '',
    ]

    out_tex = OUT / 'academic_tables.tex'
    out_tex.write_text('\n'.join(content), encoding='utf-8')
    print('Done:', out_tex)


if __name__ == '__main__':
    main()
