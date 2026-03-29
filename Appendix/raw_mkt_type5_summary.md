# Aggregated Market Returns (Markettype=5) Summary (Raw Data)

- Source file: TRD_Cnmont.csv
- Filter: Markettype = 5 (SZSE + SSE aggregate as used in your project)
- Requested year range: 1991 to 2025

## Important interpretation note

TRD_Cnmont.csv is an aggregate market-level dataset and does **not** include firm identifiers like Stkcd.
So it cannot provide "unique company/entity" counts directly. Instead, this appendix reports yearly summaries of:
- number of available Markettype=5 months, and
- Cmnstkcal (count of constituent stocks in the aggregate series).

## Coverage

- Raw rows scanned: 8,022
- Markettype=5 rows used: 423
- Markettype=5 month coverage: 1990-12 to 2026-02

## Output files

- raw_mkt_type5_yearly_summary_1991_2025.csv
- raw_mkt_type5_summary.md