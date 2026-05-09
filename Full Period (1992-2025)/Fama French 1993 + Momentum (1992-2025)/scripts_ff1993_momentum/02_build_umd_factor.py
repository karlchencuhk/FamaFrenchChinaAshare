import csv
import importlib.util
from pathlib import Path

from momentum_utils import load_stock_panel, compute_umd_for_strategy

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, "") else None


def main():
    opt_file = cfg.OUTPUT_DIR / "momentum_optimization.csv"
    with open(opt_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_strategy = {r["strategy"]: r for r in rows}
    benchmark_key = f"{cfg.MOM_BENCHMARK_J}/{cfg.MOM_BENCHMARK_K}"
    chosen = by_strategy.get(benchmark_key)
    if chosen is None:
        raise RuntimeError(f"Benchmark strategy {benchmark_key} not found in momentum_optimization.csv")
    j = int(chosen["J"])
    k = int(chosen["K"])

    months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    stock_ret, stock_size, _, by_month_stocks = load_stock_panel()
    umd, wret, lret = compute_umd_for_strategy(
        months, stock_ret, stock_size, by_month_stocks, j, k, skip=cfg.MOM_SKIP_MONTH
    )

    out_rows = []
    for m in months:
        out_rows.append(
            {
                "Trdmnt": m,
                "UMD": umd.get(m),
                "winner_ret": wret.get(m),
                "loser_ret": lret.get(m),
                "J": j,
                "K": k,
                "skip": cfg.MOM_SKIP_MONTH,
            }
        )

    out_file = cfg.OUTPUT_DIR / "umd_factor_monthly.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    rationale = cfg.OUTPUT_DIR / "momentum_selection_rationale.md"
    lines = [
        "## Momentum Strategy Protocol (Jegadeesh-Titman style)",
        "",
        "### Candidate strategies considered:",
        "- " + ", ".join(f"{a}/{b}" for a, b in cfg.MOM_STRATEGIES),
        "",
        "### Grid evidence (reported, not optimized):",
    ]
    top3 = sorted(
        rows,
        key=lambda r: (-(to_float(r["nw12_tstat"]) or -999), -(to_float(r["mean_umd_pct"]) or -999)),
    )[:3]
    for i, r in enumerate(top3, start=1):
        lines.append(
            f"{i}. {r['strategy']} - t={to_float(r['nw12_tstat']):.3f}, Sharpe={to_float(r['sharpe']):.3f}"
        )
    lines += [
        "",
        "### Robustness principle:",
        "- Following Jegadeesh-Titman style practice, momentum is evaluated on a standard J/K grid and interpreted by the pattern across strategies.",
        "- We do not claim a uniquely optimal in-sample strategy from this table.",
        "",
        f"### Benchmark strategy used for FF4: {benchmark_key}",
        "",
        "### Rationale:",
        "- We report the full J/K grid and emphasize robustness across specifications.",
        "- A pre-specified benchmark is used only as an operational input to build a single FF4 factor series.",
        "- For FF4 construction, we use a pre-specified benchmark momentum strategy.",
        "- This separates model evaluation from in-sample strategy tuning.",
        "",
        "### Implementation details for benchmark strategy:",
        f"- Formation period: {j} months",
        f"- Holding period: {k} months",
        f"- Skip month: {cfg.MOM_SKIP_MONTH} (t-1)",
        f"- Rebalancing: Monthly with {k} overlapping cohorts",
    ]
    rationale.write_text("\n".join(lines), encoding="utf-8")

    print("Done:", out_file)
    print("Done:", rationale)


if __name__ == "__main__":
    main()
