import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f3(x):
    return '' if x in (None, '') else f"{float(x):.3f}"


def f4(x):
    return '' if x in (None, '') else f"{float(x):.4f}"


def markdown_table(headers, rows):
    out = []
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def table_1_md():
    rows = read_csv(OUT / 'table_1_factor_summary.csv')
    headers = ['Factor', 'N', 'Mean(%)', 'Std(%)', 'NW12 t(Mean)', 'Sharpe', 'AC(1)', 'Ann Mean(%)', 'Ann Vol(%)']
    out = []
    for r in rows:
        out.append([
            r['factor'],
            r['n_months'],
            f3(r['mean_monthly_pct']),
            f3(r['std_monthly_pct']),
            f3(r['nw12_tstat_mean']),
            f3(r['sharpe_monthly']),
            f3(r['autocorr1']),
            f3(r['annualized_mean_pct']),
            f3(r['annualized_vol_pct']),
        ])

    txt = []
    txt.append('## Table 1. Factor Summary Statistics')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_2_md():
    rows = read_csv(OUT / 'table_2_factor_correlation.csv')
    headers = ['Factor', 'MKT_RF', 'SMB', 'HML']
    out = []
    for r in rows:
        out.append([r['row_factor'], f3(r['MKT_RF']), f3(r['SMB']), f3(r['HML'])])

    txt = []
    txt.append('## Table 2. Factor Correlation Matrix')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_3_md():
    rows = read_csv(OUT / 'table_3_six_portfolio_summary.csv')
    headers = ['Portfolio', 'N', 'Avg Return(%)', 'Std(%)', 'NW12 t(Mean)', 'Avg #Stocks']
    out = []
    for r in rows:
        out.append([
            r['portfolio'],
            r['n_months'],
            f3(r['avg_monthly_return_pct']),
            f3(r['std_monthly_pct']),
            f3(r['nw12_tstat_mean']),
            f3(r['avg_n_stocks']),
        ])

    txt = []
    txt.append('## Table 3. Six Base Portfolios (2x3 Size-BM)')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_4_md():
    rows = read_csv(OUT / 'table_4_25port_avg_excess_returns.csv')
    grid = {(int(r['size_quintile']), int(r['bm_quintile'])): f3(r['avg_excess_return_pct']) for r in rows}

    headers = ['Size\\BM'] + [f'BM{j}' for j in range(1, 6)]
    out = []
    for i in range(1, 6):
        out.append([f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)])

    txt = []
    txt.append('## Table 4. Average Excess Returns of 25 Size-BM Portfolios (%)')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_5_md():
    rows = read_csv(OUT / 'table_5_25port_ff3_regressions.csv')
    headers = ['Portfolio', 'alpha(%)', 't(alpha)', 'beta_mkt', 't(mkt)', 'beta_smb', 't(smb)', 'beta_hml', 't(hml)', 'R2']
    out = []
    for r in rows:
        out.append([
            r['portfolio'],
            f3(r['alpha_pct']),
            f3(r['nw12_t_alpha']),
            f4(r['beta_mkt']),
            f3(r['nw12_t_mkt']),
            f4(r['beta_smb']),
            f3(r['nw12_t_smb']),
            f4(r['beta_hml']),
            f3(r['nw12_t_hml']),
            f3(r['r2']),
        ])

    txt = []
    txt.append('## Table 5. Time-series Regressions of 25 Portfolios on FF3 Factors (NW12 t-stats)')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_6_md():
    rows = read_csv(OUT / 'table_6_alpha_diagnostics.csv')
    headers = ['Metric', 'Value']
    out = [[r['metric'], f3(r['value'])] for r in rows]

    txt = []
    txt.append('## Table 6. Alpha Diagnostics Across 25 Test Portfolios')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_7_md():
    rows = read_csv(OUT / 'table_7_pricing_errors.csv')
    headers = ['Portfolio', 'Actual Avg Excess(%)', 'Fitted Avg Excess(%)', 'Pricing Error(%)', 'RMSE(%)', 'MAE(%)']
    out = []
    for r in rows:
        out.append([
            r['portfolio'],
            f3(r.get('actual_avg_excess_pct')),
            f3(r.get('fitted_avg_excess_pct')),
            f3(r.get('pricing_error_pct')),
            f3(r.get('rmse_pct')),
            f3(r.get('mae_pct')),
        ])

    txt = []
    txt.append('## Table 7. Pricing Errors: Actual vs FF3-Fitted Returns')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def table_8_md():
    rows = read_csv(OUT / 'table_8_factor_premia_significance.csv')
    headers = ['Factor', 'Mean(%)', 'NW12 t', 'Significance', 'N']
    out = []
    for r in rows:
        out.append([r['factor'], f3(r['mean_monthly_pct']), f3(r['nw12_tstat']), r['signif'], r['n_months']])

    txt = []
    txt.append('## Table 8. Factor Premia Significance')
    txt.append(markdown_table(headers, out))
    txt.append('')
    txt.append('Significance: * 10%, ** 5%, *** 1%')
    return '\n'.join(txt)


def main():
    sections = [
        '# Fama-French 1993 (3-Factor) Replication Tables',
        '',
        table_1_md(),
        '',
        table_2_md(),
        '',
        table_3_md(),
        '',
        table_4_md(),
        '',
        table_5_md(),
        '',
        table_6_md(),
        '',
        table_7_md(),
        '',
        table_8_md(),
        '',
    ]

    content = '\n'.join(sections)
    out_md = OUT / 'academic_tables.md'
    out_txt = OUT / 'academic_tables.txt'
    out_md.write_text(content, encoding='utf-8')
    out_txt.write_text(content, encoding='utf-8')

    print('Done:', out_md)
    print('Done:', out_txt)


if __name__ == '__main__':
    main()
