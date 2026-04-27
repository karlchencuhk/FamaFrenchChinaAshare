import csv
import math
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def f3(x):
    return '' if x in (None, '') else f"{float(x):.3f}"


def f4(x):
    return '' if x in (None, '') else f"{float(x):.4f}"

def exp_level(x):
    if x in (None, ''):
        return ''
    return math.exp(float(x))


def star(t):
    if t in (None, ''):
        return ''
    t = abs(float(t))
    if t >= 2.576:
        return '***'
    if t >= 1.960:
        return '**'
    if t >= 1.645:
        return '*'
    return ''


def markdown_table(headers, rows):
    out = []
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def build_table_i_md():
    rows = read_csv(OUT / 'table_i_size_beta_10x10.csv')
    ret = defaultdict(dict)
    pbeta = defaultdict(dict)
    avgsz = defaultdict(dict)
    for r in rows:
        s = int(r['size_decile'])
        b = int(r['beta_decile_within_size'])
        ret[s][b] = f3(r['avg_monthly_return_pct'])
        pbeta[s][b] = f4(r['post_ranking_beta'])
        avgsz[s][b] = f3(r['avg_size'])

    hdr = ['Size\\Beta'] + [f'B{j}' for j in range(1, 11)]

    panel_ret = []
    for s in range(1, 11):
        panel_ret.append([f'S{s}'] + [ret[s].get(j, '') for j in range(1, 11)])

    panel_beta = []
    for s in range(1, 11):
        panel_beta.append([f'S{s}'] + [pbeta[s].get(j, '') for j in range(1, 11)])

    panel_sz = []
    for s in range(1, 11):
        panel_sz.append([f'S{s}'] + [avgsz[s].get(j, '') for j in range(1, 11)])

    txt = []
    txt.append('## Table I. 10x10 Portfolios Formed on Size and Pre-ranking Beta')
    txt.append('### Panel A: Average Monthly Returns (%)')
    txt.append(markdown_table(hdr, panel_ret))
    txt.append('')
    txt.append('### Panel B: Post-ranking Beta')
    txt.append(markdown_table(hdr, panel_beta))
    txt.append('')
    txt.append('### Panel C: Average Size')
    txt.append(markdown_table(hdr, panel_sz))
    return '\n'.join(txt)


def build_table_ii_md():
    srows = read_csv(OUT / 'table_ii_size_only.csv')
    brows = read_csv(OUT / 'table_ii_beta_only.csv')

    left = {r['portfolio']: r for r in srows}
    right = {r['portfolio']: r for r in brows}

    headers = ['Decile', 'Average Return (%)', 'Post-ranking Beta', 'ln(ME)', 'ln(BE/ME)', 'ME', 'BE/ME']

    rows_size = []
    for i in range(1, 11):
        sr = left.get(f'S{i}', {})
        rows_size.append([
            str(i),
            f3(sr.get('avg_monthly_return_pct', '')),
            f4(sr.get('post_ranking_beta', '')),
            f4(sr.get('avg_ln_me', '')),
            f4(sr.get('avg_ln_be_me', '')),
            f3(sr.get('avg_size', '')),
            f4(exp_level(sr.get('avg_ln_be_me', ''))),
        ])

    rows_beta = []
    for i in range(1, 11):
        br = right.get(f'B{i}', {})
        rows_beta.append([
            str(i),
            f3(br.get('avg_monthly_return_pct', '')),
            f4(br.get('post_ranking_beta', '')),
            f4(br.get('avg_ln_me', '')),
            f4(br.get('avg_ln_be_me', '')),
            f3(br.get('avg_size', '')),
            f4(exp_level(br.get('avg_ln_be_me', ''))),
        ])

    txt = []
    txt.append('## Table II. Univariate Portfolios on Size and on Beta')
    txt.append('### Panel A: Portfolios Formed on Size (ME)')
    txt.append(markdown_table(headers, rows_size))
    txt.append('')
    txt.append('### Panel B: Portfolios Formed on Pre-ranking Beta')
    txt.append(markdown_table(headers, rows_beta))
    return '\n'.join(txt)


def build_table_iii_md():
    rows = read_csv(OUT / 'table_iii_fama_macbeth.csv')
    order = [
        'M1_beta', 'M2_ln_size', 'M3_ln_be_me',
        'M4_beta_ln_size', 'M5_beta_ln_be_me', 'M6_ln_size_ln_be_me',
        'M7_all3'
    ]
    coef_order = ['intercept', 'beta', 'ln_size', 'ln_be_me']

    d = defaultdict(dict)
    for r in rows:
        m = r['model']
        c = r['coefficient']
        lam = f4(r['avg_lambda'])
        t = f3(r['nw12_tstat'])
        sig = star(r['nw12_tstat'])
        d[m][c] = f"{lam}{sig} (t={t})"

    out_rows = []
    for m in order:
        out_rows.append([m] + [d[m].get(c, '') for c in coef_order])

    txt = []
    txt.append('## Table III. Fama-MacBeth Cross-sectional Regressions (NW12 t-stats)')
    txt.append(markdown_table(['Model'] + coef_order, out_rows))
    txt.append('')
    txt.append('Significance: * 10%, ** 5%, *** 1%')
    return '\n'.join(txt)


def build_table_iv_md():
    rows = read_csv(OUT / 'table_iv_beme_only.csv')
    headers = ['BE/ME Decile', 'Avg Monthly Return (%)', 'Post-ranking Beta', 'ln(ME)', 'ln(BE/ME)', 'ME', 'BE/ME']
    out = []
    for r in rows:
        d = r['portfolio'].replace('M', '')
        out.append([
            d,
            f3(r['avg_monthly_return_pct']),
            f4(r.get('post_ranking_beta', '')),
            f4(r.get('avg_ln_me', '')),
            f4(r.get('avg_ln_be_me', '')),
            f3(r.get('avg_size', '')),
            f4(exp_level(r.get('avg_ln_be_me', ''))),
        ])

    txt = []
    txt.append('## Table IV. Portfolios Formed on BE/ME Alone')
    txt.append(markdown_table(headers, out))
    return '\n'.join(txt)


def build_table_v_md():
    rows = read_csv(OUT / 'table_v_size_beme_10x10.csv')
    ret = defaultdict(dict)
    for r in rows:
        s = int(r['size_decile'])
        m = int(r['beme_decile_within_size'])
        ret[s][m] = f3(r['avg_monthly_return_pct'])

    hdr = ['Size\\BE/ME'] + [f'M{j}' for j in range(1, 11)]
    out = []
    for s in range(1, 11):
        out.append([f'S{s}'] + [ret[s].get(j, '') for j in range(1, 11)])

    txt = []
    txt.append('## Table V. 10x10 Portfolios Formed on Size and BE/ME')
    txt.append('### Panel A: Average Monthly Returns (%)')
    txt.append(markdown_table(hdr, out))
    return '\n'.join(txt)


def main():
    sections = [
        '# Fama-French 1992 Replication Tables (Academic-style Markdown)',
        '',
        build_table_i_md(),
        '',
        build_table_ii_md(),
        '',
        build_table_iii_md(),
        '',
        build_table_iv_md(),
        '',
        build_table_v_md(),
        ''
    ]

    out_md = OUT / 'academic_tables.md'
    out_txt = OUT / 'academic_tables.txt'
    content = '\n'.join(sections)

    out_md.write_text(content, encoding='utf-8')
    out_txt.write_text(content, encoding='utf-8')

    print('Done:', out_md)
    print('Done:', out_txt)


if __name__ == '__main__':
    main()
