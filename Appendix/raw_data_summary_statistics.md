# Raw Data Summary Statistics (Source Files Only)

This appendix uses only raw files and does not rely on derived outputs.

## A. Entity count by year (stock monthly file)

- Source file: TRD_Mnth_SSE_A_SZSE_A.txt
- Entity definition: unique Stkcd appearing in any month within the calendar year
- Year range requested: 1991 to 2025

| Year | Unique entities |
| --- | ---: |
| 1991 | 13 |
| 1992 | 53 |
| 1993 | 176 |
| 1994 | 288 |
| 1995 | 312 |
| 1996 | 515 |
| 1997 | 721 |
| 1998 | 826 |
| 1999 | 924 |
| 2000 | 1061 |
| 2001 | 1140 |
| 2002 | 1207 |
| 2003 | 1267 |
| 2004 | 1363 |
| 2005 | 1366 |
| 2006 | 1418 |
| 2007 | 1517 |
| 2008 | 1577 |
| 2009 | 1644 |
| 2010 | 1867 |
| 2011 | 2020 |
| 2012 | 2101 |
| 2013 | 2115 |
| 2014 | 2186 |
| 2015 | 2318 |
| 2016 | 2463 |
| 2017 | 2754 |
| 2018 | 2831 |
| 2019 | 2907 |
| 2020 | 3041 |
| 2021 | 3151 |
| 2022 | 3206 |
| 2023 | 3231 |
| 2024 | 3218 |
| 2025 | 3213 |

## B. Raw-file coverage snapshot

| Raw file | Rows | Coverage / Notes |
| --- | ---: | --- |
| TRD_Mnth_SSE_A_SZSE_A.txt | 693,590 | Months: 1990-12 to 2026-02; Unique entities overall: 3,473; Markettype values: 1, 4 |
| FS_Combas.csv | 664,177 | Accounting years: 1990 to 2025; Unique entities: 5,873 |
| TRD_Cnmont.csv | 8,022 | Unique months: 423; Markettype values: 19 |
| TRD_Nrrate.csv | 12,886 | Dates (parsed): 1990-04-15 to 2026-03-26 |

## C. Output files generated

- raw_stock_entities_by_year_1991_2025.csv
- raw_data_summary_statistics.md