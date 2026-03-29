"""Auto-generated wrapper for ff3_factors_monthly.csv."""
from pathlib import Path
import csv
import sys
import html
import webbrowser

CSV_PATH = Path(__file__).with_suffix('.csv')


def _read_rows_with_fallback():
    last_err = None
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin1'):
        try:
            with open(CSV_PATH, newline='', encoding=enc) as f:
                rows = list(csv.DictReader(f))
            return rows
        except Exception as e:
            last_err = e
    raise last_err


def load_records():
    return _read_rows_with_fallback()


def load_dataframe():
    import pandas as pd
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin1'):
        try:
            return pd.read_csv(CSV_PATH, encoding=enc)
        except Exception:
            pass
    return pd.read_csv(CSV_PATH)


def _to_html_table(cols, rows):
    head = ''.join(f'<th>{html.escape(str(c))}</th>' for c in cols)
    body_parts = []
    for r in rows:
        tds = ''.join(f'<td>{html.escape(str(r.get(c, "")))}</td>' for c in cols)
        body_parts.append(f'<tr>{tds}</tr>')
    body = ''.join(body_parts)
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def show_table(max_rows=20000):
    rows = load_records()
    cols = list(rows[0].keys()) if rows else []
    shown = rows[:max_rows]

    info = f'Rows displayed: {len(shown):,} / {len(rows):,} | Columns: {len(cols)}'
    if len(rows) > max_rows:
        info += f' (increase max_rows in show_table() if needed)'

    if rows:
        table_html = _to_html_table(cols, shown)
    else:
        table_html = '<p><b>CSV has no rows.</b></p>'

    doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Table Viewer - {html.escape(CSV_PATH.name)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin: 12px; }}
    .info {{ margin-bottom: 10px; color: #333; font-size: 13px; }}
    .wrap {{ overflow: auto; max-height: 88vh; border: 1px solid #ddd; }}
    table {{ border-collapse: collapse; font-size: 12px; white-space: nowrap; }}
    thead th {{ position: sticky; top: 0; background: #f5f7fb; z-index: 1; }}
    th, td {{ border: 1px solid #ddd; padding: 4px 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <div class="info"><b>{html.escape(CSV_PATH.name)}</b> — {html.escape(info)}</div>
  <div class="wrap">{table_html}</div>
</body>
</html>
"""

    out_html = CSV_PATH.with_suffix('.viewer.html')
    out_html.write_text(doc, encoding='utf-8')
    webbrowser.open(out_html.as_uri())


if __name__ == '__main__':
    # Click "Run Python File" in VS Code to open browser table.
    # Optional: run with --no-gui to print a quick preview in terminal.
    if '--no-gui' in sys.argv:
        rows = load_records()
        print(f'{CSV_PATH.name}: {len(rows)} rows')
        for row in rows[:5]:
            print(row)
    else:
        show_table()
