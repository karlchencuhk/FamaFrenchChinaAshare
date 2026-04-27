import csv
import importlib.util
from pathlib import Path

from momentum_utils import mean, stdev_sample, nw_tstat_mean, load_stock_panel, compute_umd_for_strategy

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def subset(months, series_map, start_m, end_m):
    return [series_map[m] for m in months if start_m <= m <= end_m and series_map.get(m) is not None]


def main():
    ff4_file = cfg.OUTPUT_DIR / "ff4_factors_monthly.csv"
    umd = {}
    months = []
    with open(ff4_file, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m = r["Trdmnt"]
            months.append(m)
            v = r.get("UMD")
            umd[m] = float(v) if v not in (None, "") else None

    periods = [
        ("1992-2010", cfg.RETURN_START, "2010-03"),
        ("2010-2025", "2010-04", cfg.RETURN_END),
        ("full", cfg.RETURN_START, cfg.RETURN_END),
    ]
    out = []
    for name, s, e in periods:
        vals = subset(months, umd, s, e)
        mu, t = nw_tstat_mean(vals, lag=cfg.NW_LAG)
        sd = stdev_sample(vals)
        out.append(
            {
                "segment": name,
                "start": s,
                "end": e,
                "n_months": len(vals),
                "mean_umd_pct": None if mu is None else mu * 100.0,
                "std_umd_pct": None if sd is None else sd * 100.0,
                "nw12_tstat": t,
            }
        )

    # Reversal check: J=1,K=1,skip=0
    stock_ret, stock_size, _, by_month_stocks = load_stock_panel()
    umd_rev, _, _ = compute_umd_for_strategy(months, stock_ret, stock_size, by_month_stocks, 1, 1, skip=0)
    vals = [umd_rev[m] for m in months if umd_rev.get(m) is not None]
    mu, t = nw_tstat_mean(vals, lag=cfg.NW_LAG)
    out.append(
        {
            "segment": "reversal_1_1_skip0",
            "start": cfg.RETURN_START,
            "end": cfg.RETURN_END,
            "n_months": len(vals),
            "mean_umd_pct": None if mu is None else mu * 100.0,
            "std_umd_pct": None if stdev_sample(vals) is None else stdev_sample(vals) * 100.0,
            "nw12_tstat": t,
        }
    )

    # Industry-neutral placeholder (project has no industry file wired in this pipeline)
    out.append(
        {
            "segment": "industry_neutral_note",
            "start": "",
            "end": "",
            "n_months": "",
            "mean_umd_pct": "",
            "std_umd_pct": "",
            "nw12_tstat": "",
        }
    )

    out_file = cfg.OUTPUT_DIR / "momentum_subperiod_analysis.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("Done:", out_file)


if __name__ == "__main__":
    main()
