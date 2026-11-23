"""Midpoint (Shapley) shift-share decomposition of a participation rate.

Works on any population split into groups (age bands, age x sex, regions...).
For each group g between periods 0 and 1:

    S_g = population_g / total population      (group share)
    P_g = labour force_g / population_g        (group participation rate)

    aging (composition) effect    = (S1 - S0) * (P0 + P1) / 2
    participation (rate) effect   = (P1 - P0) * (S0 + S1) / 2

Summed over groups, the two effects add up exactly to the change in the
aggregate rate (no interaction term), provided the groups cover the total.
"""
from __future__ import annotations

import pandas as pd


def shift_share(pop0: pd.Series, lf0: pd.Series, pop1: pd.Series, lf1: pd.Series,
                total_pop0: float | None = None, total_pop1: float | None = None,
                scale: float = 100.0) -> pd.DataFrame:
    """Decompose the change in an aggregate participation rate between two periods.

    Parameters
    ----------
    pop0, lf0 : population and labour force by group in period 0 (same index).
    pop1, lf1 : the same for period 1.
    total_pop0, total_pop1 : aggregate population. Defaults to the sum over groups.
        Pass the published total if your groups are rounded or incomplete.
    scale : 100 returns percentage points; 1 returns fractions.

    Returns
    -------
    DataFrame indexed by group with columns
    share0, share1, rate0, rate1, aging, participation, total.
    """
    total_pop0 = pop0.sum() if total_pop0 is None else total_pop0
    total_pop1 = pop1.sum() if total_pop1 is None else total_pop1
    s0, s1 = pop0 / total_pop0, pop1 / total_pop1
    p0, p1 = lf0 / pop0, lf1 / pop1
    out = pd.DataFrame({
        "share0": s0, "share1": s1, "rate0": p0, "rate1": p1,
        "aging": scale * (s1 - s0) * (p0 + p1) / 2,
        "participation": scale * (p1 - p0) * (s0 + s1) / 2,
    })
    out["total"] = out["aging"] + out["participation"]
    return out


def chained(pop: pd.DataFrame, lf: pd.DataFrame, total_pop: pd.Series | None = None,
            scale: float = 100.0) -> pd.DataFrame:
    """Chain the decomposition across consecutive periods.

    pop, lf : DataFrames with one row per period (in order) and one column per group.
    total_pop : optional aggregate population per period.

    Returns a long DataFrame (period, group, aging, participation, total), one row
    per group for each step from the previous period. Sum over any span of
    periods to get that span's cumulative effects.
    """
    rows = []
    periods = list(pop.index)
    for a, b in zip(periods[:-1], periods[1:]):
        res = shift_share(pop.loc[a], lf.loc[a], pop.loc[b], lf.loc[b],
                          None if total_pop is None else total_pop.loc[a],
                          None if total_pop is None else total_pop.loc[b], scale)
        res = res[["aging", "participation", "total"]].copy()
        res.insert(0, "period", b)
        rows.append(res.rename_axis("group").reset_index())
    return pd.concat(rows, ignore_index=True)
