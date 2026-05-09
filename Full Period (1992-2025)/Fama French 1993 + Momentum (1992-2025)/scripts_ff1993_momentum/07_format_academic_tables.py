import csv
import importlib.util
from pathlib import Path

from momentum_utils import (
    compute_momentum_scores,
    equal_weighted_return,
    load_stock_panel,
    mean,
    pick_winners_losers,
)

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def f3(x):
    return "" if x in (None, "") else f"{float(x):.3f}"


def f4(x):
    return "" if x in (None, "") else f"{float(x):.4f}"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_table(headers, rows):
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def table_momentum_opt():
    rows = read_csv(cfg.OUTPUT_DIR / "momentum_optimization.csv")
    headers = ["Strategy", "Mean UMD (%)", "t-stat", "Sharpe", "Positive %", "Max DD (%)", "Winner (%)", "Loser (%)"]
    body = []
    for r in rows:
        body.append(
            [
                r["strategy"],
                f3(r["mean_umd_pct"]),
                f3(r["nw12_tstat"]),
                f3(r["sharpe"]),
                f3(r["positive_months_pct"]),
                f3(r["max_drawdown_pct"]),
                f3(r["avg_winner_return_pct"]),
                f3(r["avg_loser_return_pct"]),
            ]
        )
    return (
        "## Table M1 (Momentum): Strategy Grid Evidence\n"
        + md_table(headers, body)
        + "\n\nNote: Consistent with Jegadeesh-Titman style reporting, the J/K grid is presented for robustness across specifications."
    )


def table_factor_summary():
    rows = read_csv(cfg.OUTPUT_DIR / "ff4_factor_summary.csv")
    corr = read_csv(cfg.OUTPUT_DIR / "ff4_factor_correlation.csv")
    h1 = ["Factor", "Mean (%)", "Std (%)", "t-stat", "Sharpe", "Min (%)", "Max (%)", "% Positive"]
    b1 = [[r["factor"], f3(r["mean_pct"]), f3(r["std_pct"]), f3(r["nw12_tstat"]), f3(r["sharpe"]), f3(r["min_pct"]), f3(r["max_pct"]), f3(r["positive_pct"])] for r in rows]

    h2 = ["Factor", "MKT_RF", "SMB", "HML", "UMD"]
    b2 = [[r["row_factor"], f3(r["MKT_RF"]), f3(r["SMB"]), f3(r["HML"]), f3(r["UMD"])] for r in corr]
    return (
        "## Table 2 (FF4-aligned): Factor Summary Including Momentum\n"
        + md_table(h1, b1)
        + "\n\n## Table 2 (FF4-aligned): Factor Correlation Matrix\n"
        + md_table(h2, b2)
    )


def table_robustness_variants():
    rows = read_csv(cfg.OUTPUT_DIR / "momentum_robustness_variants.csv")
    headers = [
        "Construction", "Weighting", "Breakpoints", "J/K", "Mean UMD (%)", "t-stat", "Sharpe", "Positive %", "Max DD (%)"
    ]
    body = []
    for r in rows:
        body.append(
            [
                r["construction"],
                r["weighting"],
                r["momentum_breakpoints"],
                f'{r["J"]}/{r["K"]}',
                f3(r["mean_umd_pct"]),
                f3(r["nw12_tstat"]),
                f3(r["sharpe"]),
                f3(r["positive_months_pct"]),
                f3(r["max_drawdown_pct"]),
            ]
        )
    return (
        "## Table M3 (Momentum): Construction and Robustness Variants\n"
        + md_table(headers, body)
        + "\n\nNote: Variants include requested side-by-side checks for 2x3 vs decile WML, value- vs equal-weighting, 30/70 vs 20/80 momentum breakpoints, and benchmark horizons 12/1 and 12/3."
        + f"\n\nSelected operational variant for FF4 in this run: carhart_2x3, value_weighted, 30/70 breakpoints, J/K={cfg.MOM_BENCHMARK_J}/{cfg.MOM_BENCHMARK_K}."
    )


def table_event_time_performance():
    # JT-style event-time performance profile: average Buy-Sell return at t=1..36 after formation.
    horizon = 36
    j = int(cfg.MOM_BENCHMARK_J)
    skip = int(cfg.MOM_SKIP_MONTH)

    stock_ret, _, _, by_month_stocks = load_stock_panel()
    formation_months = cfg.all_months(cfg.RETURN_START, cfg.RETURN_END)
    event_buckets = {t: [] for t in range(1, horizon + 1)}

    for f_m in formation_months:
        scores = compute_momentum_scores(stock_ret, by_month_stocks, f_m, j, skip)
        winners, losers = pick_winners_losers(scores, deciles=cfg.MOM_DECILES)
        if not winners or not losers:
            continue
        f_i = cfg.month_to_int(f_m)
        for t in range(1, horizon + 1):
            m_t = cfg.int_to_month(f_i + t)
            if cfg.month_to_int(m_t) > cfg.month_to_int(cfg.RETURN_END):
                continue
            wr = equal_weighted_return(winners, m_t, stock_ret)
            lr = equal_weighted_return(losers, m_t, stock_ret)
            if wr is None or lr is None:
                continue
            event_buckets[t].append(wr - lr)

    avg_by_t = {t: mean(event_buckets[t]) for t in range(1, horizon + 1)}
    cum = 1.0
    body = []
    for t in range(1, horizon + 1):
        r = avg_by_t[t]
        if r is None:
            monthly = ""
            cumulative = ""
        else:
            cum *= (1.0 + r)
            monthly = f3(r * 100.0)
            cumulative = f3((cum - 1.0) * 100.0)
        body.append([str(t), monthly, cumulative])

    return (
        "## Table M2 (Momentum): Performance of Relative Strength Portfolios in Event Time\n"
        + md_table(["Month (t)", "Monthly Return (%)", "Cumulative Return (%)"], body)
        + "\n\nNote: Event-time returns are equal-weighted Buy-Sell decile spreads formed with J=12 and skip=1; t=1..36 months after formation."
    )


def table_regressions():
    rows = read_csv(cfg.OUTPUT_DIR / "table_25port_ff4_regressions.csv")
    grid = {(int(r["size_quintile"]), int(r["bm_quintile"])): r for r in rows}
    hdr = ["Size\\BM"] + [f"BM{j}" for j in range(1, 6)]

    def panel(field, formatter):
        body = []
        for i in range(1, 6):
            body.append([f"S{i}"] + [formatter(grid[(i, j)].get(field, "")) for j in range(1, 6)])
        return md_table(hdr, body)

    txt = []
    txt.append("## Table 6a (FF4-aligned): Stock Regressions on MKT_RF, SMB, HML, UMD")
    txt.append("")
    txt.append("#### Panel A: FF3 Alpha (%)")
    txt.append(panel("alpha_ff3_pct", f3))
    txt.append("")
    txt.append("#### Panel B: t-statistic for FF3 Alpha")
    txt.append(panel("t_alpha_ff3", f3))
    txt.append("")
    txt.append("#### Panel C: FF4 Alpha (%)")
    txt.append(panel("alpha_ff4_pct", f3))
    txt.append("")
    txt.append("#### Panel D: t-statistic for FF4 Alpha")
    txt.append(panel("t_alpha_ff4", f3))
    txt.append("")
    txt.append("#### Panel E: UMD Loading (u_umd)")
    txt.append(panel("beta_umd", f4))
    txt.append("")
    txt.append("#### Panel F: t-statistic for UMD Loading")
    txt.append(panel("t_beta_umd", f3))
    txt.append("")
    txt.append("#### Panel G: R-squared (FF3)")
    txt.append(panel("r2_ff3", f3))
    txt.append("")
    txt.append("#### Panel H: R-squared (FF4)")
    txt.append(panel("r2_ff4", f3))
    return "\n".join(txt)


def table_model_compare():
    rows = read_csv(cfg.OUTPUT_DIR / "table_alpha_comparison.csv")
    headers = ["Metric", "FF3", "FF4", "Improvement"]
    body = [[r["metric"], f3(r["ff3"]), f3(r["ff4"]), f3(r["improvement"])] for r in rows]
    return "## Table 9c (FF4-aligned): Alpha Diagnostics Comparison (FF3 vs FF4)\n" + md_table(headers, body)


def make_tex_from_md(md_text):
    lines = [
        "% Auto-generated momentum tables",
        "\\section*{Fama-French 1993 + Momentum (1992-2025)}",
    ]
    for raw in md_text.splitlines():
        line = raw.replace("_", "\\_").replace("%", "\\%")
        if line.startswith("## "):
            lines.append("\\subsection*{" + line[3:] + "}")
        elif line.startswith("### "):
            lines.append("\\paragraph{" + line[4:] + "}")
        elif line.startswith("| "):
            lines.append("\\texttt{" + line + "}\\\\")
        else:
            lines.append(line)
    return "\n".join(lines)


def main():
    sections = [
        "# FF4-Aligned Tables (Full Period, Stock-side focus)",
        "",
        table_momentum_opt(),
        "",
        table_event_time_performance(),
        "",
        table_robustness_variants(),
        "",
        table_factor_summary(),
        "",
        table_regressions(),
        "",
        table_model_compare(),
        "",
    ]
    md = "\n".join(sections)
    md_out = cfg.OUTPUT_DIR / "academic_tables_momentum.md"
    tex_out = cfg.OUTPUT_DIR / "academic_tables_momentum.tex"
    md_out.write_text(md, encoding="utf-8")
    tex_out.write_text(make_tex_from_md(md), encoding="utf-8")
    print("Done:", md_out)
    print("Done:", tex_out)


if __name__ == "__main__":
    main()
