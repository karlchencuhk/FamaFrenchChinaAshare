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


def main():
    t1 = read_csv(OUT / 'table_1_factor_summary.csv')
    t2 = read_csv(OUT / 'table_2_factor_correlation.csv')
    t3 = read_csv(OUT / 'table_3_six_portfolio_summary.csv')
    t4 = read_csv(OUT / 'table_4_25port_avg_excess_returns.csv')
    t5 = read_csv(OUT / 'table_5_25port_ff3_ep_regressions.csv')
    t6 = read_csv(OUT / 'table_6_alpha_diagnostics.csv')
    t7 = read_csv(OUT / 'table_7_pricing_errors.csv')
    t8 = read_csv(OUT / 'table_8_factor_premia_significance.csv')

    sections = ['# Fama-French 1993-style (E/P Value Leg) Replication Tables', '']

    sections += ['## Table 1. Factor Summary Statistics', markdown_table(
        ['Factor', 'N', 'Mean(%)', 'Std(%)', 'NW12 t(Mean)', 'Sharpe', 'AC(1)', 'Ann Mean(%)', 'Ann Vol(%)'],
        [[r['factor'], r['n_months'], f3(r['mean_monthly_pct']), f3(r['std_monthly_pct']), f3(r['nw12_tstat_mean']),
          f3(r['sharpe_monthly']), f3(r['autocorr1']), f3(r['annualized_mean_pct']), f3(r['annualized_vol_pct'])] for r in t1]
    ), '']

    sections += ['## Table 2. Factor Correlation Matrix', markdown_table(
        ['Factor', 'MKT_RF', 'SMB', 'HML_EP'],
        [[r['row_factor'], f3(r['MKT_RF']), f3(r['SMB']), f3(r['HML_EP'])] for r in t2]
    ), '']

    sections += ['## Table 3. Six Base Portfolios (2x3 Size-EP)', markdown_table(
        ['Portfolio', 'N', 'Avg Return(%)', 'Std(%)', 'NW12 t(Mean)', 'Avg #Stocks'],
        [[r['portfolio'], r['n_months'], f3(r['avg_monthly_return_pct']), f3(r['std_monthly_pct']),
          f3(r['nw12_tstat_mean']), f3(r['avg_n_stocks'])] for r in t3]
    ), '']

    grid = {(int(r['size_quintile']), int(r['ep_quintile'])): f3(r['avg_excess_return_pct']) for r in t4}
    rows4 = [[f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]
    sections += ['## Table 4. Average Excess Returns of 25 Size-EP Portfolios (%)', markdown_table(
        ['Size\\EP', 'EP1', 'EP2', 'EP3', 'EP4', 'EP5'], rows4
    ), '']

    sections += ['## Table 5. Time-series Regressions of 25 Portfolios on MKT_RF, SMB, HML_EP', markdown_table(
        ['Portfolio', 'alpha(%)', 't(alpha)', 'beta_mkt', 't(mkt)', 'beta_smb', 't(smb)', 'beta_hml_ep', 't(hml_ep)', 'R2'],
        [[r['portfolio'], f3(r['alpha_pct']), f3(r['nw12_t_alpha']), f4(r['beta_mkt']), f3(r['nw12_t_mkt']),
          f4(r['beta_smb']), f3(r['nw12_t_smb']), f4(r['beta_hml_ep']), f3(r['nw12_t_hml_ep']), f3(r['r2'])] for r in t5]
    ), '']

    sections += ['## Table 6. Alpha Diagnostics Across 25 Test Portfolios', markdown_table(
        ['Metric', 'Value'], [[r['metric'], f3(r['value'])] for r in t6]
    ), '']

    sections += ['## Table 7. Pricing Errors: Actual vs Model-Fitted Returns', markdown_table(
        ['Portfolio', 'Actual Avg Excess(%)', 'Fitted Avg Excess(%)', 'Pricing Error(%)', 'RMSE(%)', 'MAE(%)'],
        [[r['portfolio'], f3(r.get('actual_avg_excess_pct')), f3(r.get('fitted_avg_excess_pct')),
          f3(r.get('pricing_error_pct')), f3(r.get('rmse_pct')), f3(r.get('mae_pct'))] for r in t7]
    ), '']

    sections += ['## Table 8. Factor Premia Significance', markdown_table(
        ['Factor', 'Mean(%)', 'NW12 t', 'Significance', 'N'],
        [[r['factor'], f3(r['mean_monthly_pct']), f3(r['nw12_tstat']), r['signif'], r['n_months']] for r in t8]
    ), '', 'Significance: * 10%, ** 5%, *** 1%', '']

    content = '\n'.join(sections)
    (OUT / 'academic_tables.md').write_text(content, encoding='utf-8')
    (OUT / 'academic_tables.txt').write_text(content, encoding='utf-8')
    print('Done:', OUT / 'academic_tables.md')
    print('Done:', OUT / 'academic_tables.txt')


if __name__ == '__main__':
    main()
