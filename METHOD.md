# Method card: midpoint shift-share decomposition of a participation rate

## The question it answers

How much of a change in the overall participation rate comes from the population's **mix** changing (aging), and how much from **behaviour within groups** changing (people in each age group working or looking for work more or less)?

## The formula

The overall rate is a weighted average of group rates: P = Σ S_g P_g, where S_g is group g's share of the 15+ population and P_g its participation rate.

Between two periods:

```
ΔP = Σ_g ΔS_g · (P_g,0 + P_g,1)/2      aging (composition) effect
   + Σ_g ΔP_g · (S_g,0 + S_g,1)/2      participation (rate) effect
```

Weighting each term by the average of the two periods (the midpoint, or Shapley, weights) makes the two effects add up exactly to the actual change, with no leftover interaction term.

## How it's applied here

| Choice | Setting |
|---|---|
| Groups | 12 five-year age groups (15–19 … 65–69, 70+) × 2 sexes = 24 cells. An age-only version (12 cells) is also reported. |
| Period | Annual averages of monthly data, chained year by year from the base year (default 2011) |
| Incomplete latest year | Same months compared with the year before (e.g. Jan–Oct 2026 vs Jan–Oct 2025), chained onto the last full year |
| Data | Statistics Canada Table 14-10-0017-01, not seasonally adjusted |
| Units | Percentage points of the overall participation rate |

Chaining annual steps means any span (2012–19, 2024–26) is the sum of its years, so periods can be compared directly.

## Checks

- Each year, the aging and participation effects add up to the actual change in the rate (asserted in the code).
- Holding September 2019 age shares fixed gives a September 2026 rate of 66.1%, matching Statistics Canada's own estimate in its September 2026 release.
- The cumulative aging effect is −4.11 points (age only) and −4.07 points (age × sex). The small gap comes from shifts in the sex mix within age groups.
- The Excel workbook and the Python code give the same results.

## What it can't tell you

- **It's an accounting split, not a causal one.** Participation within an age group can respond to the age structure itself (scarce young workers can keep older ones on longer), and immigration changes who is in each group.
- **It counts people, not hours.** Older workers tend to work shorter weeks, so a participation gain at older ages adds less labour than the headcount suggests.
- **Results depend on the groups.** Finer groups move a little more of the change into the aging effect. Five-year groups with a 70+ top group are a common choice; wider top groups (65+) understate aging.
- **One partial year is not a trend.** A year-to-date step is based on fewer months and will be revised.

## When not to use it

- When you need a causal answer (why participation rose), you need a behavioural model or a cohort analysis.
- When the groups don't cover the total, the two effects won't add up to the actual change.
- With small geographies, suppressed or noisy cells can dominate the result. Use wider groups or a longer averaging window.
- With seasonally unadjusted data, never compare different months of the year.
