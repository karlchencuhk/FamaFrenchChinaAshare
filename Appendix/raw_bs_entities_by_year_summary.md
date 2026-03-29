# Balance Sheet Unique Company Count by Year (Raw Data)

- Source file: FS_Combas.csv
- Requested year range: 1991 to 2025
- Raw rows scanned: 664,177
- Accounting date coverage: 1990-12-31 to 2025-12-31

## Notes

- `all_typrep`: counts unique `Stkcd` in each year using all `Typrep` values.
- `typrep_A`: counts unique `Stkcd` in each year using only `Typrep = A` rows.

## Output files

- raw_bs_entities_by_year_1991_2025.csv
- raw_bs_entities_by_year_typrepA_1991_2025.csv
- raw_bs_entities_by_year_summary.md