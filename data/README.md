# Data

`raw/statcan_14-10-0017-01_canada.csv` is an extract of Statistics Canada Table 14-10-0017-01, *Labour force characteristics by gender and detailed age group, monthly, unadjusted for seasonality* (DOI: https://doi.org/10.25318/1410001701-eng).

- Geography: Canada
- Months: January 2011 to October 2026
- Downloaded: November 2026
- Units: persons, thousands

The analysis uses only the **Population** and **Labour force** rows. Statistics Canada revises the Labour Force Survey from time to time (for example when it rebases to new population estimates), so a fresh download may give slightly different numbers.

For provinces, run `python analysis/download_data.py` to fetch the full table. The full file is large, so it is git-ignored.

Source: Statistics Canada. Reproduced and distributed on an "as is" basis with the permission of Statistics Canada, under the Statistics Canada Open Licence.
