"""Decompose the change in a participation rate into aging and participation effects.

    python analysis/run.py                                   # Canada, 2011 onward (bundled data)
    python analysis/run.py --geo Saskatchewan --data data/raw/14100017.csv
    python analysis/run.py --geo Ontario --start 2015 --data data/raw/14100017.csv

Writes tables and three plain charts to output/<geo>/:

    summary.csv               headline numbers
    annual_contributions.csv  aging and participation effects for each year
    cumulative_by_group.csv   effects by sex and age group over the whole span
    fig1_waterfall.png        start rate -> aging -> participation by group -> end rate
    fig2_participation_by_group.png
    fig3_annual_contributions.png
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lfp import load, decompose  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "raw" / "statcan_14-10-0017-01_canada.csv"
OLD = ['55-59', '60-64', '65-69', '70+']
CORE = ['25-29', '30-34', '35-39', '40-44', '45-49', '50-54']
YOUTH = ['15-19', '20-24']
SOURCE = "Source: Statistics Canada, Table 14-10-0017-01 (not seasonally adjusted). Midpoint shift-share, chained annually."


def tables(r, out, start):
    g = r.by_group
    part = lambda sex, ages: g.loc[(g.sex == sex) & g.age.isin(ages), 'participation'].sum()
    s = r.annual
    summary = pd.DataFrame([
        (f'Participation rate {start} (%)', r.start_rate),
        (f'Participation rate {r.last_label}, chained (%)', r.end_rate),
        ('Actual change (pp)', s.actual_change.sum()),
        ('Aging effect, cumulative (pp)', s.aging.sum()),
        ('Participation effect, cumulative (pp)', s.participation.sum()),
        ('Participation effect, women, all ages (pp)', g.loc[g.sex == 'Women', 'participation'].sum()),
        ('Participation effect, men, all ages (pp)', g.loc[g.sex == 'Men', 'participation'].sum()),
        ('Participation effect, women 55+ (pp)', part('Women', OLD)),
        ('Participation effect, men 55+ (pp)', part('Men', OLD)),
        ('Aging effect, average per year (pp)', s.aging.mean()),
    ], columns=['measure', 'value'])
    summary.round(3).to_csv(out / 'summary.csv', index=False)
    s.round(4).to_csv(out / 'annual_contributions.csv', index=False)
    g.round(4).to_csv(out / 'cumulative_by_group.csv', index=False)
    return summary


def charts(r, out, start):
    g = r.by_group
    part = lambda sexes, ages: g.loc[g.sex.isin(sexes) & g.age.isin(ages), 'participation'].sum()
    span = f"{start} to {r.last_label}"

    # Figure 1: waterfall
    steps = [("Population\naging", g.aging.sum()),
             ("Women 55+", part(['Women'], OLD)), ("Men 55+", part(['Men'], OLD)),
             ("Core age\n25-54", part(['Men', 'Women'], CORE)), ("Youth\n15-24", part(['Men', 'Women'], YOUTH))]
    fig, ax = plt.subplots(figsize=(10, 6))
    level = r.start_rate
    lo = min(r.start_rate, r.end_rate, *(r.start_rate + np.cumsum([v for _, v in steps]))) - 2
    ax.bar(0, level - lo, bottom=lo, color='0.3')
    for k, (lab, v) in enumerate(steps, start=1):
        ax.bar(k, abs(v), bottom=level if v >= 0 else level + v, color='tab:blue' if v >= 0 else 'tab:red')
        ax.text(k, max(level, level + v) + 0.1, f"{v:+.2f}", ha='center', va='bottom')
        level += v
    ax.bar(len(steps) + 1, r.end_rate - lo, bottom=lo, color='0.3')
    ax.text(0, r.start_rate + 0.1, f"{r.start_rate:.1f}%", ha='center', va='bottom')
    ax.text(len(steps) + 1, r.end_rate + 0.1, f"{r.end_rate:.1f}%", ha='center', va='bottom')
    ax.set_xticks(range(len(steps) + 2), [f"{start}"] + [s for s, _ in steps] + [r.last_label.replace(' (', '\n(')])
    ax.set_ylim(lo, max(r.start_rate, r.end_rate) + 1.5)
    ax.set_ylabel("Participation rate, % (axis does not start at zero)")
    ax.set_title(f"{r.geo}: change in the participation rate by source, {span}")
    fig.text(0.01, 0.01, SOURCE, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(out / 'fig1_waterfall.png', dpi=150); plt.close(fig)

    # Figure 2: participation effect by age group and sex
    ages = list(dict.fromkeys(g.age))
    men = g[g.sex == 'Men'].set_index('age').loc[ages, 'participation']
    women = g[g.sex == 'Women'].set_index('age').loc[ages, 'participation']
    y = np.arange(len(ages))[::-1]
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(y + 0.2, women, height=0.4, label='Women')
    ax.barh(y - 0.2, men, height=0.4, label='Men')
    ax.axvline(0, color='k', lw=0.8)
    ax.set_yticks(y, ages); ax.set_xlabel("Percentage points"); ax.legend()
    ax.set_title(f"{r.geo}: participation effect by age group and sex, {span}")
    fig.text(0.01, 0.01, SOURCE, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(out / 'fig2_participation_by_group.png', dpi=150); plt.close(fig)

    # Figure 3: annual contributions
    s = r.annual
    x = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(11, 6))
    a_, p_ = s.aging.to_numpy(), s.participation.to_numpy()
    # stack: when both effects share a sign, the participation bar starts where aging ends
    p_bottom = np.where(np.sign(a_) == np.sign(p_), a_, 0)
    ax.bar(x, a_, label='Population aging', color='0.55')
    ax.bar(x, p_, bottom=p_bottom, label='Participation within groups', color='tab:orange')
    ax.plot(x, s.actual_change, 'k-o', label='Actual change')
    ax.axhline(0, color='k', lw=0.8)
    ax.set_xticks(x, [t.split(' (')[0].replace(' YTD', '\nYTD') for t in s.step])
    ax.set_ylabel("Percentage points"); ax.legend()
    ax.set_title(f"{r.geo}: annual contributions to the change in the participation rate")
    fig.text(0.01, 0.01, SOURCE, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(out / 'fig3_annual_contributions.png', dpi=150); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--geo', default='Canada', help='GEO name exactly as in the StatCan file, e.g. "Saskatchewan"')
    ap.add_argument('--start', type=int, default=2011, help='base year (default 2011)')
    ap.add_argument('--data', default=str(DEFAULT_DATA), help='path to the 14-10-0017-01 CSV')
    ap.add_argument('--no-charts', action='store_true')
    a = ap.parse_args()

    r = decompose(load(a.data, a.geo), geo=a.geo, start=a.start)
    out = ROOT / 'output' / a.geo.lower().replace(' ', '-').replace(',', '')
    out.mkdir(parents=True, exist_ok=True)
    summary = tables(r, out, a.start)
    if not a.no_charts:
        charts(r, out, a.start)
    print(summary.round(2).to_string(index=False))
    print(f"\nWritten to {out.relative_to(ROOT)}/")


if __name__ == '__main__':
    main()
