import csv
import importlib.util
from pathlib import Path

from momentum_utils import mean

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, "") else None


def rmse(xs):
    vals = [x for x in xs if x is not None]
    if not vals:
        return None
    return (sum(v * v for v in vals) / len(vals)) ** 0.5


def main():
    file = cfg.OUTPUT_DIR / "table_25port_ff4_regressions.csv"
    with open(file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    a3 = [to_float(r["alpha_ff3_pct"]) for r in rows]
    a4 = [to_float(r["alpha_ff4_pct"]) for r in rows]
    t3 = [to_float(r["t_alpha_ff3"]) for r in rows]
    t4 = [to_float(r["t_alpha_ff4"]) for r in rows]
    r23 = [to_float(r["r2_ff3"]) for r in rows]
    r24 = [to_float(r["r2_ff4"]) for r in rows]

    out = [
        {"metric": "mean_absolute_alpha_pct", "ff3": mean([abs(x) for x in a3]), "ff4": mean([abs(x) for x in a4])},
        {"metric": "rmse_alpha_pct", "ff3": rmse(a3), "ff4": rmse(a4)},
        {"metric": "n_significant_5pct", "ff3": sum(1 for t in t3 if t is not None and abs(t) >= 1.96), "ff4": sum(1 for t in t4 if t is not None and abs(t) >= 1.96)},
        {"metric": "n_significant_1pct", "ff3": sum(1 for t in t3 if t is not None and abs(t) >= 2.576), "ff4": sum(1 for t in t4 if t is not None and abs(t) >= 2.576)},
        {"metric": "mean_r2", "ff3": mean(r23), "ff4": mean(r24)},
    ]
    for r in out:
        f3 = to_float(r["ff3"])
        f4 = to_float(r["ff4"])
        r["improvement"] = (f4 - f3) if (f3 is not None and f4 is not None) else None

    out_file = cfg.OUTPUT_DIR / "table_alpha_comparison.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "ff3", "ff4", "improvement"])
        w.writeheader()
        w.writerows(out)
    alias_file = cfg.OUTPUT_DIR / "table_5_alpha_diagnostics_comparison.csv"
    with open(alias_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "ff3", "ff4", "improvement"])
        w.writeheader()
        w.writerows(out)
    print("Done:", out_file)
    print("Done:", alias_file)


if __name__ == "__main__":
    main()
