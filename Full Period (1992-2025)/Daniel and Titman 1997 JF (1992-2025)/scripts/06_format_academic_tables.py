import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f3(x):
    return '' if x in (None, '') else f"{float(x):.3f}"


def markdown_table(headers, rows):
    out = []
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def table_dt_md():
    rows = read_csv(OUT / 'table_dt_main_tests.csv')
    headers = ['Test family', 'Contrast', 'Group', 'Mean spread (%/mo)', 'NW12 t', 'Sig', 'N months']
    body = []
    for r in rows:
        body.append([
            r['test_family'],
            r['contrast'],
            r['group'],
            f3(r['mean_monthly_pct']),
            f3(r['nw12_tstat']),
            r['signif'],
            r['n_months'],
        ])

    txt = []
    txt.append('## Table 1. Daniel-Titman Characteristic-vs-Loading Tests (1992-2025)')
    txt.append(markdown_table(headers, body))
    txt.append('')
    txt.append('Interpretation guide:')
    txt.append('- Characteristics view (Daniel-Titman): significant characteristic spreads when loadings are held fixed, and weak loading spreads when characteristics are held fixed.')
    txt.append('- Risk-loading view (Fama-French): significant loading spreads when characteristics are held fixed.')
    return '\n'.join(txt)


def main():
    content = '\n'.join([
        '# Daniel and Titman (1997) Style Tests — China 1992-2025',
        '',
        table_dt_md(),
        '',
    ])

    out_md = OUT / 'academic_tables.md'
    out_txt = OUT / 'academic_tables.txt'
    out_md.write_text(content, encoding='utf-8')
    out_txt.write_text(content, encoding='utf-8')

    print('Done:', out_md)
    print('Done:', out_txt)


if __name__ == '__main__':
    main()
