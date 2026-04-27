import csv
import importlib.util
from pathlib import Path

from momentum_utils import mean, stdev_sample, nw_tstat_mean

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, "") else None


def corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n <= 1:
        return None
    xvals = [p[0] for p in pairs]
    yvals = [p[1] for p in pairs]
    mx = sum(xvals) / n
    my = sum(yvals) / n
    sxx = sum((x - mx) ** 2 for x in xvals)
    syy = sum((y - my) ** 2 for y in yvals)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def main():
    ff3_file = cfg.BASE_FF3_OUTPUT / "ff3_factors_monthly.csv"
    umd_file = cfg.OUTPUT_DIR / "umd_factor_monthly.csv"

    ff3_map = {}
    with open(ff3_file, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ff3_map[r["Trdmnt"]] = r

    umd_map = {}
    with open(umd_file, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            umd_map[r["Trdmnt"]] = r

    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    rows = []
    for m in months:
        f3 = ff3_map.get(m, {})
        u = umd_map.get(m, {})
        rows.append(
            {
                "Trdmnt": m,
                "RF": to_float(f3.get("RF")),
                "MKT_RF": to_float(f3.get("MKT_RF")),
                "SMB": to_float(f3.get("SMB")),
                "HML": to_float(f3.get("HML")),
                "UMD": to_float(u.get("UMD")),
            }
        )

    ff4_file = cfg.OUTPUT_DIR / "ff4_factors_monthly.csv"
    with open(ff4_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    factors = ["MKT_RF", "SMB", "HML", "UMD"]
    summary = []
    for fac in factors:
        s = [r[fac] for r in rows if r[fac] is not None]
        mu, t = nw_tstat_mean(s, lag=cfg.NW_LAG)
        sd = stdev_sample(s)
        sharpe = (mu / sd) if (mu is not None and sd not in (None, 0)) else None
        summary.append(
            {
                "factor": fac,
                "mean_pct": None if mu is None else mu * 100.0,
                "std_pct": None if sd is None else sd * 100.0,
                "nw12_tstat": t,
                "sharpe": sharpe,
                "min_pct": None if not s else min(s) * 100.0,
                "max_pct": None if not s else max(s) * 100.0,
                "positive_pct": None if not s else 100.0 * sum(1 for v in s if v > 0) / len(s),
            }
        )

    summary_file = cfg.OUTPUT_DIR / "ff4_factor_summary.csv"
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    summary_alias = cfg.OUTPUT_DIR / "table_1_factor_summary_with_momentum.csv"
    with open(summary_alias, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    corr_rows = []
    for ra in factors:
        row = {"row_factor": ra}
        for rb in factors:
            row[rb] = corr([r[ra] for r in rows], [r[rb] for r in rows])
        corr_rows.append(row)

    corr_file = cfg.OUTPUT_DIR / "ff4_factor_correlation.csv"
    with open(corr_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(corr_rows[0].keys()))
        w.writeheader()
        w.writerows(corr_rows)
    corr_alias = cfg.OUTPUT_DIR / "table_2_factor_correlation_with_momentum.csv"
    with open(corr_alias, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(corr_rows[0].keys()))
        w.writeheader()
        w.writerows(corr_rows)

    print("Done:", ff4_file)
    print("Done:", summary_file)
    print("Done:", corr_file)
    print("Done:", summary_alias)
    print("Done:", corr_alias)


if __name__ == "__main__":
    main()
