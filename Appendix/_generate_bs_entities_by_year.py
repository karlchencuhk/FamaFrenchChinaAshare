import csv
from collections import defaultdict
from pathlib import Path

root = Path('/Users/kahouchen/Downloads/Fama French China')
appendix = root / 'Appendix'
appendix.mkdir(parents=True, exist_ok=True)

bs_file = root / 'Raw Data' / 'Balance Sheet110248807' / 'FS_Combas.csv'

# Unique companies by accounting year (all rows)
all_by_year = defaultdict(set)
# Unique companies by accounting year for Typrep == 'A'
a_by_year = defaultdict(set)

rows = 0
acc_min = None
acc_max = None

with open(bs_file, newline='', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows += 1
        stk = (row.get('Stkcd') or '').strip().zfill(6)
        acc = (row.get('Accper') or '').strip()
        typ = (row.get('Typrep') or '').strip().strip('"')

        if not stk or len(acc) < 4 or not acc[:4].isdigit():
            continue

        y = int(acc[:4])
        all_by_year[y].add(stk)
        if typ == 'A':
            a_by_year[y].add(stk)

        if len(acc) >= 10 and acc[4] == '-' and acc[7] == '-':
            if acc_min is None or acc < acc_min:
                acc_min = acc
            if acc_max is None or acc > acc_max:
                acc_max = acc

start_y, end_y = 1991, 2025

csv_all = appendix / 'raw_bs_entities_by_year_1991_2025.csv'
with open(csv_all, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['year', 'n_unique_companies_all_typrep'])
    for y in range(start_y, end_y + 1):
        w.writerow([y, len(all_by_year.get(y, set()))])

csv_a = appendix / 'raw_bs_entities_by_year_typrepA_1991_2025.csv'
with open(csv_a, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['year', 'n_unique_companies_typrep_A'])
    for y in range(start_y, end_y + 1):
        w.writerow([y, len(a_by_year.get(y, set()))])

md_out = appendix / 'raw_bs_entities_by_year_summary.md'
lines = []
lines.append('# Balance Sheet Unique Company Count by Year (Raw Data)')
lines.append('')
lines.append('- Source file: FS_Combas.csv')
lines.append('- Requested year range: 1991 to 2025')
lines.append(f'- Raw rows scanned: {rows:,}')
lines.append(f'- Accounting date coverage: {acc_min} to {acc_max}')
lines.append('')
lines.append('## Notes')
lines.append('')
lines.append('- `all_typrep`: counts unique `Stkcd` in each year using all `Typrep` values.')
lines.append('- `typrep_A`: counts unique `Stkcd` in each year using only `Typrep = A` rows.')
lines.append('')
lines.append('## Output files')
lines.append('')
lines.append(f'- {csv_all.name}')
lines.append(f'- {csv_a.name}')
lines.append(f'- {md_out.name}')

md_out.write_text('\n'.join(lines), encoding='utf-8')

print(csv_all)
print(csv_a)
print(md_out)
