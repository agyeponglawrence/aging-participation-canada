# Method and data

The full method behind **"Nothing pushing back: the full weight of aging returns to Canada's labour market"** (Lawrence Agyepong, November 2026). The article keeps only a short note; the details, checks and caveats are here.

## The question

How much of a change in the overall participation rate comes from the population's **mix** changing (aging), and how much from **behaviour within groups** changing (people in each age group working or looking for work more or less)?

## The decomposition

The overall participation rate is a weighted average of group rates, $P = \sum_g S_g P_g$, where $S_g$ is group $g$'s share of the 15+ population and $P_g$ its participation rate. For each pair of years and each age-sex group:

$$
\Delta P = \underbrace{\sum_g \Delta S_g \, \bar{P}_g}_{\text{aging effect}} + \underbrace{\sum_g \Delta P_g \, \bar{S}_g}_{\text{participation effect}}
$$

The barred terms are averages of the two years (midpoint, or Shapley, weights), so the two terms add up exactly to the change in the overall rate, with no leftover interaction term.

I use 5-year age groups for men and women, compute the split year by year from 2011 and add the years up, so any period can be compared with any other.

## Data

- **Source:** Statistics Canada, [Table 14-10-0017-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701), Labour force characteristics by gender and detailed age group, monthly, not seasonally adjusted. Canada.
- **Groups:** 12 age groups (15–19 to 65–69, plus 70 and over) by sex, 24 cells in all. An age-only version (12 cells) is also reported.
- **Periods:** annual averages for 2011–2025. 2026 compares January–October with January–October 2025, and that change is added to the 2025 annual figure. Same months are compared because the detailed age data isn't seasonally adjusted.
- **Units:** percentage points of the overall participation rate.

## Checks

- **Exactness:** each year, the aging and participation effects add up to the actual change in the rate. The code asserts this.
- **Benchmark:** holding September 2019 age shares fixed, the method gives a September 2026 rate of 66.1%, the same as Statistics Canada's own estimate in its September 2026 release.
- **Age vs age × sex:** the age-only version puts the cumulative aging effect at −4.11 points; the age-by-sex version in Figure 1 gives −4.07, because it also picks up small shifts in the sex mix within age groups.
- **Weights:** base-year weights give aging −4.11 and participation +2.14, with a +0.16 interaction term left over; end-year weights give −3.95 and +2.30. Midpoint weights sit between the two and leave no interaction.
- **Excel vs Python:** the workbook and the code give the same results.

## Caveats

- **An accounting split, not causes.** The decomposition says where the change shows up, not why. Participation within an age group can respond to the age structure itself (scarce young workers can keep older ones on longer), and immigration changes who is in each group.
- **People, not hours.** The participation rate counts people. Older workers tend to work shorter weeks, so the past decade's offset likely added less labour than the headcount suggests.
- **One partial year.** 2026 is ten months of one year: a first clear reading, not yet a trend. The year-to-date step will be revised when the full year is in.
- **Group choice matters.** Finer groups move a little more of the change into the aging effect. A wider top group (65+) would understate aging because participation keeps falling after 70.
- **Revisions.** Statistics Canada revises the Labour Force Survey from time to time (for example when it rebases to new population estimates), so a fresh download may give slightly different numbers.
- **Immigration is not tested directly.** The 2023–24 pause in the aging effect lines up with the immigration surge, but the decomposition doesn't isolate immigration's role.

## When not to use it

- When you need a causal answer (why participation rose), you need a behavioural model or a cohort analysis.
- When the groups don't cover the total, the two effects won't add up to the actual change.
- With small geographies, suppressed or noisy cells can dominate the result. Use wider groups or a longer averaging window.
- With seasonally unadjusted data, never compare different months of the year.

## Replicate it

Everything needed is in this repository: the data, an Excel workbook with live formulas, and Python code that runs for Canada or any province, from any base year. See the [README](README.md) for how to run it, and [DECISIONS.md](DECISIONS.md) for the judgment calls behind each choice.
