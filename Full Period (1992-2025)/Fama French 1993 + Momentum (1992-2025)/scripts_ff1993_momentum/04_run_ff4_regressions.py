import csv
import importlib.util
from pathlib import Path

from momentum_utils import ols_with_nw

_cfg_path = Path(__file__).with_name("00_config.py")
_spec = importlib.util.spec_from_file_location("cfg", _cfg_path)
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)


def to_float(x):
    return float(x) if x not in (None, "") else None


def main():
    ff4 = {}
    with open(cfg.OUTPUT_DIR / "ff4_factors_monthly.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ff4[r["Trdmnt"]] = {k: to_float(v) for k, v in r.items() if k != "Trdmnt"}

    by_port = {}
    with open(cfg.BASE_FF3_OUTPUT / "ff3_port25_monthly.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by_port.setdefault(r["portfolio"], []).append(r)

    out_rows = []
    for port, rows in sorted(by_port.items()):
        y_ff3, x1_ff3, x2_ff3, x3_ff3 = [], [], [], []
        y_ff4, x1_ff4, x2_ff4, x3_ff4, x4_ff4 = [], [], [], [], []

        size_q = None
        bm_q = None
        for r in rows:
            m = r["Trdmnt"]
            fr = ff4.get(m)
            if fr is None:
                continue
            ex = to_float(r.get("excess_return"))
            if ex is None:
                continue
            if size_q is None:
                size_q = int(r["size_quintile"])
                bm_q = int(r["bm_quintile"])

            if None not in (fr["MKT_RF"], fr["SMB"], fr["HML"]):
                y_ff3.append(ex)
                x1_ff3.append(fr["MKT_RF"])
                x2_ff3.append(fr["SMB"])
                x3_ff3.append(fr["HML"])

            if None not in (fr["MKT_RF"], fr["SMB"], fr["HML"], fr["UMD"]):
                y_ff4.append(ex)
                x1_ff4.append(fr["MKT_RF"])
                x2_ff4.append(fr["SMB"])
                x3_ff4.append(fr["HML"])
                x4_ff4.append(fr["UMD"])

        r3 = ols_with_nw(y_ff3, [x1_ff3, x2_ff3, x3_ff3], lag=cfg.NW_LAG)
        r4 = ols_with_nw(y_ff4, [x1_ff4, x2_ff4, x3_ff4, x4_ff4], lag=cfg.NW_LAG)
        if r3 is None or r4 is None:
            continue
        out_rows.append(
            {
                "portfolio": port,
                "size_quintile": size_q,
                "bm_quintile": bm_q,
                "alpha_ff3_pct": r3["beta"][0] * 100.0,
                "t_alpha_ff3": r3["t_nw"][0],
                "alpha_ff4_pct": r4["beta"][0] * 100.0,
                "t_alpha_ff4": r4["t_nw"][0],
                "beta_umd": r4["beta"][4],
                "t_beta_umd": r4["t_nw"][4],
                "r2_ff3": r3["r2"],
                "r2_ff4": r4["r2"],
                "beta_mkt_ff4": r4["beta"][1],
                "beta_smb_ff4": r4["beta"][2],
                "beta_hml_ff4": r4["beta"][3],
                "n_ff3": r3["n"],
                "n_ff4": r4["n"],
            }
        )

    out_file = cfg.OUTPUT_DIR / "table_25port_ff4_regressions.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    alias_file = cfg.OUTPUT_DIR / "table_4_25port_ff4_regressions.csv"
    with open(alias_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print("Done:", out_file)
    print("Done:", alias_file)


if __name__ == "__main__":
    main()
