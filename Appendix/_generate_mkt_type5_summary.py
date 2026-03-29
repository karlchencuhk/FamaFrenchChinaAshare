import csv
from collections import defaultdict
from pathlib import Path

root = Path('/Users/kahouchen/Downloads/Fama French China')
appendix = root / 'Appendix'
appendix.mkdir(parents=True, exist_ok=True)

mkt_file = root / 'Raw Data' / 'Aggregated Monthly Market Returns141530201' / 'TRD_Cnmont.csv'

rows_scanned = 0
rows_type5 = 0
months_type5 = set()
stock_count_by_year = defaultdict(list)
mv_by_year = defaultdict(list)

with open(mkt_file, newline='', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows_scanned += 1
        mt = (row.get('Markettype') or '').strip().strip('"')
        if mt != '5':
            continue

        rows_type5 += 1
        m = (row.get('Trdmnt') or '').strip().strip('"')
        if not (len(m) >= 7 and m[4] == '-'):
            continue

        months_type5.add(m)
        y = int(m[:4])

        nstk_raw = (row.get('Cmnstkcal') or '').strip().strip('"')
        if nstk_raw:
            try:
                stock_count_by_year[y].append(float(nstk_raw))
            except ValueError:
                pass

        mv_raw = (row.get('Cmmvttl') or '').strip().strip('"')
        if mv_raw:
            try:
                mv_by_year[y].append(float(mv_raw))
            except ValueError:
                pass


def smean(xs):
    return sum(xs) / len(xs) if xs else None


def smin(xs):
    return min(xs) if xs else None


def smax(xs):
    return max(xs) if xs else None

start_y, end_y = 1991, 2025

csv_out = appendix / 'raw_mkt_type5_yearly_summary_1991_2025.csv'
with open(csv_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow([
        'year',
        'n_months_markettype5',
        'cmnstkcal_mean',
        'cmnstkcal_min',
        'cmnstkcal_max',
        'cmmvttl_mean',
    ])

    for y in range(start_y, end_y + 1):
        months = [m for m in months_type5 if int(m[:4]) == y]
        n_months = len(months)
        nstk = stock_count_by_year.get(y, [])
        mv = mv_by_year.get(y, [])

        w.writerow([
            y,
            n_months,
            '' if smean(nstk) is None else f'{smean(nstk):.4f}',
            '' if smin(nstk) is None else f'{smin(nstk):.0f}',
            '' if smax(nstk) is None else f'{smax(nstk):.0f}',
            '' if smean(mv) is None else f'{smean(mv):.4f}',
        ])

md_out = appendix / 'raw_mkt_type5_summary.md'
min_month = min(months_type5) if months_type5 else ''
max_month = max(months_type5) if months_type5 else ''

lines = []
lines.append('# Aggregated Market Returns (Markettype=5) Summary (Raw Data)')
lines.append('')
lines.append('- Source file: TRD_Cnmont.csv')
lines.append('- Filter: Markettype = 5 (SZSE + SSE aggregate as used in your project)')
lines.append('- Requested year range: 1991 to 2025')
lines.append('')
lines.append('## Important interpretation note')
lines.append('')
lines.append('TRD_Cnmont.csv is an aggregate market-level dataset and does **not** include firm identifiers like Stkcd.')
lines.append('So it cannot provide "unique company/entity" counts directly. Instead, this appendix reports yearly summaries of:')
lines.append('- number of available Markettype=5 months, and')
lines.append('- Cmnstkcal (count of constituent stocks in the aggregate series).')
lines.append('')
lines.append('## Coverage')
lines.append('')
lines.append(f'- Raw rows scanned: {rows_scanned:,}')
lines.append(f'- Markettype=5 rows used: {rows_type5:,}')
lines.append(f'- Markettype=5 month coverage: {min_month} to {max_month}')
lines.append('')
lines.append('## Output files')
lines.append('')
lines.append(f'- {csv_out.name}')
lines.append(f'- {md_out.name}')

md_out.write_text('\n'.join(lines), encoding='utf-8')

print(csv_out)
print(md_out)
