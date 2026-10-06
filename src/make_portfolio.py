"""Write the two slide logs (Markdown) and portfolio.json from one place, so they cannot disagree.

Numbers come from the recorded check outputs in data/ (checks.json, overlay.json, inspect.json,
reference-line.json, fit-offsets.json, transcription/compare.json), not retyped. The script fails if
any path portfolio.json names is missing.

Usage: python3 src/make_portfolio.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load(name: str) -> dict:
    return json.loads((D / name).read_text())


chk = load("checks.json")
ovl = load("overlay.json")
ins = load("inspect.json")
ref = load("reference-line.json")
fit = load("fit-offsets.json")
cmp_ = load("transcription/compare.json")

money = lambda n: f"${n:,}M"
deck_checks = lambda deck: [r for r in ins["results"] if r["deck"] == deck]
f_ins, r_ins = deck_checks("faithful.pptx"), deck_checks("redesign.pptx")
passed = lambda rs: sum(1 for r in rs if r["ok"])
total_dy = [fit[f"row {n} total"]["dy"] for n in (1, 12, 24)]
label_dx = [fit[f"row {n} O&M label"]["dx"] for n in (1, 12, 24)]
bar_fit = [fit[k] for k in ("band bar outline", "row 1 bar outline", "row 1 divider", "row 24 bar outline", "row 24 divider")]
bar_px = max(max(abs(b["dx"]), abs(b["dy"])) for b in bar_fit)
fix = cmp_["resolved"][0]

HOW_MADE = ("Claude Code agents rebuilt this GAO figure from the source image as editable PowerPoint and drafted the logs. "
            "I chose the source, set the rules each rebuild follows, and checked every slide, number and log before publishing.")
SOURCE = {
    "image": "slides/figure1/source.png",
    "title": "Figure 1: Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year 2025, in millions of dollars",
    "credit": "U.S. Government Accountability Office, GAO-25-107795 (July 17, 2025), Figure 1",
    "url": "https://www.gao.gov/products/gao-25-107795",
    "license": "Work of the U.S. government, not subject to copyright protection in the United States (report page iii).",
    "page": "PDF page 11 (printed page 5)",
}
NOT_POWERPOINT = {
    "what": "No step in this build opened the file in Microsoft PowerPoint.",
    "evidence": "The .pptx comes from PptxGenJS 4.0.1 and is checked with python-pptx 1.0.2, and File > Info in PowerPoint "
                "will name PptxGenJS. Renders, the overlay and every position calibration come from LibreOffice, so text "
                "positions in PowerPoint are unchecked.",
}
FONTS = {
    "what": "The published PDF and PNG use Liberation Sans where the .pptx names Arial.",
    "evidence": "pdffonts lists only LiberationSans and LiberationSans-Bold in both PDFs. LibreOffice substitutes this "
                "metric-compatible font, so widths and line breaks hold and glyph shapes differ slightly.",
}

FAITHFUL_LOG = {
    "changed": [
        {"what": "Moved GAO's report figure onto a 16:9 slide at its printed size, 5.0 by 6.32 in, centered, with the report's caption and rule above it.",
         "why": "The source is a portrait figure on a report page. At its printed size the rebuild keeps GAO's point sizes and fits the 7.5 in slide height, so nothing is rescaled."},
        {"what": "Rebuilt the 24 bars as one native 100% stacked bar chart whose embedded data are the 48 printed percents.",
         "why": f"A native chart opens in Edit Data, so every value can be checked in PowerPoint. GAO drew each bar from its rounded percent (all 24 bars measure within {chk['bar_max_gap']} points of their labels), so charting the printed percents reproduces the drawing."},
        {"what": "Set the agency names and dollar totals in a native two-column table whose 24 rows share the chart's row pitch of 0.202 in.",
         "why": "A table keeps all 48 cells in one editable object and lines each row up with its bar by construction. A text column would have meant 24 or 48 loose text boxes to keep in line."},
        {"what": "Drew the top band (the gray label area, the overall O&M and DME bar and its five values) with shapes and text boxes.",
         "why": f"The band is about twice as tall as an agency bar and sits apart from the rows, so it cannot be a 25th category of the same chart. Its divider sits at the printed 79%, where GAO drew it: the band's bar measures {chk['band_bar']:.2f}%."},
        {"what": "Set the two DME labels that sit outside their bars (Housing and Urban Development 3%, Small Business Administration 5%) as text boxes, and switched off the chart's own labels for those two points.",
         "why": "PowerPoint stores a moved data label as an offset from its default spot, and LibreOffice computes that spot differently, so a moved label would land in different places in the two programs. The inspector checks both text boxes against the CSV."},
        {"what": "Drew the axis rule, the numbers 0 to 100 and the axis title as a shape and text boxes in place of the chart's own axis.",
         "why": "A 100% stacked chart's axis prints 0% to 100%, and GAO prints the numbers without percent signs. GAO's rule also starts 18 px (300 ppi) below the last bar's fill, lower than a chart axis line sits."},
        {"what": "Placed each text element on its measured baseline, then moved it by the offset that best matched its ink to the source in a 300 dpi render, 1 to 5 px (under 1.2 pt).",
         "why": "LibreOffice sets baselines a little lower than the font-metric model used to place them. The offsets are the NUDGE table in src/build-faithful.js, and the result is in data/fit-offsets.json."},
        {"what": "Added a slide footer: the source line and 'Portfolio reconstruction of a public GAO figure. Not a GAO product.'",
         "why": "Every rebuilt slide carries it, so the slide cannot pass for a GAO product."},
    ],
    "kept": [
        {"what": "GAO's order (largest planned total first), all 24 names as printed, every dollar total and every percent label.",
         "why": "These are the figure's content. Each value was read in four passes and matches data/figure1.csv, and the inspector compares the chart, its embedded workbook and the table with that file."},
        {"what": "Colors from the figure's pixels: O&M #409993, DME #99CCFF, band gray #D7D7D7, black text and outlines.",
         "why": "The PDF holds the figure as an indexed-color image, so these are its exact palette values."},
        {"what": "GAO's type and lines: caption Arial Bold 9 pt, band heading 9 pt bold, $105,136 at 10 pt bold, totals 8 pt bold, names 7 pt bold, percent labels 7 pt, source line 6 pt, 0.5 pt outlines and a 1.9 pt axis rule.",
         "why": "Measured on the 300 ppi figure from cap heights and word widths, and from the PDF's text layer for the caption, where the word 'Figure' is 27.56 pt wide, the width of 9 pt Arial Bold."},
        {"what": "The caption, the legend's two definitions and the source line, word for word.",
         "why": "They carry the figure's title and its definitions of DME and O&M."},
    ],
    "rejected": [
        {"what": "Putting the totals into the chart's category labels.",
         "why": "PowerPoint sets category labels in one style, right-aligned against the axis, so names could not sit left-aligned at the figure's edge with bold totals in their own right-aligned column."},
        {"what": "A 25th chart category for the top band.",
         "why": "It would force the band to the agency bars' height and spacing."},
        {"what": "Tracing over a pasted copy of the source image, or keeping any picture on the slide.",
         "why": "Everything on the slide is a native, editable object. The inspector fails any slide that holds a picture, and its test proves that it does."},
        {"what": "Two tables with different row pitches, to follow GAO's dollar column exactly.",
         "why": f"GAO's totals run on a slightly longer pitch than its bars. With one table on the bars' pitch, the row 1 total sits {total_dy[0]} px low and the row 24 total {abs(total_dy[2])} px high at 300 ppi (about 1 pt), while names stay within 1 px. One table keeps the slide simple."},
        {"what": "Moving the chart's inside labels by hand to match GAO's padding.",
         "why": f"LibreOffice places inside-end labels {min(label_dx)} to {max(label_dx)} px (300 ppi) closer to the segment end than GAO did. Hand-placed labels would stop following the data."},
    ],
    "flagged": [
        {"what": "The figure prints 79% for O&M, and the exact share is 78.78%.",
         "evidence": f"{money(chk['om_musd'])} / {money(chk['printed_total'])} = {chk['om_share_exact']}% (checks.md). GAO's text rounds it the same way: 'about $83 billion (79 percent)' (PDF p. 10, printed p. 4)."},
        {"what": "Ties in the printed shares cannot be ordered from the figure.",
         "evidence": f"GAO drew every bar from its rounded percent (all 24 within {chk['bar_max_gap']} points, checks.md), so Defense, Interior and the Nuclear Regulatory Commission at 83%, for example, carry no finer detail."},
        FONTS,
        NOT_POWERPOINT,
    ],
    "checks": [
        {"what": "Transcription in four passes: the PDF image by eye (A), GAO's web JPEG by eye in reverse order (B), tesseract OCR (C) and the sources agent's sheet, opened last (D)",
         "result": f"{cmp_['values_compared']} values compared, {cmp_['disagreements']} disagreement: OCR read row {fix['row']}'s O&M label as {fix['passes']['C']}%. A 6x zoom shows {fix['kept']}%, and the DME label beside it is 9% (data/transcription/compare.md). Passes A and B were read by the same agent, so C and D are the independent ones."},
        {"what": "24 agency totals against the printed total",
         "result": f"Sum {money(chk['sum_of_totals'])} equals the printed {money(chk['printed_total'])}."},
        {"what": "O&M and DME shares",
         "result": f"{money(chk['om_musd'])} / {money(chk['printed_total'])} = {chk['om_share_exact']}%, printed 79%. {money(chk['dme_musd'])} = {chk['dme_share_exact']}%, printed 21%. The two add to {money(chk['printed_total'])}."},
        {"what": "Rounding of each agency's shares",
         "result": f"All 24 rows add to 100. The rounded shares imply ${chk['weighted_om_from_rounded']:,}M of O&M against the printed {money(chk['om_musd'])}, inside the +/-${chk['rounding_slack']:,}M that whole-percent rounding allows."},
        {"what": "Bar lengths against their labels",
         "result": f"All 24 bars measure within {chk['bar_max_gap']} points of their printed percents at 300 ppi (checks.md)."},
        {"what": "Order",
         "result": "Totals strictly decrease down the figure. The closest pairs, Energy with Agriculture and USAID with EPA, are each $1M apart."},
        {"what": "Inspector (python-pptx) on faithful.pptx",
         "result": f"{passed(f_ins)} of {len(f_ins)} checks pass: one native 100% stacked bar chart, chart values and embedded workbook equal to the CSV, table equal to the CSV, outside labels, no pictures, Arial only, footer present. A test builds broken decks and each one fails."},
        {"what": "Overlay on the published figure",
         "result": f"RMSE {ovl['rmse_figure_300dpi']} on the figure at 300 dpi (the source image at its native resolution), {ovl['rmse_figure_96dpi']} at 96 dpi and {ovl['rmse_slide_96dpi']} for the whole slide, where 0 means identical. Bar outlines and dividers land within {bar_px} px at 300 ppi."},
    ],
}

REDESIGN_LOG = {
    "changed": [
        {"what": "Replaced GAO's figure title with an action title: 'Agencies planned 79% of FY2025 IT spending, about $83 billion, for operations and maintenance'.",
         "why": "A slide read at a distance needs its finding in the title. The numbers and hedges are GAO's: 'about $83 billion (79 percent) in planned total IT spending for fiscal year 2025 was intended for operations and maintenance' (PDF p. 10, printed p. 4)."},
        {"what": "Sorted the 24 agencies by O&M share, highest first, in place of GAO's order by total spending.",
         "why": "The slide compares each agency with the overall share, and a sorted bar chart shows the spread and the extremes at a glance. Agencies with equal shares keep GAO's order, largest total first."},
        {"what": "Plotted one series, the O&M share, on a 0 to 100% axis that starts at zero.",
         "why": "Each agency's two shares add to 100, so the DME bar repeats the same information. One series drops half the ink and the legend, and the zero baseline keeps bar lengths true to the shares."},
        {"what": "Added a reference line at the all-agency share, labeled 'All 24 agencies: 79%'.",
         "why": f"It turns each bar into a comparison with the total. The line sits at the exact share from the printed dollars, 82,828 / 105,136 = {ref['target_pct']}%, and carries GAO's rounded label."},
        {"what": "Labeled values only on the five extremes: Housing and Urban Development 97%, Small Business Administration 95%, Homeland Security 91%, Treasury 61% and Transportation 60%.",
         "why": "These five stand apart from the rest: the next share below 91% is 87%, and the next above 61% is 69%. The gridlines carry the other values, and every value stays in the faithful slide and data/figure1.csv."},
        {"what": "Shortened agency names, for example 'Defense' for 'Department of Defense', 'NASA' and 'USAID'.",
         "why": "Short names fit 24 rows beside the bars. The mapping is the redesign_label column of data/figure1.csv."},
        {"what": "Left out the dollar totals.",
         "why": "The slide carries one message, the share. The totals stay in the faithful slide and the CSV, and the notes column gives the overall $82,828 million of $105,136 million."},
        {"what": "Added a notes column: what the line is, the report's separate 'about 80 percent' statement, and GAO's legacy caveat.",
         "why": "These are the qualifiers a reader needs before repeating the number. Each one cites the report page it comes from."},
        {"what": "Colored the bars #2B5D96 and the line #D55E00 (vermilion).",
         "why": "The dataviz palette validator rated #2F5D8A below its chroma floor (OKLCH chroma 0.089, so it reads gray). #2B5D96 is the nearest blue that passes every check with #D55E00 (data/palette-check.txt)."},
    ],
    "kept": [
        {"what": "GAO's numbers and hedges: 'planned', 'about $83 billion', 79%.",
         "why": "The title claims no more precision or certainty than the report."},
        {"what": "The definitions: operations and maintenance (O&M) spelled out in the subtitle, and the other 21% named as development, modernization and enhancement.",
         "why": "They come from the figure's legend and the report's footnote 11 (PDF p. 10)."},
        {"what": "The scope and source: the 24 CFO Act agencies, GAO-25-107795 Figure 1, GAO analysis of IT Dashboard data.",
         "why": "The scope is from PDF p. 10 and the source line from the figure."},
        {"what": "Arial throughout: title 28 pt, subtitle 16 pt, notes 14 pt, axis numbers 11 pt, source and footer 10 pt.",
         "why": "The deck's type standard, with one exception for the agency names (see Rejected)."},
    ],
    "rejected": [
        {"what": "A dot plot.",
         "why": "Dots would show the same 24 shares, but bars on a 0 to 100% axis read as a share of the whole, which is what the data are, and they keep the zero baseline in view."},
        {"what": "Small multiples.",
         "why": "There is one measure and one comparison. Panels would split the agencies across several plots and repeat the reference line."},
        {"what": "Keeping the 100% stacked bars with DME.",
         "why": "DME is 100 minus O&M on every row, so the second color adds a legend and no information."},
        {"what": "Coloring the five extremes and graying the rest.",
         "why": "It would pull the eye to the extremes and away from the reference line, which carries the title's number. In a sorted chart, position and labels already mark the extremes."},
        {"what": "Value labels on all 24 bars.",
         "why": "A column of 24 numbers competes with the reference line. The faithful slide keeps every value."},
        {"what": "Agency names at 14 pt, the deck's body minimum.",
         "why": "Under a two-line title the 24 rows get 0.179 in each, and 14 pt names would overlap. They are 12 pt, the largest size that keeps them apart. One render at a slightly tighter pitch made LibreOffice drop every other name, so the label interval is now fixed at 1."},
        {"what": "Putting the report's 'about 80 percent' in the title.",
         "why": "That is GAO's general statement about what agencies have typically reported, not the FY2025 plan, and the slide keeps the two numbers apart."},
    ],
    "flagged": [
        {"what": "The report gives two figures for O&M spending: 'about 80 percent' in general and 79% for FY2025 plans.",
         "evidence": "PDF p. 2 and p. 7 (printed p. 1): agencies 'have typically reported spending about 80 percent on operations and maintenance of existing IT'. PDF p. 10 (printed p. 4): 'about $83 billion (79 percent) in planned total IT spending for fiscal year 2025'. The slide uses 79%, and its notes keep the general statement separate."},
        {"what": "O&M spending is not the same as legacy spending.",
         "evidence": "PDF p. 10: 'it is uncertain how much of the operations and maintenance is spent on legacy technology because the Office of Management and Budget (OMB) does not require agencies to include information on whether their investments are considered legacy IT.' The slide's third note keeps this caveat."},
        {"what": "The reference line is a drawn shape, not part of the chart data.",
         "evidence": f"It sits at {ref['target_pct']}% of the plot width and measured {ref['measured_pct']}% in a 300 dpi render (data/reference-line.json). It does not move if the chart data change, and the speaker notes say so."},
        {"what": "Ties are ordered by total spending because the source cannot rank them.",
         "evidence": "Four groups share a printed share: 87% (Veterans Affairs, NASA), 83% (Defense, Interior, Nuclear Regulatory Commission), 79% (Justice, Education) and 72% (General Services Administration, USAID). GAO drew the bars from rounded percents (checks.md)."},
        FONTS,
        NOT_POWERPOINT,
    ],
    "checks": [
        {"what": "Chart values",
         "result": "The chart cache and the embedded workbook equal the printed O&M shares in data/figure1.csv, in the sorted order (inspector)."},
        {"what": "Sort and tie order",
         "result": "4 tie groups, each in GAO's order (checks.md)."},
        {"what": "Extremes",
         "result": "Highest: Housing and Urban Development 97%, Small Business Administration 95%, Homeland Security 91%. Lowest: Treasury 61%, Transportation 60%. Value labels appear on exactly those five (inspector)."},
        {"what": "Reference line position",
         "result": f"{ref['measured_pct']}% of the axis in a 300 dpi render, against a target of {ref['target_pct']}% (data/reference-line.json)."},
        {"what": "Numbers in the title and notes",
         "result": f"'about $83 billion' is {money(chk['om_musd'])} rounded, 79% is {chk['om_share_exact']}% rounded and 21% is {chk['dme_share_exact']}% rounded, as GAO prints them (checks.md)."},
        {"what": "Palette",
         "result": "The dataviz validator passes #2B5D96 with #D55E00 on the lightness band, chroma floor, colorblind separation (delta E 21.3), normal-vision floor and contrast (data/palette-check.txt)."},
        {"what": "Inspector (python-pptx) on redesign.pptx",
         "result": f"{passed(r_ins)} of {len(r_ins)} checks pass: one native bar chart, values and embedded workbook equal to the CSV, labels only on the extremes, no pictures, Arial only, footer present, no dash characters or banned words."},
        {"what": "Render review",
         "result": "All 24 names visible with no overlaps at 96 and 200 dpi, after a render where LibreOffice dropped every other name was fixed."},
    ],
}

ITEMS = [
    {
        "id": "figure1-faithful", "group": "figure1", "kind": "chart-faithful",
        "title": "Faithful rebuild: GAO Figure 1 as a native PowerPoint chart",
        "summary": "GAO's figure of planned FY2025 IT spending for 24 agencies, rebuilt on a 16:9 slide as one native 100% stacked bar chart with the 48 printed percents embedded and a table for names and totals. Laid over the published figure, its bar outlines land within 1 px at 300 ppi.",
        "source": SOURCE,
        "after": {"image": "slides/figure1/faithful.png", "pptx": "slides/figure1/faithful.pptx", "pdf": "slides/figure1/faithful.pdf"},
        "overlay": "slides/figure1/overlay.png",
        "log": FAITHFUL_LOG,
        "logMarkdown": "slides/figure1/log-faithful.md",
    },
    {
        "id": "figure1-redesign", "group": "figure1", "kind": "chart-redesign",
        "title": "Redesign: the same data as an executive slide",
        "summary": "Sorted by operations and maintenance share, with a line at the all-agency 79%, labels on the five extremes, and an action title in GAO's own numbers. Notes keep the report's general 'about 80 percent' and its legacy caveat apart from the FY2025 figure.",
        "source": SOURCE,
        "after": {"image": "slides/figure1/redesign.png", "pptx": "slides/figure1/redesign.pptx", "pdf": "slides/figure1/redesign.pdf"},
        "overlay": None,
        "log": REDESIGN_LOG,
        "logMarkdown": "slides/figure1/log-redesign.md",
    },
]

DOWNLOADS = [
    ("Faithful rebuild (PowerPoint)", "slides/figure1/faithful.pptx"),
    ("Faithful rebuild (PDF)", "slides/figure1/faithful.pdf"),
    ("Redesign (PowerPoint)", "slides/figure1/redesign.pptx"),
    ("Redesign (PDF)", "slides/figure1/redesign.pdf"),
    ("Figure 1 values with where each was printed (CSV)", "data/figure1.csv"),
    ("Arithmetic, rounding and pixel checks", "checks.md"),
]

CREDITS = [
    "GAO, Information Technology: Agencies Need to Plan for Modernizing Critical Decades-Old Legacy Systems, GAO-25-107795 "
    "(Washington, D.C.: July 17, 2025), Figure 1, https://www.gao.gov/products/gao-25-107795. \"This is a work of the U.S. "
    "government and is not subject to copyright protection in the United States.\"",
    "Not affiliated with or endorsed by GAO. The report's cover, the GAO logo and the Figure 2 photograph are not used.",
]


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def log_markdown(item: dict) -> str:
    sections = [("Changed", "changed", "What", "Why", "why"), ("Kept", "kept", "What", "Why", "why"),
                ("Rejected", "rejected", "What", "Why", "why"), ("Flagged", "flagged", "What", "Evidence", "evidence"),
                ("Checks", "checks", "Check", "Result", "result")]
    files = [Path(p).name for p in (item["after"]["pptx"], item["after"]["pdf"], item["after"]["image"]) if p]
    if item["overlay"]:
        files.append(Path(item["overlay"]).name)
    lines = [
        f"# {item['title']}",
        "",
        f"Slide log for item `{item['id']}` ({item['kind']}). Source: GAO-25-107795, \"{SOURCE['title']}\", {SOURCE['page']}. "
        f"Files in this folder: {', '.join(f'`{f}`' for f in files)}.",
        "",
        item["summary"],
        "",
        f"How this was made: {HOW_MADE}",
    ]
    for heading, key, c1, c2, detail in sections:
        lines += ["", f"## {heading}", "", f"| {c1} | {c2} |", "|---|---|"]
        lines += [f"| {cell(e['what'])} | {cell(e[detail])} |" for e in item["log"][key]]
    lines += ["", "Portfolio reconstruction of a public GAO figure. Not a GAO product.", ""]
    return "\n".join(lines)


def main() -> int:
    for item in ITEMS:
        (ROOT / item["logMarkdown"]).write_text(log_markdown(item))
    portfolio = {
        "slug": "chart-rebuilds",
        "title": "Chart Rebuilds: GAO's federal IT spending chart",
        "oneLiner": "A dense GAO chart, 24 agencies with every value printed, rebuilt as a native PowerPoint chart, checked against its own printed totals, then redesigned around its one finding.",
        "repo": "https://github.com/logan-ankenbrandt/chart-rebuilds",
        "order": 3,
        "skills": ["Microsoft PowerPoint", "Slide Reconstruction", "Data Visualization", "Presentation Design",
                   "Visual Storytelling", "Attention to Detail", "Critical Thinking", "Content Editing",
                   "Technical Documentation", "Software Engineering"],
        "howMade": HOW_MADE,
        "cover": "renders/cover.png",
        "items": ITEMS,
        "downloads": [{"label": label, "path": p, "bytes": (ROOT / p).stat().st_size} for label, p in DOWNLOADS],
        "credits": CREDITS,
    }
    (ROOT / "portfolio.json").write_text(json.dumps(portfolio, indent=2, ensure_ascii=False) + "\n")

    paths = [portfolio["cover"]] + [d["path"] for d in portfolio["downloads"]]
    for it in ITEMS:
        paths += [it["source"]["image"], it["after"]["image"], it["after"]["pptx"], it["after"]["pdf"], it["logMarkdown"]]
        if it["overlay"]:
            paths.append(it["overlay"])
    missing = [p for p in paths if p and not (ROOT / p).is_file()]
    print(f"wrote portfolio.json and {len(ITEMS)} logs; {len(set(paths))} referenced paths, {len(missing)} missing")
    for p in missing:
        print("MISSING:", p)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
