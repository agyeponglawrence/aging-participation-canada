"""Builds excel/Aging_LFP_shift_share_Canada.xlsx: the full decomposition with live Excel formulas.
Run: python analysis/build_workbook.py  (then recalculate in Excel or LibreOffice to fill cached values)."""
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "statcan_14-10-0017-01_canada.csv"
OUT = ROOT / "excel"
OUT.mkdir(parents=True, exist_ok=True)
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.comments import Comment

ARIAL = "Arial"
F = lambda **k: Font(name=ARIAL, **{"size": 10, **k})
BLUE = Font(name=ARIAL, size=10, color="0000FF")
GREEN = Font(name=ARIAL, size=10, color="008000")
BOLD = F(bold=True)
HDR_FILL = PatternFill("solid", fgColor="DDEBF7")
KEY_FILL = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF")

d = pd.read_csv(DATA, low_memory=False)
BANDS = ['15 to 19 years','20 to 24 years','25 to 29 years','30 to 34 years','35 to 39 years',
         '40 to 44 years','45 to 49 years','50 to 54 years','55 to 59 years','60 to 64 years',
         '65 to 69 years','70 years and over']
SHORT = ['15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70+']
ALL = '15 years and over'
GENDERS = [('Total - Gender','Total'),('Men+','Men'),('Women+','Women')]
MEAS = [('Population','Pop'),('Labour force','LF')]

wb = Workbook()

# ---------------- Raw ----------------
ws = wb.active; ws.title = "Raw"
keep = d[d['Labour force characteristics'].isin(['Population','Labour force'])][
    ['REF_DATE','GEO','Labour force characteristics','Gender','Age group','VECTOR','COORDINATE','VALUE','STATUS','SCALAR_FACTOR']]
ws.append(list(keep.columns))
for r in keep.itertuples(index=False):
    ws.append(list(r))
for c in ws[1]: c.font = BOLD; c.fill = HDR_FILL
for row in ws.iter_rows(min_row=2, min_col=8, max_col=8):
    row[0].font = BLUE
ws.freeze_panes = "A2"
for i, w in enumerate([10, 9, 26, 15, 18, 10, 10, 10, 7, 10], 1):
    ws.column_dimensions[L(i)].width = w

# ---------------- Monthly (pivot of Raw) ----------------
wm = wb.create_sheet("Monthly")
sub = d[d['Labour force characteristics'].isin(['Population','Labour force'])]
piv = sub.pivot_table(index='REF_DATE', columns=['Labour force characteristics','Gender','Age group'], values='VALUE')
vec = sub.groupby(['Labour force characteristics','Gender','Age group'])['VECTOR'].first()
months = sorted(piv.index)
# column plan: D.. : for gender, for measure, [ALL]+BANDS
cols = []  # (gender_long, gender_short, meas_long, meas_short, band_long, band_short)
for gl, gs in GENDERS:
    for ml, ms in MEAS:
        for bl, bs in [(ALL,'15+')] + list(zip(BANDS, SHORT)):
            cols.append((gl, gs, ml, ms, bl, bs))
COL0 = 4  # D
wm["A1"] = "Gender"; wm["A2"] = "Measure (thousands)"; wm["A3"] = "Age group"; wm["A4"] = "StatCan vector"
wm["A5"] = "REF_DATE"; wm["B5"] = "Year"; wm["C5"] = "Month"
for j, (gl, gs, ml, ms, bl, bs) in enumerate(cols):
    c = COL0 + j
    wm.cell(1, c, gs); wm.cell(2, c, ms); wm.cell(3, c, bs); wm.cell(4, c, vec[(ml, gl, bl)])
    wm.cell(5, c, f"{gs}|{ms}|{bs}")
for r in range(1, 6):
    for c in range(1, COL0 + len(cols)):
        wm.cell(r, c).font = BOLD; wm.cell(r, c).fill = HDR_FILL
MROW0 = 6
for i, m in enumerate(months):
    r = MROW0 + i
    wm.cell(r, 1, m); wm.cell(r, 2, int(m[:4])); wm.cell(r, 3, int(m[5:]))
    for j, (gl, gs, ml, ms, bl, bs) in enumerate(cols):
        cell = wm.cell(r, COL0 + j, float(piv.loc[m, (ml, gl, bl)])); cell.font = BLUE; cell.number_format = "#,##0.0"
MROW1 = MROW0 + len(months) - 1
wm.freeze_panes = "D6"
wm.column_dimensions["A"].width = 10
for j in range(len(cols)): wm.column_dimensions[L(COL0 + j)].width = 9
wm["A4"].comment = Comment("Values are a pivot of the Raw sheet (Statistics Canada table 14-10-0017-01, Canada, "
                           "unadjusted, persons in thousands). Each column header row 4 is the StatCan vector id.", "Claude")

def mcol(gs, ms, bs):
    for j, (gl, g, ml, m, bl, b) in enumerate(cols):
        if (g, m, b) == (gs, ms, bs): return L(COL0 + j)
    raise KeyError((gs, ms, bs))

# ---------------- Annual ----------------
wa = wb.create_sheet("Annual")
periods = [(str(y), y, 1, 12) for y in range(2011, 2026)] + [("2025 Jan-Oct", 2025, 1, 10), ("2026 Jan-Oct", 2026, 1, 10)]
wa["A1"] = "Period"; wa["B1"] = "Year"; wa["C1"] = "Last month"
for j, (gl, gs, ml, ms, bl, bs) in enumerate(cols):
    wa.cell(1, COL0 + j, f"{gs}|{ms}|{bs}")
for c in range(1, COL0 + len(cols)):
    wa.cell(1, c).font = BOLD; wa.cell(1, c).fill = HDR_FILL
AROW0 = 2
yr_rng = f"Monthly!$B${MROW0}:$B${MROW1}"; mo_rng = f"Monthly!$C${MROW0}:$C${MROW1}"
for i, (lab, y, m0, m1) in enumerate(periods):
    r = AROW0 + i
    wa.cell(r, 1, lab); wa.cell(r, 2, y); wa.cell(r, 3, m1)
    for j in range(len(cols)):
        cl = L(COL0 + j)
        rng = f"Monthly!${cl}${MROW0}:${cl}${MROW1}"
        cell = wa.cell(r, COL0 + j, f"=AVERAGEIFS({rng},{yr_rng},$B{r},{mo_rng},\"<=\"&$C{r})")
        cell.number_format = "#,##0.0"
AROW1 = AROW0 + len(periods) - 1
wa.freeze_panes = "D2"; wa.column_dimensions["A"].width = 14
for j in range(len(cols)): wa.column_dimensions[L(COL0 + j)].width = 9
wa["A1"].comment = Comment("Annual rows = average of the 12 monthly unadjusted values. The two Jan-Oct rows average "
                           "months 1-10 so that 2026 year-to-date is compared like-for-like with 2025.", "Claude")

def acell(gs, ms, bs, r):  # Annual cell ref for a period row
    return f"Annual!${mcol(gs, ms, bs)}${r}"

# ---------------- Rates ----------------
# Shares S (relative to TOTAL 15+ population) and rates P, for Total age cells and for Men/Women age cells.
wr = wb.create_sheet("Rates")
rblocks = []  # (header, formula builder)
for gs in ['Total', 'Men', 'Women']:
    for bs in SHORT:
        rblocks.append((f"S|{gs}|{bs}", lambda r, gs=gs, bs=bs: f"={acell(gs,'Pop',bs,r)}/{acell('Total','Pop','15+',r)}"))
for gs in ['Total', 'Men', 'Women']:
    for bs in SHORT:
        rblocks.append((f"P|{gs}|{bs}", lambda r, gs=gs, bs=bs: f"={acell(gs,'LF',bs,r)}/{acell(gs,'Pop',bs,r)}"))
# checks
rblocks.append(("Actual rate 15+", lambda r: f"={acell('Total','LF','15+',r)}/{acell('Total','Pop','15+',r)}"))
RC0 = 2
def rcol(h):
    for j, (hh, _) in enumerate(rblocks):
        if hh == h: return L(RC0 + j)
    raise KeyError(h)
rblocks.append(("Sum S Total", lambda r: "=SUM(" + f"{rcol('S|Total|15-19')}{r}:{rcol('S|Total|70+')}{r})"))
rblocks.append(("Sum S Men+Women", lambda r: f"=SUM({rcol('S|Men|15-19')}{r}:{rcol('S|Women|70+')}{r})"))
rblocks.append(("Implied rate (sum S x P, Total)", lambda r: f"=SUMPRODUCT({rcol('S|Total|15-19')}{r}:{rcol('S|Total|70+')}{r},{rcol('P|Total|15-19')}{r}:{rcol('P|Total|70+')}{r})"))
rblocks.append(("Implied rate (sum S x P, by sex)", lambda r: f"=SUMPRODUCT({rcol('S|Men|15-19')}{r}:{rcol('S|Women|70+')}{r},{rcol('P|Men|15-19')}{r}:{rcol('P|Women|70+')}{r})"))
rblocks.append(("Check: implied - actual (Total)", lambda r: f"={rcol('Implied rate (sum S x P, Total)')}{r}-{rcol('Actual rate 15+')}{r}"))
rblocks.append(("Check: implied - actual (by sex)", lambda r: f"={rcol('Implied rate (sum S x P, by sex)')}{r}-{rcol('Actual rate 15+')}{r}"))
wr["A1"] = "Period"
for j, (h, _) in enumerate(rblocks):
    wr.cell(1, RC0 + j, h)
for c in range(1, RC0 + len(rblocks)):
    wr.cell(1, c).font = BOLD; wr.cell(1, c).fill = HDR_FILL
for i, (lab, *_r) in enumerate(periods):
    r = AROW0 + i
    wr.cell(r, 1, f"=Annual!A{r}").font = GREEN
    for j, (h, fb) in enumerate(rblocks):
        cell = wr.cell(r, RC0 + j, fb(r))
        cell.number_format = "0.0000" if h.startswith(("S|", "Sum", "Check")) else "0.00%"
        if h.startswith("Check"): cell.number_format = "0.000000"
wr.freeze_panes = "B2"; wr.column_dimensions["A"].width = 14
for j in range(len(rblocks)): wr.column_dimensions[L(RC0 + j)].width = 10
wr["A1"].comment = Comment("S = population share of each age (x sex) cell in the TOTAL 15+ population. "
                           "P = labour force / population of that cell. Shares for Men and Women are relative to the total "
                           "population, so the 24 sex x age cells sum to 1 and their contributions add up to the aggregate rate.", "Claude")

# ---------------- Decomposition sheets ----------------
# transitions: (label, from_row, to_row, period_group)
trans = []
for y in range(2011, 2025):
    grp = "2011-2019" if y + 1 <= 2019 else ("2020-2021" if y + 1 <= 2021 else "2022-2025")
    trans.append((f"{y}->{y+1}", AROW0 + (y - 2011), AROW0 + (y + 1 - 2011), str(y + 1), grp))
trans.append(("2025 Jan-Oct -> 2026 Jan-Oct", AROW0 + 15, AROW0 + 16, "2026 YTD", "2026 YTD (y/y)"))

def build_decomp(name, cells, title):
    """cells: list of (gs, bs) age (x sex) cells."""
    w = wb.create_sheet(name)
    w["A1"] = title; w["A1"].font = F(bold=True, size=12)
    w["A2"] = ("Midpoint (Shapley) shift-share. Composition_g = (S1-S0) x (P0+P1)/2 ; Rate_g = (P1-P0) x (S0+S1)/2. "
               "The two terms sum exactly to the change in the aggregate participation rate. Units: percentage points.")
    w["A2"].font = F(italic=True)
    hdr = ["Transition", "To (year label)", "Period group"]
    comp_h = [f"Comp {gs} {bs}" for gs, bs in cells]
    rate_h = [f"Rate {gs} {bs}" for gs, bs in cells]
    tail = ["Composition total", "Rate total", "Comp + Rate", "Actual change", "Check (sum - actual)",
            "Cum. composition", "Cum. rate", "Cum. actual"]
    H = hdr + comp_h + rate_h + tail
    HR = 4
    for j, h in enumerate(H, 1):
        c = w.cell(HR, j, h); c.font = BOLD; c.fill = HDR_FILL; c.alignment = Alignment(wrap_text=True, vertical="top")
    w.row_dimensions[HR].height = 42
    n = len(cells)
    c_comp0 = 4; c_rate0 = 4 + n; c_tail0 = 4 + 2 * n
    T = {h: L(c_tail0 + k) for k, h in enumerate(tail)}
    R0 = HR + 1
    for i, (lab, fr, to, ylab, grp) in enumerate(trans):
        r = R0 + i
        w.cell(r, 1, lab); w.cell(r, 2, ylab); w.cell(r, 3, grp)
        for k, (gs, bs) in enumerate(cells):
            S = rcol(f"S|{gs}|{bs}"); P = rcol(f"P|{gs}|{bs}")
            w.cell(r, c_comp0 + k, f"=100*(Rates!{S}{to}-Rates!{S}{fr})*(Rates!{P}{fr}+Rates!{P}{to})/2").number_format = "0.000"
            w.cell(r, c_rate0 + k, f"=100*(Rates!{P}{to}-Rates!{P}{fr})*(Rates!{S}{fr}+Rates!{S}{to})/2").number_format = "0.000"
        w.cell(r, c_tail0 + 0, f"=SUM({L(c_comp0)}{r}:{L(c_comp0+n-1)}{r})")
        w.cell(r, c_tail0 + 1, f"=SUM({L(c_rate0)}{r}:{L(c_rate0+n-1)}{r})")
        w.cell(r, c_tail0 + 2, f"={T['Composition total']}{r}+{T['Rate total']}{r}")
        A = rcol("Actual rate 15+")
        w.cell(r, c_tail0 + 3, f"=100*(Rates!{A}{to}-Rates!{A}{fr})")
        w.cell(r, c_tail0 + 4, f"={T['Comp + Rate']}{r}-{T['Actual change']}{r}").number_format = "0.000000"
        for k, h in enumerate(["Cum. composition", "Cum. rate", "Cum. actual"]):
            src = T[["Composition total", "Rate total", "Actual change"][k]]
            w.cell(r, c_tail0 + 5 + k, f"=SUM({src}${R0}:{src}{r})")
        for k in range(8):
            if k != 4: w.cell(r, c_tail0 + k).number_format = "0.00"
    R1 = R0 + len(trans) - 1
    # period-group sums by cell
    SR = R1 + 3
    w.cell(SR - 1, 1, "Cumulative contribution by period group (percentage points)").font = BOLD
    groups = ["2011-2019", "2020-2021", "2022-2025", "2026 YTD (y/y)"]
    w.cell(SR, 1, "Period group").font = BOLD
    for j in range(2, len(H) + 1):
        w.cell(SR, j, f"={L(j)}{HR}").font = BOLD
    for j in range(1, len(H) + 1): w.cell(SR, j).fill = HDR_FILL
    for g_i, g in enumerate(groups + ["2011-2026 YTD (all)"]):
        r = SR + 1 + g_i
        w.cell(r, 1, g)
        for j in range(c_comp0, c_tail0 + 4):
            cl = L(j)
            if g.startswith("2011-2026"):
                w.cell(r, j, f"=SUM({cl}${R0}:{cl}${R1})").number_format = "0.00"
            else:
                w.cell(r, j, f"=SUMIFS({cl}${R0}:{cl}${R1},$C${R0}:$C${R1},$A{r})").number_format = "0.00"
    # annualized pace row for the two comparison windows
    r = SR + 1 + len(groups) + 1
    w.cell(r, 1, "Average per year, 2011-2019 (8 steps)").font = BOLD
    for j in range(c_comp0, c_tail0 + 4):
        w.cell(r, j, f"={L(j)}{SR+1}/8").number_format = "0.00"
    r2 = r + 1
    w.cell(r2, 1, "2026 YTD y/y step (one year)").font = BOLD
    for j in range(c_comp0, c_tail0 + 4):
        w.cell(r2, j, f"={L(j)}{SR+4}").number_format = "0.00"
    w.freeze_panes = w.cell(R0, 4)
    w.column_dimensions["A"].width = 26; w.column_dimensions["B"].width = 10; w.column_dimensions["C"].width = 14
    for j in range(4, len(H) + 1): w.column_dimensions[L(j)].width = 10
    return w, R0, R1, T, SR, c_comp0, c_rate0, n

age_cells = [("Total", bs) for bs in SHORT]
sex_cells = [("Men", bs) for bs in SHORT] + [("Women", bs) for bs in SHORT]
wA, A_R0, A_R1, A_T, A_SR, A_c0, A_r0, A_n = build_decomp("Decomp_Age", age_cells, "Decomposition by 5-year age band (both sexes)")
wS, S_R0, S_R1, S_T, S_SR, S_c0, S_r0, S_n = build_decomp("Decomp_AgeSex", sex_cells, "Decomposition by 5-year age band x sex (24 cells; shares relative to total population)")
wS["A3"] = ("Note: here the composition term also absorbs shifts in the sex mix within each age band (e.g. women outliving men at 70+), so its total differs slightly from Decomp_Age. The rate term is the part attributable to changing participation of each sex-age cell.")
wS["A3"].font = F(italic=True)

# ---------------- Checks ----------------
wc = wb.create_sheet("Checks")
wc["A1"] = "Checks against published benchmarks"; wc["A1"].font = F(bold=True, size=12)
rows = [("Check", "Workbook value", "Published / expected", "Difference", "Source and note")]
# Sept 2019 vs Sept 2026 standardization (StatCan Chart 4)
def mrow(m): return MROW0 + months.index(m)
r19, r26, r25 = mrow("2019-09"), mrow("2026-09"), mrow("2025-09")
def mref(gs, ms, bs, r): return f"Monthly!${mcol(gs,ms,bs)}${r}"
def act(r): return f"100*{mref('Total','LF','15+',r)}/{mref('Total','Pop','15+',r)}"
def std(rS, rP):  # shares from rS, rates from rP
    terms = "+".join(f"{mref('Total','Pop',b,rS)}/{mref('Total','Pop','15+',rS)}*{mref('Total','LF',b,rP)}/{mref('Total','Pop',b,rP)}" for b in SHORT)
    return f"100*({terms})"
rows += [
    ("Participation rate, Sept 2019 (unadjusted)", f"={act(r19)}", 65.9, "StatCan Daily 9 Oct 2026, Chart 4"),
    ("Participation rate, Sept 2026 (unadjusted)", f"={act(r26)}", 64.6, "StatCan Chart 4 (SA published rate is 64.8)"),
    ("Sept 2026 rate at Sept 2019 age composition", f"={std(r19, r26)}", 66.1, "StatCan Chart 4: 5-year shares held at Sept 2019"),
    ("Sept 2025 rate at Sept 2019 age composition", f"={std(r19, r25)}", 66.2, "StatCan Chart 4"),
    ("Standardized change, Sept 2025 -> Sept 2026", f"={std(r19, r26)}-{std(r19, r25)}", -0.1, "StatCan text: 'little changed (-0.1 percentage points) year over year'"),
    ("Standardized change, Sept 2019 -> Sept 2026", f"={std(r19, r26)}-{act(r19)}", 0.2, "StatCan text: '0.2 percentage points higher than in September 2019'"),
    ("65+ share of 15+ population, Sept 2026", f"=100*({mref('Total','Pop','65-69',r26)}+{mref('Total','Pop','70+',r26)})/{mref('Total','Pop','15+',r26)}", 23.2, "StatCan text box"),
    ("65+ share of 15+ population, Sept 2019", f"=100*({mref('Total','Pop','65-69',r19)}+{mref('Total','Pop','70+',r19)})/{mref('Total','Pop','15+',r19)}", 20.5, "StatCan text box"),
    ("Cumulative composition term, 2011 -> 2026 YTD", f"=Decomp_Age!{A_T['Cum. composition']}{A_R1}", -4.0, "Tombe (The Hub, Jul 2026): aging lowered participation 'about four full percentage points' over 15 years"),
    ("Cumulative rate term, 2011 -> 2026 YTD", f"=Decomp_Age!{A_T['Cum. rate']}{A_R1}", None, "No published benchmark; sign should be positive (Fields 2017)"),
    ("Cumulative actual change, 2011 -> 2026 YTD", f"=Decomp_Age!{A_T['Cum. actual']}{A_R1}", None, "Should equal composition + rate"),
    ("Max abs. check residual, Decomp_Age", f"=MAX(ABS(MIN(Decomp_Age!{A_T['Check (sum - actual)']}{A_R0}:{A_T['Check (sum - actual)']}{A_R1})),ABS(MAX(Decomp_Age!{A_T['Check (sum - actual)']}{A_R0}:{A_T['Check (sum - actual)']}{A_R1})))", 0, "Terms must sum exactly to the actual change (rounding of published levels only)"),
    ("Max abs. check residual, Decomp_AgeSex", f"=MAX(ABS(MIN(Decomp_AgeSex!{S_T['Check (sum - actual)']}{S_R0}:{S_T['Check (sum - actual)']}{S_R1})),ABS(MAX(Decomp_AgeSex!{S_T['Check (sum - actual)']}{S_R0}:{S_T['Check (sum - actual)']}{S_R1})))", 0, "Same, 24-cell version"),
]
for i, row in enumerate(rows):
    r = 3 + i
    for j, v in enumerate(row[:4] if i == 0 else [row[0], row[1], row[2], None], 1):
        wc.cell(r, j, v)
    if i == 0:
        wc.cell(r, 5, row[4])
        for j in range(1, 6): wc.cell(r, j).font = BOLD; wc.cell(r, j).fill = HDR_FILL
    else:
        wc.cell(r, 5, row[3])
        wc.cell(r, 2).number_format = "0.00"
        if row[2] is not None:
            wc.cell(r, 3).font = BLUE; wc.cell(r, 3).number_format = "0.0"
            wc.cell(r, 4, f"=B{r}-C{r}").number_format = "0.00"
wc.column_dimensions["A"].width = 46; wc.column_dimensions["B"].width = 14; wc.column_dimensions["C"].width = 18
wc.column_dimensions["D"].width = 11; wc.column_dimensions["E"].width = 90
wc["A3"].comment = Comment("Blue = published figure typed in from the source named in column E.", "Claude")

# ---------------- Summary ----------------
wsu = wb.create_sheet("Summary", 0)
wsu["A1"] = "Aging and labour force participation, Canada, 2011-2026: shift-share summary"; wsu["A1"].font = F(bold=True, size=13)
wsu["A2"] = "Source: Statistics Canada table 14-10-0017-01 (Canada, unadjusted, 5-year age groups x gender). All cells are formulas linked to the Decomp sheets; percentage points."
wsu["A2"].font = F(italic=True)
# Table 1: annual contributions
wsu["A4"] = "Table 1. Annual contributions to the change in the participation rate"; wsu["A4"].font = BOLD
h = ["Year", "Composition (aging)", "Rate (age-specific participation)", "Actual change", "Cum. composition", "Cum. rate", "Cum. actual"]
for j, x in enumerate(h, 1):
    c = wsu.cell(5, j, x); c.font = BOLD; c.fill = HDR_FILL; c.alignment = Alignment(wrap_text=True)
wsu.row_dimensions[5].height = 30
T1R0 = 6
for i in range(len(trans)):
    r = T1R0 + i; sr = A_R0 + i
    wsu.cell(r, 1, f"=Decomp_Age!B{sr}").font = GREEN
    for j, key in enumerate(["Composition total", "Rate total", "Actual change", "Cum. composition", "Cum. rate", "Cum. actual"], 2):
        c = wsu.cell(r, j, f"=Decomp_Age!{A_T[key]}{sr}"); c.font = GREEN; c.number_format = "0.00"
T1R1 = T1R0 + len(trans) - 1
# Table 2: rate term by age band and period group
T2 = T1R1 + 3
wsu.cell(T2, 1, "Table 2. Rate term by age band (both sexes), cumulative by period, percentage points").font = BOLD
groups = ["2011-2019", "2020-2021", "2022-2025", "2026 YTD (y/y)", "2011-2026 YTD (all)"]
hdr2 = ["Age band"] + groups + ["Avg/yr 2011-2019"]
for j, x in enumerate(hdr2, 1):
    c = wsu.cell(T2 + 1, j, x); c.font = BOLD; c.fill = HDR_FILL
for k, bs in enumerate(SHORT):
    r = T2 + 2 + k
    wsu.cell(r, 1, bs)
    col = L(A_r0 + k)
    for g_i in range(5):
        c = wsu.cell(r, 2 + g_i, f"=Decomp_Age!{col}{A_SR + 1 + g_i}"); c.font = GREEN; c.number_format = "0.00"
    c = wsu.cell(r, 7, f"=Decomp_Age!{col}{A_SR + 6}"); c.font = GREEN; c.number_format = "0.00"
r = T2 + 2 + len(SHORT)
wsu.cell(r, 1, "Rate total").font = BOLD
for g_i in range(5):
    c = wsu.cell(r, 2 + g_i, f"=Decomp_Age!{A_T['Rate total']}{A_SR + 1 + g_i}"); c.font = GREEN; c.number_format = "0.00"
c = wsu.cell(r, 7, f"=Decomp_Age!{A_T['Rate total']}{A_SR + 6}"); c.font = GREEN; c.number_format = "0.00"
r += 1
wsu.cell(r, 1, "Composition total (memo)").font = BOLD
for g_i in range(5):
    c = wsu.cell(r, 2 + g_i, f"=Decomp_Age!{A_T['Composition total']}{A_SR + 1 + g_i}"); c.font = GREEN; c.number_format = "0.00"
c = wsu.cell(r, 7, f"=Decomp_Age!{A_T['Composition total']}{A_SR + 6}"); c.font = GREEN; c.number_format = "0.00"
T2END = r
# Table 3: rate term 55+ by sex
T3 = T2END + 3
wsu.cell(T3, 1, "Table 3. Rate term for older age bands, by sex, cumulative by period (contribution to the aggregate rate, pp)").font = BOLD
for j, x in enumerate(["Cell"] + groups, 1):
    c = wsu.cell(T3 + 1, j, x); c.font = BOLD; c.fill = HDR_FILL
older = ["55-59", "60-64", "65-69", "70+"]
rr = T3 + 2
for gs in ["Men", "Women"]:
    for bs in older:
        k = sex_cells.index((gs, bs)); col = L(S_r0 + k)
        wsu.cell(rr, 1, f"{gs} {bs}")
        for g_i in range(5):
            c = wsu.cell(rr, 2 + g_i, f"=Decomp_AgeSex!{col}{S_SR + 1 + g_i}"); c.font = GREEN; c.number_format = "0.00"
        rr += 1
    # subtotal 55+
    wsu.cell(rr, 1, f"{gs} 55+ subtotal").font = BOLD
    for g_i in range(5):
        c = wsu.cell(rr, 2 + g_i, f"=SUM({L(2+g_i)}{rr-4}:{L(2+g_i)}{rr-1})"); c.number_format = "0.00"
    rr += 1
# also all-ages by sex
for gs in ["Men", "Women"]:
    k0 = sex_cells.index((gs, "15-19")); k1 = sex_cells.index((gs, "70+"))
    wsu.cell(rr, 1, f"{gs} all ages, rate term").font = BOLD
    for g_i in range(5):
        c = wsu.cell(rr, 2 + g_i, f"=SUM(Decomp_AgeSex!{L(S_r0+k0)}{S_SR+1+g_i}:{L(S_r0+k1)}{S_SR+1+g_i})"); c.font = GREEN; c.number_format = "0.00"
    rr += 1
T3END = rr - 1
for col, w in zip("ABCDEFG", [30, 14, 16, 14, 16, 18, 16]):
    wsu.column_dimensions[col].width = w

# Charts
bar = BarChart(); bar.type = "col"; bar.grouping = "stacked"; bar.overlap = 100
bar.title = "Annual contributions to the change in the participation rate (pp)"
bar.y_axis.title = "Percentage points"; bar.x_axis.title = "Year"
cats = Reference(wsu, min_col=1, min_row=T1R0, max_row=T1R1)
bar.add_data(Reference(wsu, min_col=2, max_col=3, min_row=5, max_row=T1R1), titles_from_data=True)
bar.set_categories(cats)
line = LineChart()
line.add_data(Reference(wsu, min_col=4, min_row=5, max_row=T1R1), titles_from_data=True)
line.set_categories(cats)
bar += line
bar.roundedCorners = False; bar.legend.overlay = False; bar.title.overlay = False
bar.x_axis.title.overlay = False; bar.y_axis.title.overlay = False
bar.x_axis.delete = False; bar.y_axis.delete = False
bar.height = 9; bar.width = 20
wsu.add_chart(bar, "I4")

cum = LineChart(); cum.title = "Cumulative since 2011 (pp)"
cum.add_data(Reference(wsu, min_col=5, max_col=7, min_row=5, max_row=T1R1), titles_from_data=True)
cum.set_categories(cats)
cum.roundedCorners = False; cum.legend.overlay = False; cum.title.overlay = False
cum.x_axis.delete = False; cum.y_axis.delete = False
cum.height = 9; cum.width = 20
wsu.add_chart(cum, "I23")

# ---------------- ReadMe ----------------
wrd = wb.create_sheet("ReadMe", 0)
lines = [
    ("Aging and labour force participation in Canada: shift-share workbook", F(bold=True, size=13)),
    ("", None),
    ("Purpose", BOLD),
    ("Decompose annual changes in Canada's labour force participation rate (15+) into a composition term (shift in population age shares) and a rate term (changes in age-specific participation), chained from 2011, with the rate term split by age band and by sex.", None),
    ("", None),
    ("Data", BOLD),
    ("Statistics Canada table 14-10-0017-01, Labour force characteristics by gender and detailed age group, monthly, unadjusted for seasonality. Canada. Population and labour force, persons in thousands. 5-year age groups 15-19 ... 65-69 and 70+. Months 2011-01 to 2026-10. Downloaded by Lawrence Agyepong, Nov 2026.", None),
    ("", None),
    ("Sheets", BOLD),
    ("Summary: Tables 1-3 and charts, all linked to the Decomp sheets.", None),
    ("Checks: workbook values next to published benchmarks (StatCan Oct 2026 Daily, Tombe 2026). Blue cells are typed-in published figures.", None),
    ("Decomp_Age: 12 age cells, both sexes. Decomp_AgeSex: 24 age x sex cells with shares relative to the total population, so contributions add to the aggregate.", None),
    ("Rates: shares S and participation rates P per cell per period, with identity checks (shares sum to 1; sum of S x P equals the actual rate).", None),
    ("Annual: AVERAGEIFS over Monthly; 2011-2025 annual averages and Jan-Oct averages for 2025 and 2026.", None),
    ("Monthly: pivot of Raw (values, blue), one column per vector. Raw: the StatCan rows for population and labour force.", None),
    ("", None),
    ("Method", BOLD),
    ("For each pair of adjacent periods (0 -> 1) and each cell g: Composition_g = (S1 - S0) x (P0 + P1)/2 and Rate_g = (P1 - P0) x (S0 + S1)/2, where S is the cell's share of the 15+ population and P its participation rate. Midpoint weights make the interaction term vanish, so the terms sum exactly to the change in the aggregate rate. Cumulative values are sums of the annual terms (chained), so sub-period contributions are well defined.", None),
    ("The final step is 2025 Jan-Oct -> 2026 Jan-Oct (a year-over-year step on like months, because the detailed-age table is not seasonally adjusted). Cumulative figures through 2025 use annual averages; the 2026 YTD cumulative adds that y/y step.", None),
    ("", None),
    ("Conventions", BOLD),
    ("Blue text = data or typed-in published figures. Black = formulas. Green = links to another sheet. Units in Decomp and Summary sheets are percentage points.", None),
    ("Published levels are rounded to 0.1 thousand, so computed rates match published rates only within rounding; the Checks sheet shows how close.", None),
    ("", None),
    ("Caveats", BOLD),
    ("Contributions, not causes: age-specific rates respond to the age structure and to immigration. A 70+ top band hides aging within 70+ (small, and rates there are low). Education is inside the rate term. Participation counts people, not hours.", None),
]
for i, (t, f) in enumerate(lines, 1):
    c = wrd.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical="top")
    if f: c.font = f
    else: c.font = F()
wrd.column_dimensions["A"].width = 120

# fonts everywhere
for sh in wb.worksheets:
    for row in sh.iter_rows():
        for c in row:
            if c.value is not None and c.font.name != ARIAL:
                c.font = Font(name=ARIAL, size=c.font.size or 10, bold=c.font.bold, italic=c.font.italic, color=c.font.color)

wb.save(OUT / "Aging_LFP_shift_share_Canada.xlsx")
print("saved")
