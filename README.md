# How much of the fall in participation is aging?

A replication package for **"Nothing pushing back: the full weight of aging returns to Canada's labour market"** by Lawrence Agyepong (November 2026).

The analysis splits the change in the labour force participation rate into two parts:

- an **aging effect**: the population shifting into older age groups, where fewer people work
- a **participation effect**: participation rising or falling within each age group

It works for Canada or any province, from any base year.

## Headline results (Canada, 2011 to January–October 2026)

| Measure | Percentage points |
|---|---|
| Actual change in the participation rate (66.8% → 64.9%) | −1.92 |
| Aging effect | −4.11 |
| Participation effect | +2.20 |
| … of which women, all ages | +1.62 |
| … of which women 55 and over | +1.07 |
| … of which men 55 and over | +0.72 |

Since 2024 the participation effect has been at or below zero (−0.35 in 2024, −0.03 in 2025, −0.01 in 2026 so far), while the aging effect has come back to −0.36 in 2026. The full year-by-year numbers are in `output/canada/annual_contributions.csv`.

## Quick start

```bash
pip install -r requirements.txt
python analysis/run.py                 # Canada, base year 2011, using the bundled data
```

Tables and charts are written to `output/canada/`.

### Run it for a province

The bundled data covers Canada only. For a province, download the full table once, then pass the province name:

```bash
python analysis/download_data.py       # saves data/raw/14100017.csv (large; git-ignored)
python analysis/run.py --geo Saskatchewan --data data/raw/14100017.csv
python analysis/run.py --geo "British Columbia" --start 2015 --data data/raw/14100017.csv
```

Use the province name exactly as Statistics Canada spells it (for example `"Newfoundland and Labrador"`). The script stops with a clear message if a series is missing or suppressed, which can happen for the smallest provinces.

### Use the method on your own data

The decomposition itself is in `shiftshare/`. It doesn't know anything about Canada, so you can use it for any population split into groups (age, sex, region, education):

```python
import pandas as pd
from shiftshare import shift_share

pop0 = pd.Series({"15-24": 4.5, "25-54": 14.8, "55+": 11.9})   # population, period 0
lf0  = pd.Series({"15-24": 2.9, "25-54": 12.8, "55+": 4.4})    # labour force, period 0
pop1 = pd.Series({"15-24": 4.6, "25-54": 15.6, "55+": 13.6})
lf1  = pd.Series({"15-24": 2.8, "25-54": 13.6, "55+": 5.0})

res = shift_share(pop0, lf0, pop1, lf1)   # columns: aging, participation, total (pp)
print(res[["aging", "participation"]].sum())
```

`chained()` runs the same thing over a sequence of periods. These numbers are made up for illustration.

## What's in the repo

```
README.md                   this file
METHOD.md                   one-page method card: formula, choices, checks, when not to use it
DECISIONS.md                the judgment calls behind the analysis, and alternatives rejected
shiftshare/                 the reusable decomposition (no Canada-specific code)
analysis/
    run.py                  command-line entry point: tables + charts for any geography
    lfp.py                  loads Table 14-10-0017-01 and chains the decomposition
    download_data.py        fetches the full table (all provinces) from Statistics Canada
    build_workbook.py       rebuilds the Canada Excel workbook with live formulas
data/raw/                   Canada extract of Table 14-10-0017-01 (see data/README.md)
output/canada/              results for Canada: CSV tables, charts, Excel workbook
```

The **Excel workbook** (`output/canada/Aging_LFP_shift_share_Canada.xlsx`) does the same decomposition with live formulas, so you can trace every number back to a Statistics Canada row without writing code. It covers Canada only. The Python version produces the same results.

The charts in this repo are deliberately plain. The published versions in the article are styled differently, but they show the same numbers.

## Requirements

Python 3.10 or later, with pandas, numpy, matplotlib and openpyxl (see `requirements.txt`).

## Data and licence

- Data: Statistics Canada, [Table 14-10-0017-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701), Labour force characteristics by gender and detailed age group, monthly, unadjusted for seasonality. Reproduced and distributed on an "as is" basis with the permission of Statistics Canada, under the [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence).
- Code: MIT licence (see `LICENSE`).

## Citation

Agyepong, L. (2026). *Nothing pushing back: the full weight of aging returns to Canada's labour market*. Replication package, https://github.com/agyeponglawrence/aging-participation-canada

Questions or errors: open an issue.
