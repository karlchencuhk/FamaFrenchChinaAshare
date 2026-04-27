import csv
import importlib.util
from pathlib import Path

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
    return "## Table 1. Momentum Strategy Optimization\n" + md_table(headers, body)


def table_factor_summary():
    rows = read_csv(cfg.OUTPUT_DIR / "ff4_factor_summary.csv")
    corr = read_csv(cfg.OUTPUT_DIR / "ff4_factor_correlation.csv")
    h1 = ["Factor", "Mean (%)", "Std (%)", "t-stat", "Sharpe", "Min (%)", "Max (%)", "% Positive"]
    b1 = [[r["factor"], f3(r["mean_pct"]), f3(r["std_pct"]), f3(r["nw12_tstat"]), f3(r["sharpe"]), f3(r["min_pct"]), f3(r["max_pct"]), f3(r["positive_pct"])] for r in rows]

    h2 = ["Factor", "MKT_RF", "SMB", "HML", "UMD"]
    b2 = [[r["row_factor"], f3(r["MKT_RF"]), f3(r["SMB"]), f3(r["HML"]), f3(r["UMD"])] for r in corr]
    return (
        "## Table 2. Factor Summary Including Momentum\n"
        + "### Panel A: Summary Statistics\n"
        + md_table(h1, b1)
        + "\n\n### Panel B: Correlation Matrix\n"
        + md_table(h2, b2)
    )


def table_regressions():
    rows = read_csv(cfg.OUTPUT_DIR / "table_25port_ff4_regressions.csv")
    headers = ["Size", "BM", "alpha_FF3 (%)", "t(alpha_FF3)", "alpha_FF4 (%)", "t(alpha_FF4)", "beta_UMD", "t(beta_UMD)", "R2_FF3", "R2_FF4"]
    body = []
    for r in rows:
        body.append(
            [
                str(r["size_quintile"]),
                str(r["bm_quintile"]),
                f3(r["alpha_ff3_pct"]),
                f3(r["t_alpha_ff3"]),
                f3(r["alpha_ff4_pct"]),
                f3(r["t_alpha_ff4"]),
                f4(r["beta_umd"]),
                f3(r["t_beta_umd"]),
                f3(r["r2_ff3"]),
                f3(r["r2_ff4"]),
            ]
        )
    return "## Table 3. FF4 Regressions on 25 Size-BM Portfolios\n" + md_table(headers, body)


def table_model_compare():
    rows = read_csv(cfg.OUTPUT_DIR / "table_alpha_comparison.csv")
    headers = ["Metric", "FF3", "FF4", "Improvement"]
    body = [[r["metric"], f3(r["ff3"]), f3(r["ff4"]), f3(r["improvement"])] for r in rows]
    return "## Table 4. Model Comparison: FF3 vs FF4\n" + md_table(headers, body)


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
        "# Fama-French 1993 + Momentum (Carhart-style FF4) Tables",
        "",
        table_momentum_opt(),
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
