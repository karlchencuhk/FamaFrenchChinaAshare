import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f3(x):
    return '' if x in (None, '') else f'{float(x):.3f}'


def tex_escape(s):
    return (s.replace('_', '\\_').replace('%', '\\%'))


def table_1_tex():
    rows = read_csv(OUT / 'table_dt_main_tests.csv')
    lines = []
    lines.append('\\begin{table}[htbp]')
    lines.append('\\centering')
    lines.append('\\caption{Daniel--Titman characteristic-versus-loading tests (1992--2025)}')
    lines.append('\\label{tab:dt_main}')
    lines.append('\\small')
    lines.append('\\begin{tabular}{p{3.0cm}p{3.0cm}p{3.2cm}rrrr}')
    lines.append('\\toprule')
    lines.append('Test family & Contrast & Group & Mean (\\%) & $t_{NW12}$ & Sig & $N$ \\\\')
    lines.append('\\midrule')
    for r in rows:
        lines.append(
            f"{tex_escape(r['test_family'])} & {tex_escape(r['contrast'])} & {tex_escape(r['group'])} & "
            f"{f3(r['mean_monthly_pct'])} & {f3(r['nw12_tstat'])} & {r['signif']} & {r['n_months']} \\\\"
        )
    lines.append('\\bottomrule')
    lines.append('\\end{tabular}')
    lines.append('\\vspace{0.4em}')
    lines.append('\\begin{minipage}{0.92\\linewidth}')
    lines.append('\\footnotesize Notes: Monthly spreads are in percentage points. Newey--West $t$-statistics use 12 lags.')
    lines.append('\\end{minipage}')
    lines.append('\\end{table}')
    return '\n'.join(lines)


def main():
    tex = '\n\n'.join([
        '% Auto-generated LaTeX tables for Daniel and Titman tests',
        table_1_tex(),
        '',
    ])
    out_tex = OUT / 'academic_tables.tex'
    out_tex.write_text(tex, encoding='utf-8')
    print('Done:', out_tex)


if __name__ == '__main__':
    main()
