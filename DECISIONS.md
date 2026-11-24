# Decision log

The judgment calls behind this analysis: what was chosen, what was considered instead, and why. Useful if you adapt the method to a different question.

| Decision | Chosen | Alternatives considered | Why |
|---|---|---|---|
| Base year | 2011 | 2007, 2010 | 2011 is when the first baby boomers turned 65, so it marks the start of the retirement wave. Earlier research (Bank of Canada, Statistics Canada) already covers the drag from 2007. |
| Decomposition weights | Midpoint (Shapley) | Base-year weights; end-year weights | Base- or end-year weights leave an interaction term (about +0.16 points over 2011–26) that has to be assigned somewhere. Midpoint weights split it evenly and the parts add up exactly. Base-year gives aging −4.11 / rate +2.14; end-year −3.95 / +2.30; midpoint in between. |
| One long span or annual chaining | Chained annually | A single 2011 → 2026 comparison | Chaining shows when the offset happened and lets any sub-period be summed. A single span mixed seasonally different months in the final year. |
| Age groups | 5-year groups, 70+ at the top | 10-year groups; 65+ at the top | Participation falls steeply between 55 and 70, so wide groups hide part of the aging. Splitting 65–69 from 70+ keeps the drop between them in the aging effect. |
| Split by sex | Yes (24 cells) | Age only | The offset came mostly from women, which is a central finding. The age-only version is kept as a check (−4.11 vs −4.07). |
| Latest year | Same months year to date | Wait for full-year data; use the last 12 months | The analysis asks what's happening now. Same months avoid seasonal bias in unadjusted data. The cost is a noisier final step, flagged in the article. |
| Data | Unadjusted monthly LFS | Seasonally adjusted series | Detailed age-by-sex series aren't published seasonally adjusted. Annual averages remove seasonality anyway. |

## Title history

The article's title changed three times while the analysis was being written up. Each change moved the title closer to the main finding: what is happening now that population growth has slowed.

| # | Date | Title | Why it changed |
|---|---|---|---|
| 1 | Nov 16, 2026 | Nothing pushing back: the full weight of aging returns to Canada's labour market | Working title for the first draft. |
| 2 | Nov 23, 2026 | Aging's full drag returns | Shorter title for the Substack draft. |
| 3 | Nov 24, 2026 | **Canada's aging drag is back, and nothing is offsetting it** (final) | Titles 1 and 2 covered aging's return but not the other half of the finding: rising participation no longer offsets it. Considered and rejected: "Canada's aging drag is back at full strength" (only half the story; −0.36 is about its normal pace), "As population growth slows, aging's full drag returns", "With fewer newcomers, aging is back at full strength", and "Canada's participation rate has lost its cushion". |

Final subtitle: *So far in 2026, with population growth slowing, the participation rate is falling at roughly aging's pace.*
