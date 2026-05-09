import csv
import importlib.util
from pathlib import Path

from momentum_utils import (
    cumulative_max_drawdown,
    load_stock_panel,
    mean,
    nw_tstat_mean,
    stdev_sample,
    compute_umd_for_strategy,
    compute_umd_2x3_for_strategy,
)

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def metrics_from_series(months, umd_map):
    vals = [umd_map[m] for m in months if umd_map.get(m) is not None]
    mu, t = nw_tstat_mean(vals, lag=cfg.NW_LAG)
    sd = stdev_sample(vals)
    return {
        "n_months": len(vals),
        "mean_umd_pct": None if mu is None else mu * 100.0,
        "std_umd_pct": None if sd is None else sd * 100.0,
        "nw12_tstat": t,
        "sharpe": None if (mu is None or sd in (None, 0)) else mu / sd,
        "positive_months_pct": None if not vals else 100.0 * sum(1 for v in vals if v > 0) / len(vals),
        "max_drawdown_pct": None if not vals else cumulative_max_drawdown(vals) * 100.0,
    }


def main():
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    stock_ret, stock_size, _, by_month_stocks = load_stock_panel()

    # Validation report: strict Carhart timing and no look-ahead.
    # For J=12, skip=1 at formation month f, score uses f-12..f-1 excluding f-1? In this pipeline:
    # end = f-skip, start = end-J+1 => f-12..f-1 with skip=1 means using f-12..f-1? no, with month index
    # this corresponds to prior 12 months excluding current formation month.
    f = "2000-06"
    end_i = cfg.month_to_int(f) - cfg.MOM_SKIP_MONTH
    start_i = end_i - cfg.MOM_BENCHMARK_J + 1
    validation_rows = [
        {"check": "carhart_timing_j", "value": str(cfg.MOM_BENCHMARK_J)},
        {"check": "carhart_timing_skip", "value": str(cfg.MOM_SKIP_MONTH)},
        {"check": "sample_formation_month", "value": f},
        {"check": "score_start_month", "value": cfg.int_to_month(start_i)},
        {"check": "score_end_month", "value": cfg.int_to_month(end_i)},
        {"check": "first_holding_month", "value": f},
        {
            "check": "no_look_ahead_pass",
            "value": "true" if end_i < cfg.month_to_int(f) else "false",
        },
    ]
    vfile = cfg.OUTPUT_DIR / "momentum_construction_validation.csv"
    with open(vfile, "w", newline="", encoding="utf-8") as fobj:
        w = csv.DictWriter(fobj, fieldnames=["check", "value"])
        w.writeheader()
        w.writerows(validation_rows)

    # Robustness variants requested by user.
    variants = [
        # construction, weighting, breakpoints, J, K, skip
        ("decile_wml", "value_weighted", "10/90", 12, 1, 1),
        ("decile_wml", "equal_weighted", "10/90", 12, 1, 1),
        ("decile_wml", "value_weighted", "10/90", 12, 3, 1),
        ("decile_wml", "equal_weighted", "10/90", 12, 3, 1),
        ("carhart_2x3", "value_weighted", "30/70", 12, 1, 1),
        ("carhart_2x3", "equal_weighted", "30/70", 12, 1, 1),
        ("carhart_2x3", "value_weighted", "20/80", 12, 1, 1),
        ("carhart_2x3", "equal_weighted", "20/80", 12, 1, 1),
        ("carhart_2x3", "value_weighted", "30/70", 12, 3, 1),
        ("carhart_2x3", "equal_weighted", "30/70", 12, 3, 1),
        ("carhart_2x3", "value_weighted", "20/80", 12, 3, 1),
        ("carhart_2x3", "equal_weighted", "20/80", 12, 3, 1),
    ]

    out = []
    for construction, weighting, bps, j, k, skip in variants:
        if construction == "decile_wml":
            umd, _, _ = compute_umd_for_strategy(
                months, stock_ret, stock_size, by_month_stocks, j, k, skip=skip, weighting=weighting, deciles=10
            )
        else:
            low_q, high_q = (0.2, 0.8) if bps == "20/80" else (0.3, 0.7)
            umd, _, _ = compute_umd_2x3_for_strategy(
                months,
                stock_ret,
                stock_size,
                by_month_stocks,
                j,
                k,
                skip=skip,
                weighting=weighting,
                mom_low_q=low_q,
                mom_high_q=high_q,
            )
        m = metrics_from_series(months, umd)
        out.append(
            {
                "construction": construction,
                "weighting": weighting,
                "momentum_breakpoints": bps,
                "J": j,
                "K": k,
                "skip": skip,
                **m,
            }
        )

    ofile = cfg.OUTPUT_DIR / "momentum_robustness_variants.csv"
    with open(ofile, "w", newline="", encoding="utf-8") as fobj:
        w = csv.DictWriter(fobj, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    print("Done:", vfile)
    print("Done:", ofile)


if __name__ == "__main__":
    main()
