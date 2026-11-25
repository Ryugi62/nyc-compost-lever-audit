"""Pure estimation functions (no I/O). Ubiquitous language: district, intensity, outcome, placebo, DiD."""
import math
import random
from collections import defaultdict


def months(y1, m1, n):
    out, y, m = [], y1, m1
    for _ in range(n):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def log_change(series, before, after):
    """ln(mean(after)) - ln(mean(before)); None if either mean is not positive."""
    a = sum(series.get(m, 0.0) for m in before) / len(before)
    b = sum(series.get(m, 0.0) for m in after) / len(after)
    return math.log(b / a) if a > 0 and b > 0 else None


def did_outcome(series, pre_before, pre_after, post_before, post_after):
    """(post change) - (pre-trend change)."""
    post = log_change(series, post_before, post_after)
    pre = log_change(series, pre_before, pre_after)
    return None if post is None or pre is None else post - pre


def center_within(groups, values):
    byg = defaultdict(list)
    for k, g in groups.items():
        byg[g].append(k)
    return {k: values[k] - sum(values[j] for j in byg[groups[k]]) / len(byg[groups[k]]) for k in groups}


def slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    if sxx == 0:
        raise ValueError("no variation in x")
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx


def within_slope_perm(groups, x, y, n_perm=10000, seed=20261126):
    """Slope of within-group-centered y on x; two-sided permutation p shuffling x inside groups."""
    keys = sorted(groups)
    g = {k: groups[k] for k in keys}
    xc, yc = center_within(g, {k: x[k] for k in keys}), center_within(g, {k: y[k] for k in keys})
    b = slope([xc[k] for k in keys], [yc[k] for k in keys])
    rnd = random.Random(seed)
    byg = defaultdict(list)
    for k in keys:
        byg[g[k]].append(k)
    hits = 0
    for _ in range(n_perm):
        perm = {}
        for grp in sorted(byg):
            members = byg[grp]
            vals = [xc[k] for k in members]
            rnd.shuffle(vals)
            perm.update(zip(members, vals))
        if abs(slope([perm[k] for k in keys], [yc[k] for k in keys])) >= abs(b) - 1e-12:
            hits += 1
    return b, hits / n_perm


def verdict(beta_main, p_main, beta_no_april):
    """Pre-registered decision line (prereg/2026-11-26-did-placebo.md)."""
    if beta_main > 0 and p_main < 0.05 and beta_no_april > 0:
        return "PASS"
    if beta_main > 0:
        return "WEAK"
    return "NULL_OR_NEGATIVE"
