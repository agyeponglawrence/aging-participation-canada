"""Load LFS Table 14-10-0017-01 for one geography and run the chained decomposition.

Used by run.py. Kept separate so you can import it in a notebook:

    from analysis.lfp import load, decompose
    monthly = load("data/raw/14100017.csv", geo="Alberta")
    result = decompose(monthly, start=2011)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shiftshare import shift_share  # noqa: E402

BANDS = ['15 to 19 years', '20 to 24 years', '25 to 29 years', '30 to 34 years', '35 to 39 years',
         '40 to 44 years', '45 to 49 years', '50 to 54 years', '55 to 59 years', '60 to 64 years',
         '65 to 69 years', '70 years and over']
SHORT = dict(zip(BANDS, ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54',
                         '55-59', '60-64', '65-69', '70+']))
ALL = '15 years and over'
TOTAL = 'Total - Gender'
SEXES = {'Men+': 'Men', 'Women+': 'Women'}


def load(path, geo: str = "Canada") -> pd.DataFrame:
    """Monthly population and labour force (thousands) for one GEO, wide by (measure, gender, age)."""
    d = pd.read_csv(path, low_memory=False, encoding="utf-8-sig",
                    usecols=['REF_DATE', 'GEO', 'Labour force characteristics', 'Gender', 'Age group', 'VALUE'])
    geos = sorted(d['GEO'].dropna().unique())
    if geo not in geos:
        raise SystemExit(f"GEO '{geo}' not in {path}. Available: {', '.join(geos)}\n"
                         "The bundled file covers Canada only; run analysis/download_data.py for provinces.")
    d = d[(d['GEO'] == geo) & d['Labour force characteristics'].isin(['Population', 'Labour force'])
          & d['Gender'].isin([TOTAL, *SEXES]) & d['Age group'].isin([ALL, *BANDS])]
    p = d.pivot_table(index='REF_DATE', columns=['Labour force characteristics', 'Gender', 'Age group'],
                      values='VALUE')
    need = [(m, g, b) for m in ['Population', 'Labour force'] for g in [TOTAL, *SEXES] for b in BANDS]
    missing = [c for c in need if c not in p.columns or p[c].isna().any()]
    if missing:
        raise SystemExit(f"{len(missing)} series are missing or suppressed for {geo}, e.g. {missing[:3]}.\n"
                         "Small provinces can have suppressed cells; try a larger geography.")
    p.index = pd.PeriodIndex(p.index, freq='M')
    return p


@dataclass
class Result:
    geo: str
    annual: pd.DataFrame        # one row per step: aging, participation, actual_change
    by_group: pd.DataFrame      # cumulative effects by sex x age over the whole span
    start_rate: float
    end_rate: float
    last_label: str             # e.g. "2026 YTD (Jan-Oct)" or "2025"


def _rate(x):
    return 100 * x[('Labour force', TOTAL, ALL)] / x[('Population', TOTAL, ALL)]


def _frame(x, genders):
    cells = [(g, b) for g in genders for b in BANDS]
    idx = pd.MultiIndex.from_tuples([(SEXES.get(g, 'Total'), SHORT[b]) for g, b in cells], names=['sex', 'age'])
    return (pd.Series([x[('Population', g, b)] for g, b in cells], index=idx),
            pd.Series([x[('Labour force', g, b)] for g, b in cells], index=idx))


def decompose(monthly: pd.DataFrame, geo: str = "", start: int = 2011) -> Result:
    """Chain the midpoint shift-share year by year from `start`.

    Full calendar years use annual averages. If the latest year is incomplete, its step
    compares the same months with the year before (the detailed data are not seasonally
    adjusted), chained onto the last full year's annual average.
    """
    years = monthly.index.year
    last_year = int(years.max())
    last_month = int(monthly.index[years == last_year].month.max())
    full_last = last_year if last_month == 12 else last_year - 1
    if start >= full_last:
        raise SystemExit(f"start year must be before {full_last}")
    ann = monthly[(years >= start) & (years <= full_last)].groupby(years[(years >= start) & (years <= full_last)]).mean()

    steps = [(str(y + 1), ann.loc[y], ann.loc[y + 1]) for y in range(start, full_last)]
    last_label = str(full_last)
    if last_month < 12:
        mon = monthly.index.month
        ytd = monthly[(mon <= last_month) & (years >= last_year - 1)]
        ytd = ytd.groupby(ytd.index.year).mean()
        months = f"Jan-{pd.Timestamp(2000, last_month, 1):%b}"
        last_label = f"{last_year} YTD ({months})"
        steps.append((last_label, ytd.loc[last_year - 1], ytd.loc[last_year]))

    annual, groups = [], []
    for label, a, b in steps:
        t0, t1 = a[('Population', TOTAL, ALL)], b[('Population', TOTAL, ALL)]
        age = shift_share(*_frame(a, [TOTAL]), *_frame(b, [TOTAL]), t0, t1)
        sex = shift_share(*_frame(a, list(SEXES)), *_frame(b, list(SEXES)), t0, t1)
        actual = _rate(b) - _rate(a)
        # the two effects must add up to the actual change (groups cover the 15+ total)
        tol = 0.02  # published totals are rounded independently of the groups
        assert abs(age['total'].sum() - actual) < tol, (label, age['total'].sum(), actual)
        assert abs(sex['total'].sum() - actual) < tol, (label, sex['total'].sum(), actual)
        annual.append({'step': label, 'aging': age['aging'].sum(),
                       'participation': age['participation'].sum(), 'actual_change': actual})
        groups.append(sex[['aging', 'participation']])

    annual = pd.DataFrame(annual)
    start_rate = _rate(ann.loc[start])
    return Result(geo=geo, annual=annual, by_group=sum(groups).reset_index(),
                  start_rate=start_rate, end_rate=start_rate + annual['actual_change'].sum(),
                  last_label=last_label)
