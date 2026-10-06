# Faithful rebuild: GAO Figure 1 as a native PowerPoint chart

Slide log for item `figure1-faithful` (chart-faithful). Source: GAO-25-107795, "Figure 1: Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year 2025, in millions of dollars", PDF page 11 (printed page 5). Files in this folder: `faithful.pptx`, `faithful.pdf`, `faithful.png`, `overlay.png`.

GAO's figure of planned FY2025 IT spending for 24 agencies, rebuilt on a 16:9 slide as one native 100% stacked bar chart with the 48 printed percents embedded and a table for names and totals. Laid over the published figure, its bar outlines land within 1 px at 300 ppi.

How this was made: Claude Code agents rebuilt this GAO figure from the source image as editable PowerPoint and drafted the logs. I chose the source, set the rules each rebuild follows, and checked every slide, number and log before publishing.

## Changed

| What | Why |
|---|---|
| Moved GAO's report figure onto a 16:9 slide at its printed size, 5.0 by 6.32 in, centered, with the report's caption and rule above it. | The source is a portrait figure on a report page. At its printed size the rebuild keeps GAO's point sizes and fits the 7.5 in slide height, so nothing is rescaled. |
| Rebuilt the 24 bars as one native 100% stacked bar chart whose embedded data are the 48 printed percents. | A native chart opens in Edit Data, so every value can be checked in PowerPoint. GAO drew each bar from its rounded percent (all 24 bars measure within 0.07 points of their labels), so charting the printed percents reproduces the drawing. |
| Set the agency names and dollar totals in a native two-column table whose 24 rows share the chart's row pitch of 0.202 in. | A table keeps all 48 cells in one editable object and lines each row up with its bar by construction. A text column would have meant 24 or 48 loose text boxes to keep in line. |
| Drew the top band (the gray label area, the overall O&M and DME bar and its five values) with shapes and text boxes. | The band is about twice as tall as an agency bar and sits apart from the rows, so it cannot be a 25th category of the same chart. Its divider sits at the printed 79%, where GAO drew it: the band's bar measures 79.00%. |
| Set the two DME labels that sit outside their bars (Housing and Urban Development 3%, Small Business Administration 5%) as text boxes, and switched off the chart's own labels for those two points. | PowerPoint stores a moved data label as an offset from its default spot, and LibreOffice computes that spot differently, so a moved label would land in different places in the two programs. The inspector checks both text boxes against the CSV. |
| Drew the axis rule, the numbers 0 to 100 and the axis title as a shape and text boxes in place of the chart's own axis. | A 100% stacked chart's axis prints 0% to 100%, and GAO prints the numbers without percent signs. GAO's rule also starts 18 px (300 ppi) below the last bar's fill, lower than a chart axis line sits. |
| Placed each text element on its measured baseline, then moved it by the offset that best matched its ink to the source in a 300 dpi render, 1 to 5 px (under 1.2 pt). | LibreOffice sets baselines a little lower than the font-metric model used to place them. The offsets are the NUDGE table in src/build-faithful.js, and the result is in data/fit-offsets.json. |
| Added a slide footer: the source line and 'Portfolio reconstruction of a public GAO figure. Not a GAO product.' | Every rebuilt slide carries it, so the slide cannot pass for a GAO product. |

## Kept

| What | Why |
|---|---|
| GAO's order (largest planned total first), all 24 names as printed, every dollar total and every percent label. | These are the figure's content. Each value was read in four passes and matches data/figure1.csv, and the inspector compares the chart, its embedded workbook and the table with that file. |
| Colors from the figure's pixels: O&M #409993, DME #99CCFF, band gray #D7D7D7, black text and outlines. | The PDF holds the figure as an indexed-color image, so these are its exact palette values. |
| GAO's type and lines: caption Arial Bold 9 pt, band heading 9 pt bold, $105,136 at 10 pt bold, totals 8 pt bold, names 7 pt bold, percent labels 7 pt, source line 6 pt, 0.5 pt outlines and a 1.9 pt axis rule. | Measured on the 300 ppi figure from cap heights and word widths, and from the PDF's text layer for the caption, where the word 'Figure' is 27.56 pt wide, the width of 9 pt Arial Bold. |
| The caption, the legend's two definitions and the source line, word for word. | They carry the figure's title and its definitions of DME and O&M. |

## Rejected

| What | Why |
|---|---|
| Putting the totals into the chart's category labels. | PowerPoint sets category labels in one style, right-aligned against the axis, so names could not sit left-aligned at the figure's edge with bold totals in their own right-aligned column. |
| A 25th chart category for the top band. | It would force the band to the agency bars' height and spacing. |
| Tracing over a pasted copy of the source image, or keeping any picture on the slide. | Everything on the slide is a native, editable object. The inspector fails any slide that holds a picture, and its test proves that it does. |
| Two tables with different row pitches, to follow GAO's dollar column exactly. | GAO's totals run on a slightly longer pitch than its bars. With one table on the bars' pitch, the row 1 total sits 3 px low and the row 24 total 4 px high at 300 ppi (about 1 pt), while names stay within 1 px. One table keeps the slide simple. |
| Moving the chart's inside labels by hand to match GAO's padding. | LibreOffice places inside-end labels 3 to 5 px (300 ppi) closer to the segment end than GAO did. Hand-placed labels would stop following the data. |

## Flagged

| What | Evidence |
|---|---|
| The figure prints 79% for O&M, and the exact share is 78.78%. | $82,828M / $105,136M = 78.78% (checks.md). GAO's text rounds it the same way: 'about $83 billion (79 percent)' (PDF p. 10, printed p. 4). |
| Ties in the printed shares cannot be ordered from the figure. | GAO drew every bar from its rounded percent (all 24 within 0.07 points, checks.md), so Defense, Interior and the Nuclear Regulatory Commission at 83%, for example, carry no finer detail. |
| The published PDF and PNG use Liberation Sans where the .pptx names Arial. | pdffonts lists only LiberationSans and LiberationSans-Bold in both PDFs. LibreOffice substitutes this metric-compatible font, so widths and line breaks hold and glyph shapes differ slightly. |
| No step in this build opened the file in Microsoft PowerPoint. | The .pptx comes from PptxGenJS 4.0.1 and is checked with python-pptx 1.0.2, and File > Info in PowerPoint will name PptxGenJS. Renders, the overlay and every position calibration come from LibreOffice, so text positions in PowerPoint are unchecked. |

## Checks

| Check | Result |
|---|---|
| Transcription in four passes: the PDF image by eye (A), GAO's web JPEG by eye in reverse order (B), tesseract OCR (C) and the sources agent's sheet, opened last (D) | 75 values compared, 1 disagreement: OCR read row 2's O&M label as 21%. A 6x zoom shows 91%, and the DME label beside it is 9% (data/transcription/compare.md). Passes A and B were read by the same agent, so C and D are the independent ones. |
| 24 agency totals against the printed total | Sum $105,136M equals the printed $105,136M. |
| O&M and DME shares | $82,828M / $105,136M = 78.78%, printed 79%. $22,308M = 21.22%, printed 21%. The two add to $105,136M. |
| Rounding of each agency's shares | All 24 rows add to 100. The rounded shares imply $82,847.15M of O&M against the printed $82,828M, inside the +/-$525.68M that whole-percent rounding allows. |
| Bar lengths against their labels | All 24 bars measure within 0.07 points of their printed percents at 300 ppi (checks.md). |
| Order | Totals strictly decrease down the figure. The closest pairs, Energy with Agriculture and USAID with EPA, are each $1M apart. |
| Inspector (python-pptx) on faithful.pptx | 19 of 19 checks pass: one native 100% stacked bar chart, chart values and embedded workbook equal to the CSV, table equal to the CSV, outside labels, no pictures, Arial only, footer present. A test builds broken decks and each one fails. |
| Overlay on the published figure | RMSE 0.1425 on the figure at 300 dpi (the source image at its native resolution), 0.1387 at 96 dpi and 0.0908 for the whole slide, where 0 means identical. Bar outlines and dividers land within 1 px at 300 ppi. |

Portfolio reconstruction of a public GAO figure. Not a GAO product.
