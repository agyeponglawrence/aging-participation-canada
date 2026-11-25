# How much of the fall in participation is aging?

This is the replication package for my article **"Canada's aging drag is back, and nothing is offsetting it"** (November 2026).

The analysis splits the change in Canada's labour force participation rate since 2011 into two parts:

- **Aging effect:** more of the population is in older age groups, where fewer people work.
- **Participation effect:** people within each age group are working, or looking for work, more or less than before.

**Main result:** aging took 4.1 percentage points off the participation rate between 2011 and 2026. Rising participation, mostly among older women, gave back 2.2 points. Since 2024 that offset has stopped.

---

## Start here

Pick the route that suits you. You don't need all three.

| I want to… | Go to |
|---|---|
| Understand the method | [METHOD.md](METHOD.md): the formula, data, checks and caveats on one page |
| Check the numbers in Excel | [`excel/Aging_LFP_shift_share_Canada.xlsx`](excel/). Start with the **ReadMe** and **Summary** tabs. |
| Rerun it, or run it for a province | The Python steps below |

---

## Run it in Python

You need Python 3.10 or later.

**1. Get the files.** On this page, click **Code → Download ZIP** and unzip it, or run:

```bash
git clone https://github.com/agyeponglawrence/aging-participation-canada
cd aging-participation-canada
```

**2. Install the packages** (once):

```bash
pip install -r requirements.txt
```

**3. Run the analysis for Canada:**

```bash
python analysis/run.py
```

The results appear in `output/canada/`: three CSV tables and three charts. The first table, `summary.csv`, has the headline numbers.

### Run it for a province

The repository only includes data for Canada. For a province, download the full Statistics Canada table once (about 55 MB, 750 MB unzipped), then name the province:

```bash
python analysis/download_data.py
python analysis/run.py --geo Saskatchewan --data data/raw/14100017.csv
```

Results go to `output/saskatchewan/`. Use the province name exactly as Statistics Canada spells it, in quotes if it has spaces: `"British Columbia"`, `"Newfoundland and Labrador"`, `"Prince Edward Island"`.

To start from a different year, add `--start`, for example `--start 2015`.

If the download fails (Statistics Canada's site is sometimes down for maintenance), get the table by hand from the [table page](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701): choose **Download options → Download entire table**, unzip it, and put `14100017.csv` in `data/raw/`.

---

## What's in the folder

| Folder or file | What it is |
|---|---|
| `METHOD.md` | The method, data notes, checks and caveats |
| `DECISIONS.md` | Why I made each choice (base year, weights, age groups) and what I considered instead |
| `excel/` | `Aging_LFP_shift_share_Canada.xlsx`: the full analysis with live formulas, so every number traces back to a Statistics Canada row. `original_working_file.xlsx`: the working file I first built the analysis in (pivot tables, age groups only). |
| `analysis/` | The Python scripts. `run.py` is the only one most people need. |
| `shiftshare/` | The decomposition itself, written so it works on any data (see below) |
| `data/raw/` | The Statistics Canada data for Canada |
| `output/canada/` | Results for Canada: tables and charts |

The charts here are deliberately plain. The ones in the article are styled differently but show the same numbers.

---

## Use the method on other data

The decomposition in `shiftshare/` doesn't know anything about Canada. Give it population and labour force by group for two periods and it returns the two effects. Run this from the repository folder:

```python
import pandas as pd
from shiftshare import shift_share

# made-up numbers: population and labour force by group, in two periods
pop0 = pd.Series({"15-24": 4.5, "25-54": 14.8, "55+": 11.9})
lf0  = pd.Series({"15-24": 2.9, "25-54": 12.8, "55+": 4.4})
pop1 = pd.Series({"15-24": 4.6, "25-54": 15.6, "55+": 13.6})
lf1  = pd.Series({"15-24": 2.8, "25-54": 13.6, "55+": 5.0})

result = shift_share(pop0, lf0, pop1, lf1)
print(result[["aging", "participation"]].sum())   # percentage points
```

---

## Data, licence and citation

- **Data:** Statistics Canada, [Table 14-10-0017-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701), monthly, not seasonally adjusted. Used under the [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence).
- **Code:** MIT licence (see `LICENSE`). You're free to reuse and adapt it with credit.
- **Cite as:** Agyepong, L. (2026). *Canada's aging drag is back, and nothing is offsetting it*. Replication package. https://github.com/agyeponglawrence/aging-participation-canada

Found an error or have a question? [Open an issue](https://github.com/agyeponglawrence/aging-participation-canada/issues).
