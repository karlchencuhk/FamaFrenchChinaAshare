import csv
from collections import defaultdict
from pathlib import Path
import importlib.util

from dt_utils import to_float, nw_tstat_mean, significance_from_t, mean, write_csv


_cfg_path = Path(__file__).with_name('00_config.py')
_spec = importlib.util.spec_from_file_location('cfg', _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def load_size_grid():
    # key: (month, size_tercile, beta_smb_bin)
    out = {}
    with open(cfg.OUTPUT_DIR / 'dt_size_3x3_monthly.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out[(row['Trdmnt'], int(row['size_tercile']), int(row['beta_smb_bin']))] = to_float(row['vw_return'])
    return out


def load_bm_grid():
    # key: (month, bm_tercile, beta_hml_bin)
    out = {}
    with open(cfg.OUTPUT_DIR / 'dt_bm_3x3_monthly.csv', newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out[(row['Trdmnt'], int(row['bm_tercile']), int(row['beta_hml_bin']))] = to_float(row['vw_return'])
    return out


def add_test(out_rows, test_family, contrast, group, series):
    mu, t = nw_tstat_mean(series, lag=cfg.NW_LAG)
    out_rows.append({
        'test_family': test_family,
        'contrast': contrast,
        'group': group,
        'mean_monthly_pct': '' if mu is None else mu * 100.0,
        'n_months': len([x for x in series if x is not None]),
        'nw12_tstat': '' if t is None else t,
        'signif': significance_from_t(t),
    })


def main():
    print('Step 5/8: running Daniel-Titman characteristic-vs-loading tests...')

    size_grid = load_size_grid()
    bm_grid = load_bm_grid()
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)

    out_rows = []

    # A) Hold characteristic (size tercile), vary loading (beta_smb high-low)
    all_spreads = []
    for s in (1, 2, 3):
        spread = []
        for m in months:
            hi = size_grid.get((m, s, 3))
            lo = size_grid.get((m, s, 1))
            spread.append((hi - lo) if (hi is not None and lo is not None) else None)
        add_test(out_rows, 'Size characteristic held fixed', 'High beta_SMB - Low beta_SMB', f'Size tercile {s}', spread)
        all_spreads.append(spread)

    pooled = []
    for i in range(len(months)):
        vals = [all_spreads[g][i] for g in range(3) if all_spreads[g][i] is not None]
        pooled.append(mean(vals) if vals else None)
    add_test(out_rows, 'Size characteristic held fixed', 'High beta_SMB - Low beta_SMB', 'Pooled across size terciles', pooled)

    # B) Hold loading (beta_smb bin), vary characteristic (small-big size)
    all_spreads = []
    for b in (1, 2, 3):
        spread = []
        for m in months:
            small = size_grid.get((m, 1, b))
            big = size_grid.get((m, 3, b))
            spread.append((small - big) if (small is not None and big is not None) else None)
        add_test(out_rows, 'beta_SMB loading held fixed', 'Small size - Big size', f'beta_SMB bin {b}', spread)
        all_spreads.append(spread)

    pooled = []
    for i in range(len(months)):
        vals = [all_spreads[g][i] for g in range(3) if all_spreads[g][i] is not None]
        pooled.append(mean(vals) if vals else None)
    add_test(out_rows, 'beta_SMB loading held fixed', 'Small size - Big size', 'Pooled across beta_SMB bins', pooled)

    # C) Hold characteristic (BM tercile), vary loading (beta_hml high-low)
    all_spreads = []
    for bm in (1, 2, 3):
        spread = []
        for m in months:
            hi = bm_grid.get((m, bm, 3))
            lo = bm_grid.get((m, bm, 1))
            spread.append((hi - lo) if (hi is not None and lo is not None) else None)
        add_test(out_rows, 'BM characteristic held fixed', 'High beta_HML - Low beta_HML', f'BM tercile {bm}', spread)
        all_spreads.append(spread)

    pooled = []
    for i in range(len(months)):
        vals = [all_spreads[g][i] for g in range(3) if all_spreads[g][i] is not None]
        pooled.append(mean(vals) if vals else None)
    add_test(out_rows, 'BM characteristic held fixed', 'High beta_HML - Low beta_HML', 'Pooled across BM terciles', pooled)

    # D) Hold loading (beta_hml bin), vary characteristic (high-low BM)
    all_spreads = []
    for b in (1, 2, 3):
        spread = []
        for m in months:
            high_bm = bm_grid.get((m, 3, b))
            low_bm = bm_grid.get((m, 1, b))
            spread.append((high_bm - low_bm) if (high_bm is not None and low_bm is not None) else None)
        add_test(out_rows, 'beta_HML loading held fixed', 'High BM - Low BM', f'beta_HML bin {b}', spread)
        all_spreads.append(spread)

    pooled = []
    for i in range(len(months)):
        vals = [all_spreads[g][i] for g in range(3) if all_spreads[g][i] is not None]
        pooled.append(mean(vals) if vals else None)
    add_test(out_rows, 'beta_HML loading held fixed', 'High BM - Low BM', 'Pooled across beta_HML bins', pooled)

    write_csv(
        cfg.OUTPUT_DIR / 'table_dt_main_tests.csv',
        ['test_family', 'contrast', 'group', 'mean_monthly_pct', 'n_months', 'nw12_tstat', 'signif'],
        out_rows,
    )

    print('Done:', cfg.OUTPUT_DIR / 'table_dt_main_tests.csv')


if __name__ == '__main__':
    main()
