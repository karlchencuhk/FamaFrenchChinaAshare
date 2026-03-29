import csv
from collections import defaultdict
from pathlib import Path

root = Path('/Users/kahouchen/Downloads/Fama French China')
appendix = root / 'Appendix'
appendix.mkdir(parents=True, exist_ok=True)

stock_file = root / 'Monthly Stock Price  Returns121529524' / 'TRD_Mnth_SSE_A_SZSE_A.txt'
bs_file = root / 'Balance Sheet110248807' / 'FS_Combas.csv'
mkt_file = root / 'Aggregated Monthly Market Returns141530201' / 'TRD_Cnmont.csv'
rf_file = root / 'Risk-Free Rate135436249' / 'TRD_Nrrate.csv'

# ---------- Stock-level yearly entity counts ----------
entities_by_year = defaultdict(set)
rows_stock = 0
min_month = None
max_month = None
markettypes = set()
all_entities = set()

with open(stock_file, newline='', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows_stock += 1
        stk = (row.get('Stkcd') or '').strip().zfill(6)
        m = (row.get('Trdmnt') or '').strip()
        mt = (row.get('Markettype') or '').strip()
        if mt:
            markettypes.add(mt)
        if len(m) >= 7 and m[4] == '-':
            if min_month is None or m < min_month:
                min_month = m
            if max_month is None or m > max_month:
                max_month = m
            try:
                y = int(m[:4])
            except ValueError:
                continue
            if stk:
                entities_by_year[y].add(stk)
                all_entities.add(stk)

# Requested window
start_y, end_y = 1991, 2025
year_counts = [(y, len(entities_by_year.get(y, set()))) for y in range(start_y, end_y + 1)]

csv_out = appendix / 'raw_stock_entities_by_year_1991_2025.csv'
with open(csv_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['year', 'n_unique_entities'])
    w.writerows(year_counts)

# ---------- Other raw-data summary stats ----------
# Balance sheet
rows_bs = 0
bs_entities = set()
bs_years = set()
with open(bs_file, newline='', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows_bs += 1
        stk = (row.get('Stkcd') or '').strip().zfill(6)
        if stk:
            bs_entities.add(stk)
        acc = (row.get('Accper') or '').strip()
        if len(acc) >= 4 and acc[:4].isdigit():
            bs_years.add(int(acc[:4]))

# Market returns
rows_mkt = 0
mkt_months = set()
mkt_types = set()
with open(mkt_file, newline='', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows_mkt += 1
        m = (row.get('Trdmnt') or '').strip().strip('"')
        mt = (row.get('Markettype') or '').strip().strip('"')
        if m:
            mkt_months.add(m)
        if mt:
            mkt_types.add(mt)

# Risk-free
rows_rf = 0
rf_dates = []
with open(rf_file, newline='', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    _ = next(r, None)
    for row in r:
        if not row or len(row) < 4:
            continue
        rows_rf += 1
        d = row[1].strip()
        if len(d) == 10 and d[4] == '-' and d[7] == '-':
            rf_dates.append(d)

rf_min = min(rf_dates) if rf_dates else ''
rf_max = max(rf_dates) if rf_dates else ''

# ---------- Markdown appendix ----------
md_out = appendix / 'raw_data_summary_statistics.md'

lines = []
lines.append('# Raw Data Summary Statistics (Source Files Only)')
lines.append('')
lines.append('This appendix uses only raw files and does not rely on derived outputs.')
lines.append('')
lines.append('## A. Entity count by year (stock monthly file)')
lines.append('')
lines.append(f'- Source file: {stock_file.name}')
lines.append('- Entity definition: unique Stkcd appearing in any month within the calendar year')
lines.append('- Year range requested: 1991 to 2025')
lines.append('')
lines.append('| Year | Unique entities |')
lines.append('| --- | ---: |')
for y, c in year_counts:
    lines.append(f'| {y} | {c} |')
lines.append('')
lines.append('## B. Raw-file coverage snapshot')
lines.append('')
lines.append('| Raw file | Rows | Coverage / Notes |')
lines.append('| --- | ---: | --- |')
lines.append(
    f'| TRD_Mnth_SSE_A_SZSE_A.txt | {rows_stock:,} | Months: {min_month} to {max_month}; Unique entities overall: {len(all_entities):,}; Markettype values: {", ".join(sorted(markettypes))} |'
)
lines.append(
    f'| FS_Combas.csv | {rows_bs:,} | Accounting years: {min(bs_years) if bs_years else ""} to {max(bs_years) if bs_years else ""}; Unique entities: {len(bs_entities):,} |'
)
lines.append(
    f'| TRD_Cnmont.csv | {rows_mkt:,} | Unique months: {len(mkt_months):,}; Markettype values: {len(mkt_types):,} |'
)
lines.append(
    f'| TRD_Nrrate.csv | {rows_rf:,} | Dates (parsed): {rf_min} to {rf_max} |'
)
lines.append('')
lines.append('## C. Output files generated')
lines.append('')
lines.append(f'- {csv_out.name}')
lines.append(f'- {md_out.name}')

md_out.write_text('\n'.join(lines), encoding='utf-8')

print(csv_out)
print(md_out)
