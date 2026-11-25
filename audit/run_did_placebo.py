"""I/O adapter: load NYC open-data caches, run the pre-registered DiD placebo test, print results.
Usage: python3 -m audit.run_did_placebo [data_dir]"""
import gzip
import json
import math
import sys
from collections import Counter, defaultdict

from audit.core import did_outcome, months, verdict, within_slope_perm

BM = {"BROOKLYN": "BK", "BRONX": "BX", "MANHATTAN": "MN", "QUEENS": "QN", "STATEN IS": "SI", "STATEN ISLAND": "SI"}


def load(d):
    org, tot, boro = defaultdict(dict), defaultdict(dict), {}
    for r in json.load(open(f"{d}/dsny-2023-2026.json")):
        cd = str(int(r["borough_id"])) + r["communitydistrict"].zfill(2)
        m = r["month"].replace(" / ", "-")
        f = lambda k: float(r.get(k) or 0)
        org[cd][m] = f("resorganicstons")
        tot[cd][m] = f("refusetonscollected") + f("papertonscollected") + f("mgptonscollected") + f("resorganicstons")
        boro[cd] = r["borough"]
    best, units = {}, Counter()
    for r in json.load(gzip.open(f"{d}/pluto-blk-cd.json.gz")):
        try:
            k, n = (r["borough"], int(r["block"])), int(r["n"])
            _ = r["cd"]
        except (KeyError, ValueError, TypeError):
            continue
        if k not in best or n > best[k][1]:
            best[k] = (r["cd"], n)
        try:
            units[r["cd"]] += float(r.get("u") or 0)
        except ValueError:
            pass
    vio = Counter()
    for r in json.load(open(f"{d}/oath-organic-blk-month-2024-10_2026-11.json")):
        if not ("2026-04" <= r["m"][:7] <= "2026-09"):
            continue
        try:
            k = (BM.get(r.get("b", "")), int(r.get("blk") or -1))
        except ValueError:
            continue
        cd = best.get(k, (None,))[0]
        if cd:
            vio[cd] += int(r["n"])
    return org, tot, boro, units, vio


def main(d="data"):
    org, tot, boro, units, vio = load(d)
    pre23 = months(2023, 4, 6)
    sample = sorted(c for c in org if units.get(c, 0) > 0 and "2026-09" in org[c]
                    and all(org[c].get(m, 0) > 0 for m in pre23))
    x = {c: 1000 * vio[c] / units[c] for c in sample}
    ratio = {c: {m: (org[c].get(m, 0) / tot[c][m]) if tot[c].get(m) else 0 for m in tot[c]} for c in sample}
    print(f"sample: {len(sample)} districts {sample}")
    print("by borough:", dict(Counter(boro[c] for c in sample)))

    def run(label, series, y0, m0, n):
        w = {yr: months(yr, m0, n) for yr in (2023, 2024, 2025, 2026)}
        y = {c: did_outcome(series[c], w[2023], w[2024], w[2025], w[2026]) for c in sample}
        keep = {c: boro[c] for c in sample if y[c] is not None}
        b, p = within_slope_perm(keep, x, y)
        print(f"{label}: n {len(keep)} · beta_DiD {100*(math.exp(b)-1):+.2f}% per 1 violation/1,000 units · p {p:.4f}")
        return b, p

    def comp(label, series, a, b_):
        from audit.core import log_change
        y = {c: log_change(series[c], a, b_) for c in sample}
        keep = {c: boro[c] for c in sample if y[c] is not None}
        b, p = within_slope_perm(keep, x, y)
        print(f"  component {label}: beta {100*(math.exp(b)-1):+.2f}% · p {p:.4f}")

    b_main, p_main = run("MAIN  tons Apr-Sep", org, 2023, 4, 6)
    b_noapr, p_noapr = run("NO-APR tons May-Sep", org, 2023, 5, 5)
    run("ALT   organics share Apr-Sep", ratio, 2023, 4, 6)
    comp("post 2025->2026 Apr-Sep", org, months(2025, 4, 6), months(2026, 4, 6))
    comp("pre  2023->2024 Apr-Sep", org, months(2023, 4, 6), months(2024, 4, 6))
    comp("mid  2024->2025 Apr-Sep (info)", org, months(2024, 4, 6), months(2025, 4, 6))
    print("VERDICT:", verdict(b_main, p_main, b_noapr))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
