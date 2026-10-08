# Redesign: the same data as an executive slide

Slide log for item `figure1-redesign` (chart-redesign). Source: GAO-25-107795, "Figure 1: Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year 2025, in millions of dollars", PDF page 11 (printed page 5). Files in this folder: `redesign.pptx`, `redesign.pdf`, `redesign.png`.

Sorted by operations and maintenance share, with a line at the all-agency 79%, labels on the five extremes, and an action title in GAO's own numbers. Notes keep the report's general 'about 80 percent' and its legacy caveat apart from the FY2025 figure.

How this was made: Claude Code agents rebuilt this GAO figure from the source image as editable PowerPoint and drafted the logs. I approved the source and the rules each rebuild follows, and checked every slide, number and log before publishing.

## Changed

| What | Why |
|---|---|
| Replaced GAO's figure title with an action title: 'Agencies planned 79% of FY2025 IT spending, about $83 billion, for operations and maintenance (O&M)'. | A slide read at a distance needs its finding in the title. The numbers and hedges are GAO's: 'about $83 billion (79 percent) in planned total IT spending for fiscal year 2025 was intended for operations and maintenance' (PDF p. 10, printed p. 4). |
| Set the subtitle to the spread: 'Planned O&M share by agency ranged from 60% (Transportation) to 97% (Housing and Urban Development)'. | The title gives the all-agency 79%, and the 24 bars show how far agencies sit from it, which GAO also points out: the figure 'shows how agencies can vary in their percentage of operations and maintenance spending' (PDF p. 10). The subtitle states that spread from the lowest and highest rows of data/figure1.csv, and says 'planned' as GAO does. |
| Sorted the 24 agencies by O&M share, highest first, in place of GAO's order by total spending. | The slide compares each agency with the overall share, and a sorted bar chart shows the spread and the extremes at a glance. Agencies with equal shares keep GAO's order, largest total first. |
| Plotted one series, the O&M share, on a 0 to 100% axis that starts at zero. | Each agency's two shares add to 100, so the DME bar repeats the same information. One series drops half the ink and the legend, and the zero baseline keeps bar lengths true to the shares. |
| Added a reference line at the all-agency share, labeled 'All 24 agencies: 79%'. | It turns each bar into a comparison with the total. The line sits at the exact share from the printed dollars, 82,828 / 105,136 = 78.78%, and carries GAO's rounded label. |
| Labeled values only on the five extremes: Housing and Urban Development 97%, Small Business Administration 95%, Homeland Security 91%, Treasury 61% and Transportation 60%. | These five stand apart from the rest: the next share below 91% is 87%, and the next above 61% is 69%. The gridlines carry the other values, and every value stays in the faithful slide and data/figure1.csv. |
| Shortened agency names, for example 'Defense' for 'Department of Defense', 'NASA' and 'USAID'. | Short names fit 24 rows beside the bars. The mapping is the redesign_label column of data/figure1.csv. |
| Left out the dollar totals. | The slide carries one message, the share. The totals stay in the faithful slide and the CSV, and the notes column gives the overall $82,828 million of $105,136 million. |
| Added a notes column: what the line is, the report's separate 'about 80 percent' statement, and GAO's legacy caveat. | These are the qualifiers a reader needs before repeating the number. Each one cites the report page it comes from. The three notes are paragraphs of one text box at one fixed gap, starting level with the top of the plot. |
| Colored the bars #2B5D96 and the line #D55E00 (vermilion). | The dataviz palette validator rated #2F5D8A below its chroma floor (OKLCH chroma 0.089, so it reads gray). #2B5D96, a slightly more saturated blue of about the same lightness, passes every check with #D55E00 (data/palette-check.txt). |

## Kept

| What | Why |
|---|---|
| GAO's numbers and hedges: 'planned', 'about $83 billion', 79%. | The title claims no more precision or certainty than the report. |
| The definitions: operations and maintenance (O&M) spelled out in the title, and the other 21% named as development, modernization and enhancement. | They come from the figure's legend and the report's footnote 11 (PDF p. 10). |
| The scope and source: the 24 CFO Act agencies, GAO-25-107795 Figure 1, GAO analysis of IT Dashboard data. | The scope is from PDF p. 10 and the source line from the figure. |
| Arial throughout, theme fonts included: title 28 pt, subtitle 16 pt, notes 14 pt, chart text 11 to 12 pt, source and footer 10 pt. | The deck's type standard. Chart text sits below the 14 pt body size because of the 24 rows (see Rejected), and nothing is under 10 pt. |

## Rejected

| What | Why |
|---|---|
| A dot plot. | Dots would show the same 24 shares, but bars on a 0 to 100% axis read as a share of the whole, which is what the data are, and they keep the zero baseline in view. |
| Small multiples. | There is one measure and one comparison. Panels would split the agencies across several plots and repeat the reference line. |
| Keeping the 100% stacked bars with DME. | DME is 100 minus O&M on every row, so the second color adds a legend and no information. |
| Coloring the five extremes and graying the rest. | It would pull the eye to the extremes and away from the reference line, which carries the title's number. In a sorted chart, position and labels already mark the extremes. |
| Value labels on all 24 bars. | A column of 24 numbers competes with the reference line. The faithful slide keeps every value. |
| Agency names at 14 pt, the deck's body minimum. | Under a two-line title the 24 rows get 0.179 in each, and 14 pt names would overlap. They are 12 pt, the largest size that keeps them apart. One render at a slightly tighter pitch made LibreOffice drop every other name, so the label interval is now fixed at 1. |
| Putting the report's 'about 80 percent' in the title. | That is GAO's general statement about what agencies have typically reported, not the FY2025 plan, and the slide keeps the two numbers apart. |

## Flagged

| What | Evidence |
|---|---|
| The report gives two figures for O&M spending: 'about 80 percent' in general and 79% for FY2025 plans. | PDF p. 2 and p. 7 (printed p. 1): agencies 'have typically reported spending about 80 percent on operations and maintenance of existing IT'. PDF p. 10 (printed p. 4): 'about $83 billion (79 percent) in planned total IT spending for fiscal year 2025'. The slide uses 79%, and its notes keep the general statement separate. |
| O&M spending is not the same as legacy spending. | PDF p. 10: 'it is uncertain how much of the operations and maintenance is spent on legacy technology because the Office of Management and Budget (OMB) does not require agencies to include information on whether their investments are considered legacy IT.' The slide's third note keeps this caveat. |
| The reference line is a drawn shape, not part of the chart data. | It sits at 78.78% of the plot width and measured 78.81% in a 300 dpi render (data/reference-line.json). It does not move if the chart data change, and the speaker notes say so. |
| Ties are ordered by total spending because the source cannot rank them. | Four groups share a printed share: 87% (Veterans Affairs, NASA), 83% (Defense, Interior, Nuclear Regulatory Commission), 79% (Justice, Education) and 72% (General Services Administration, USAID). GAO drew the bars from rounded percents (checks.md). |
| The published PDF and PNG use Liberation Sans where the .pptx names Arial. | pdffonts lists only LiberationSans and LiberationSans-Bold in both PDFs. LibreOffice substitutes this metric-compatible font, so widths and line breaks hold and glyph shapes differ slightly. |
| No step in this build opened the file in Microsoft PowerPoint. | The .pptx comes from PptxGenJS 4.0.1 and is checked with python-pptx 1.0.2. Its file properties name PptxGenJS 4.0.1 as the application (the inspector checks this). Renders, the overlay and every position calibration come from LibreOffice, so text positions in PowerPoint are unchecked. |

## Checks

| Check | Result |
|---|---|
| Chart values | The chart cache and the embedded workbook equal the printed O&M shares in data/figure1.csv, in the sorted order (inspector). |
| Sort and tie order | 4 tie groups, each in GAO's order (checks.md). |
| Extremes | Highest: Housing and Urban Development 97%, Small Business Administration 95%, Homeland Security 91%. Lowest: Treasury 61%, Transportation 60%. Value labels appear on exactly those five (inspector). |
| Reference line position | 78.81% of the axis in a 300 dpi render, against a target of 78.78% (data/reference-line.json). |
| Numbers in the title, subtitle and notes | 'about $83 billion' is $82,828M rounded, 79% is 78.78% rounded and 21% is 21.22% rounded, as GAO prints them (checks.md). The subtitle's 60% and 97% are the printed shares of Transportation and Housing and Urban Development (data/figure1.csv rows 6 and 18), the lowest and highest of the 24. |
| Palette | The dataviz validator passes #2B5D96 with #D55E00 on the lightness band, chroma floor, colorblind separation (delta E 21.3), normal-vision floor and contrast (data/palette-check.txt). |
| Inspector (python-pptx) on redesign.pptx | 17 of 17 checks pass: one native bar chart, values and embedded workbook equal to the CSV, labels only on the extremes, no pictures, Arial only (theme fonts too), footer present, no dash characters or banned words, file properties that name PptxGenJS. |
| Render review | All 24 names visible with no overlaps at 96 and 200 dpi. An earlier render that dropped every other name was fixed by setting the label interval to 1. |

Portfolio reconstruction of a public GAO figure. Not a GAO product.
