import csv
import importlib.util
from pathlib import Path

from momentum_utils import (
    mean,
    stdev_sample,
    nw_tstat_mean,
    cumulative_max_drawdown,
    load_stock_panel,
    compute_umd_for_strategy,
)

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def main():
    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    stock_ret, stock_size, _, by_month_stocks = load_stock_panel()

    rows = []
    for j, k in cfg.MOM_STRATEGIES:
        umd, wret, lret = compute_umd_for_strategy(
            months, stock_ret, stock_size, by_month_stocks, j, k, skip=cfg.MOM_SKIP_MONTH
        )
        umd_series = [umd[m] for m in months if umd.get(m) is not None]
        winner_series = [wret[m] for m in months if wret.get(m) is not None]
        loser_series = [lret[m] for m in months if lret.get(m) is not None]

        mu, t = nw_tstat_mean(umd_series, lag=cfg.NW_LAG)
        sd = stdev_sample(umd_series)
        sharpe = (mu / sd) if (mu is not None and sd not in (None, 0)) else None
        pos = (sum(1 for x in umd_series if x > 0) / len(umd_series) * 100.0) if umd_series else None
        mdd = cumulative_max_drawdown(umd_series)

        rows.append(
            {
                "strategy": f"{j}/{k}",
                "J": j,
                "K": k,
                "n_months": len(umd_series),
                "mean_umd_pct": None if mu is None else mu * 100.0,
                "std_umd_pct": None if sd is None else sd * 100.0,
                "nw12_tstat": t,
                "sharpe": sharpe,
                "positive_months_pct": pos,
                "max_drawdown_pct": None if mdd is None else mdd * 100.0,
                "avg_winner_return_pct": None if not winner_series else mean(winner_series) * 100.0,
                "avg_loser_return_pct": None if not loser_series else mean(loser_series) * 100.0,
            }
        )

    # Titman-style reporting: keep the predefined strategy grid order.
    # No in-sample "best strategy" optimization score is used here.

    out = cfg.OUTPUT_DIR / "momentum_optimization.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    alias_out = cfg.OUTPUT_DIR / "table_momentum_optimization.csv"
    with open(alias_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Done:", out)
    print("Done:", alias_out)


if __name__ == "__main__":
    main()
