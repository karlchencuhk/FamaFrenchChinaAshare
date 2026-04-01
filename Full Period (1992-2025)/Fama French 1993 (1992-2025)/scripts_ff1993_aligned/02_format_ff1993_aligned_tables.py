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


def markdown_table(headers, rows):
    out = []
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def main():
    t1 = read_csv(cfg.OUT_DIR / 'table_1_ff1993_size_bm_5x5.csv')
    t2 = read_csv(cfg.OUT_DIR / 'table_2_ff1993_factor_summary.csv')
    t6 = read_csv(cfg.OUT_DIR / 'table_6a_ff1993_stock_regressions.csv')
    t9a = read_csv(cfg.OUT_DIR / 'table_9a_ff1993_alpha_by_portfolio.csv')
    t9c = read_csv(cfg.OUT_DIR / 'table_9c_ff1993_alpha_diagnostics.csv')

    lines = ['# FF1993-Aligned Tables (Full Period, Stock-side focus)', '']

    grid = {(int(r['size_quintile']), int(r['bm_quintile'])): f3(r['avg_excess_return_pct']) for r in t1}
    rows = [[f'S{i}'] + [grid.get((i, j), '') for j in range(1, 6)] for i in range(1, 6)]
    lines += ['## Table 1 (FF1993-aligned): 5x5 Size-BE/ME Portfolios, Avg Excess Return (%)',
              markdown_table(['Size\\BM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5'], rows), '']

    rows2 = [[r['factor'], f3(r['mean_monthly_pct']), f3(r['std_monthly_pct']), f3(r['nw12_tstat_mean']), f3(r['annualized_mean_pct']), f3(r['annualized_vol_pct']), r['n_months']] for r in t2]
    lines += ['## Table 2 (FF1993-aligned): Factor Summary',
              markdown_table(['Factor', 'Mean %', 'Std %', 'NW t', 'Ann Mean %', 'Ann Vol %', 'N'], rows2), '']

    rows6 = [[r['portfolio'], f3(r['alpha_pct']), f3(r['nw12_t_alpha']), f4(r['beta_mkt']), f4(r['beta_smb']), f4(r['beta_hml']), f3(r['r2'])] for r in t6]
    lines += ['## Table 6a (FF1993-aligned): Stock Regressions on MKT_RF, SMB, HML',
              markdown_table(['Portfolio', 'Alpha %', 't(alpha)', 'b_mkt', 's_smb', 'h_hml', 'R2'], rows6), '']

    rows9a = [[r['portfolio'], f3(r['alpha_pct']), f3(r['nw12_t_alpha']), f3(r['abs_alpha_pct'])] for r in t9a]
    lines += ['## Table 9a (Analogue): Alpha by Portfolio',
              markdown_table(['Portfolio', 'Alpha %', 't(alpha)', '|Alpha| %'], rows9a), '']

    rows9c = [[r['metric'], r['value']] for r in t9c]
    lines += ['## Table 9c (Analogue): Joint Alpha Diagnostics',
              markdown_table(['Metric', 'Value'], rows9c), '']

    md = '\n'.join(lines)
    (cfg.OUT_DIR / 'ff1993_aligned_tables.md').write_text(md, encoding='utf-8')
    (cfg.OUT_DIR / 'ff1993_aligned_tables.txt').write_text(md, encoding='utf-8')

    tex = ['% FF1993-aligned tables (lightweight export)', '\\section*{FF1993-aligned tables}', '\\begin{verbatim}', md, '\\end{verbatim}']
    (cfg.OUT_DIR / 'ff1993_aligned_tables.tex').write_text('\n'.join(tex), encoding='utf-8')

    print('Done:', cfg.OUT_DIR / 'ff1993_aligned_tables.md')
    print('Done:', cfg.OUT_DIR / 'ff1993_aligned_tables.tex')


if __name__ == '__main__':
    main()
