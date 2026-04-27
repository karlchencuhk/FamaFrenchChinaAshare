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
    best = rows[0]
    j = int(best["J"])
    k = int(best["K"])

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
    top3 = rows[:3]
    lines = [
        "## Optimal Momentum Strategy Selection",
        "",
        "### Candidate strategies considered:",
        "- " + ", ".join(r["strategy"] for r in rows),
        "",
        "### Top 3 performing strategies:",
    ]
    for i, r in enumerate(top3, start=1):
        lines.append(
            f"{i}. {r['strategy']} - t={to_float(r['nw12_tstat']):.3f}, Sharpe={to_float(r['sharpe']):.3f}"
        )
    lines += [
        "",
        f"### Selected strategy: {best['strategy']}",
        "",
        "### Rationale:",
        "- Selected by best composite ranking using Sharpe, t-stat, mean return, and drawdown.",
        "- Uses monthly overlapping portfolio implementation to reduce horizon mismatch.",
        "- China A-share momentum appears strongest under this formation/holding pair in-sample.",
        "",
        "### Implementation details for selected strategy:",
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
