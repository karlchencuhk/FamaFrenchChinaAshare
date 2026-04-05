import csv
from pathlib import Path
import importlib.util

_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f3(x):
    return '' if x in (None, '') else f"{float(x):.3f}"


def f4(x):
    return '' if x in (None, '') else f"{float(x):.4f}"


def f2(x):
    return '' if x in (None, '') else f"{float(x):.2f}"


def f0(x):
    return '' if x in (None, '') else f"{int(float(x))}"


def markdown_table(headers, rows):
    out = []
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def make_grid_from_long_df(rows, value_col, formatter):
    grid = {}
    for r in rows:
        size_q = int(r['size_quintile'])
        bm_q = int(r['bm_quintile'])
        grid[(size_q, bm_q)] = formatter(r[value_col])
    return [[f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]

def main():
    # Reading all necessary CSV files
    try:
        t_chars = read_csv(cfg.OUT_DIR / 'ff1993_portfolio_characteristics.csv')
        t1 = read_csv(cfg.OUT_DIR / 'table_1_ff1993_size_bm_5x5.csv')
        t2 = read_csv(cfg.OUT_DIR / 'table_2_ff1993_factor_summary.csv')
        t2_port = read_csv(cfg.OUT_DIR / 'table_2_ff1993_port25_stats.csv')
        t6 = read_csv(cfg.OUT_DIR / 'table_6a_ff1993_stock_regressions.csv')
        t9a_capm = read_csv(cfg.OUT_DIR / 'table_9a_ff1993_capm_only_by_portfolio.csv')
        t9a_ff3 = read_csv(cfg.OUT_DIR / 'table_9a_ff1993_alpha_by_portfolio.csv')
        # t9c = read_csv(cfg.OUT_DIR / 'table_9c_ff1993_capm_only_diagnostics.csv')
    except FileNotFoundError as e:
        print(f"Error reading file: {e}. Please ensure all data-building scripts have run successfully.")
        return

    lines = ['# FF1993-Aligned Tables (Full Period, Stock-side focus)', '']

    # --- Updated Table Generation ---
    # Table 1a: Average Firm Size (ME)
    rows_size = make_grid_from_long_df(t_chars, 'avg_me_rmb_mm', f0)
    lines += ['## Table 1a (Analogue): Average Firm Size (ME, RMB MM)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], rows_size), '']

    # Table 1b: Average % of Total Market Value
    rows_mkt_pct = make_grid_from_long_df(t_chars, 'avg_me_pct_of_total', f2)
    lines += ['## Table 1b (Analogue): Average % of Total Market Value',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], rows_mkt_pct), '']

    # Table 1c: Average Number of Firms
    rows_n_firms = make_grid_from_long_df(t_chars, 'avg_n_firms', f0)
    lines += ['## Table 1c (Analogue): Average Number of Firms',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], rows_n_firms), '']

    grid = {(int(r['size_quintile']), int(r['bm_quintile'])): f3(r['avg_excess_return_pct']) for r in t1}
    rows = [[f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]
    lines += ['## Table 1e (FF1993-aligned): 5x5 Size-BE/ME Portfolios, Avg Excess Return (%)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], rows), '']

    rows2 = [[r['factor'], f3(r['mean_monthly_pct']), f3(r['std_monthly_pct']), f3(r['nw12_tstat_mean']), f3(r['annualized_mean_pct']), f3(r['annualized_vol_pct']), r['n_months']] for r in t2]
    lines += ['## Table 2 (FF1993-aligned): Factor Summary',
              markdown_table(['Factor', 'Mean %', 'Std %', 'NW t', 'Ann Mean %', 'Ann Vol %', 'N'], rows2), '']

    grid_mean = make_grid_from_long_df(t2_port, 'mean_pct', f3)
    grid_std  = make_grid_from_long_df(t2_port, 'std_pct', f2)
    grid_t    = make_grid_from_long_df(t2_port, 'nw12_tstat', f3)
    hdr = ['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5']
    lines += ['## Table 2 (Extended): 25-Portfolio Return Statistics',
              '### Panel A: Mean Excess Return (%/month)',
              markdown_table(hdr, grid_mean), '',
              '### Panel B: Standard Deviation (%/month)',
              markdown_table(hdr, grid_std), '',
              '### Panel C: NW t-statistic (mean ≠ 0)',
              markdown_table(hdr, grid_t), '']

    def make_grid(rows, key, formatter):
        grid = {}
        for r in rows:
            p = r['portfolio']
            s_part, b_part = p.split('B')
            s = int(s_part.replace('S', ''))
            b = int(b_part)
            grid[(s, b)] = formatter(r[key])
        return [[f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]

    lines += ['## Table 6a (FF1993-aligned): Stock Regressions on MKT_RF, SMB, HML', '']
    
    panel_defs = [
        ('Panel A: Alpha (%)', 'alpha_pct', f3),
        ('Panel B: t-statistic for Alpha', 'nw12_t_alpha', f3),
        ('Panel C: Market Beta (b_mkt)', 'beta_mkt', f4),
        ('Panel D: SMB Loading (s_smb)', 'beta_smb', f4),
        ('Panel E: HML Loading (h_hml)', 'beta_hml', f4),
        ('Panel F: R-squared', 'r2', f3),
    ]

    for title, key, formatter in panel_defs:
        lines.append(f'#### {title}')
        grid_rows = make_grid(t6, key, formatter)
        lines.append(markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], grid_rows))
        lines.append('')

    def make_alpha_grids(rows):
        grid_alpha = {}
        grid_t = {}
        for r in rows:
            p = r['portfolio']
            s_part, b_part = p.split('B')
            s = int(s_part.replace('S', ''))
            b = int(b_part)
            grid_alpha[(s, b)] = f3(r['alpha_pct'])
            grid_t[(s, b)] = f3(r['nw12_t_alpha'])
        rows_alpha = [[f'S{i}'] + [grid_alpha.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]
        rows_t = [[f'S{i}'] + [grid_t.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]
        return rows_alpha, rows_t

    capm_alpha, capm_t = make_alpha_grids(t9a_capm)
    ff3_alpha, ff3_t = make_alpha_grids(t9a_ff3)

    lines += ['## Table 9a (Analogue): Alpha Grids by Size and BE/ME',
              '### CAPM only',
              '#### Panel A: Alpha (%)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], capm_alpha),
              '',
              '#### Panel B: t(alpha)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], capm_t),
              '',
              '### 3-factor model',
              '#### Panel A: Alpha (%)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], ff3_alpha),
              '',
              '#### Panel B: t(alpha)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], ff3_t),
              '']

    # rows9c = [[r['metric'], r['value']] for r in t9c]
    # lines += ['## Table 9c (Analogue, CAPM only): Alpha Diagnostics',
    #           markdown_table(['Metric', 'Value'], rows9c), '']

    md = '\n'.join(lines)
    (cfg.OUT_DIR / 'ff1993_aligned_tables.md').write_text(md, encoding='utf-8')
    (cfg.OUT_DIR / 'ff1993_aligned_tables.txt').write_text(md, encoding='utf-8')

    tex = ['% FF1993-aligned tables (lightweight export)', '\\section*{FF1993-aligned tables}', '\\begin{verbatim}', md, '\\end{verbatim}']
    (cfg.OUT_DIR / 'ff1993_aligned_tables.tex').write_text('\n'.join(tex), encoding='utf-8')

    print('Done:', cfg.OUT_DIR / 'ff1993_aligned_tables.md')
    print('Done:', cfg.OUT_DIR / 'ff1993_aligned_tables.tex')


if __name__ == '__main__':
    main()
