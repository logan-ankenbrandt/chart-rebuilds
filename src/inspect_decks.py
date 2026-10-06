"""Inspect both decks with python-pptx and compare every charted value with data/figure1.csv.

For each deck it checks that the slide has exactly one native chart of the expected type with an embedded
workbook, that the chart's cached values AND the embedded workbook's cells match the CSV, that the slide
holds no picture (so nothing is a pasted screenshot), that every font is Arial, that every shape sits on
the slide, that the footer is present, and that no text carries a dash character or a banned word.
The faithful deck's table and outside labels are checked against the CSV too.

Usage: python3 src/inspect_decks.py [deck-folder]   (exits non-zero on any failure; writes data/inspect.json
for the repo's own decks only)
"""

import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pptx import Presentation
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE_TYPE

from writing_rules import violations

ROOT = Path(__file__).resolve().parent.parent
DECKS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "slides" / "figure1"  # a folder holding faithful.pptx and redesign.pptx
FOOTER = "Portfolio reconstruction of a public GAO figure. Not a GAO product."
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def load_csv() -> list[dict]:
    with (ROOT / "data" / "figure1.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r["order"] != "0"]


def workbook_columns(blob: bytes) -> dict[str, list]:
    """Column letter -> cell values (rows 2 and down) of the chart's embedded workbook."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = ["".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")) for si in root.findall("m:si", NS)]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cols: dict[str, list] = {}
    for c in sheet.iter(f"{{{NS['m']}}}c"):
        ref = c.get("r")
        col, row = re.match(r"([A-Z]+)(\d+)", ref).groups()
        v = c.find("m:v", NS)
        if v is None or int(row) < 2:
            continue
        value = shared[int(v.text)] if c.get("t") == "s" else float(v.text)
        cols.setdefault(col, []).append(value)
    return cols


def all_text(slide) -> list[str]:
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text)
        if shape.has_table:
            texts += [cell.text for row in shape.table.rows for cell in row.cells]
    if slide.has_notes_slide:
        texts.append(slide.notes_slide.notes_text_frame.text)
    return texts


def inspect(deck: Path, expected_type, categories: list[str], series: dict[str, list[int]], results: list) -> None:
    prs = Presentation(str(deck))
    slide = prs.slides[0]
    name = deck.name

    def check(what: str, ok: bool, detail: str) -> None:
        results.append({"deck": name, "check": what, "ok": bool(ok), "detail": detail})

    check("one slide, 16:9", len(prs.slides) == 1 and round(prs.slide_width / prs.slide_height, 3) == round(16 / 9, 3),
          f"{len(prs.slides)} slide, {prs.slide_width / 914400:.3f} x {prs.slide_height / 914400:.3f} in")
    charts = [s for s in slide.shapes if s.has_chart]
    check("exactly one native chart", len(charts) == 1, f"{len(charts)} chart graphic frame(s)")
    chart = charts[0].chart
    check("chart type", chart.chart_type == expected_type, f"{chart.chart_type} (expected {expected_type})")
    plot = chart.plots[0]
    cats = [str(c) for c in plot.categories]
    check("categories match data/figure1.csv", cats == categories, f"{len(cats)} categories in the expected order")
    for s in plot.series:
        want = series.get(s.name)
        got = [int(v) for v in s.values]
        check(f"series '{s.name}' values match the CSV", want == got, f"{len(got)} values" + ("" if want == got else f": got {got}, want {want}"))
    check("series names", sorted(s.name for s in plot.series) == sorted(series), ", ".join(s.name for s in plot.series))

    wb = chart.part.chart_workbook.xlsx_part
    check("embedded workbook present", wb is not None and len(wb.blob) > 0, f"{len(wb.blob):,} bytes" if wb else "missing")
    cols = workbook_columns(wb.blob)
    wb_cats = [str(v) for v in cols.get("A", [])]
    check("workbook categories match the CSV", wb_cats == categories, f"column A has {len(wb_cats)} rows")
    for i, s in enumerate(plot.series):
        col = chr(ord("B") + i)
        got = [int(v) for v in cols.get(col, [])]
        check(f"workbook column {col} ('{s.name}') matches the CSV", got == series[s.name], f"{len(got)} values")

    pics = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE]
    check("no pictures on the slide", not pics, f"{len(pics)} picture(s)")
    off = [s.name for s in slide.shapes
           if s.left < 0 or s.top < 0 or s.left + s.width > prs.slide_width or s.top + s.height > prs.slide_height]
    check("every shape inside the slide", not off, ", ".join(off) or "all inside")

    with zipfile.ZipFile(deck) as z:
        xml = "".join(z.read(n).decode("utf-8") for n in z.namelist()
                      if re.match(r"ppt/(slides/slide\d+|charts/chart\d+)\.xml$", n))
    faces = set(re.findall(r'<a:latin typeface="([^"]+)"', xml))
    check("only Arial", faces == {"Arial"}, ", ".join(sorted(faces)))

    texts = all_text(slide)
    check("footer present", any(FOOTER in t for t in texts), FOOTER)
    hits = sorted({v for t in texts for v in violations(t)})
    check("no dash characters or banned words in slide text and notes", not hits, ", ".join(hits) or "none")
    return slide, chart


def main() -> int:
    rows = load_csv()
    results: list = []

    # Faithful: the figure's order, two series of printed percents.
    order = [r["agency"] for r in rows]
    slide, chart = inspect(DECKS / "faithful.pptx", XL_CHART_TYPE.BAR_STACKED_100, order,
                           {"O&M": [int(r["om_pct"]) for r in rows], "DME": [int(r["dme_pct"]) for r in rows]}, results)
    tables = [s for s in slide.shapes if s.has_table]
    table_rows = [[c.text for c in row.cells] for row in tables[0].table.rows] if tables else []
    want_rows = [[r["agency"], f"${int(r['total_musd']):,}"] for r in rows]
    results.append({"deck": "faithful.pptx", "check": "table names and totals match the CSV", "ok": table_rows == want_rows,
                    "detail": f"{len(table_rows)} rows x 2 columns"})
    outside = {r["agency"]: f"{r['dme_pct']}%" for r in rows
               if r["agency"] in ("Department of Housing and Urban Development", "Small Business Administration")}
    boxes = [s.text_frame.text for s in slide.shapes if s.has_text_frame]
    results.append({"deck": "faithful.pptx", "check": "outside DME labels carry the printed values",
                    "ok": all(boxes.count(v) >= 1 for v in outside.values()), "detail": ", ".join(outside.values())})
    xml = chart.part.blob.decode("utf-8")
    deleted = re.findall(r'<c:dLbl><c:idx val="(\d+)"/><c:delete val="1"/></c:dLbl>', xml)
    want_deleted = [str(int(r["order"]) - 1) for r in rows if r["agency"] in outside]
    results.append({"deck": "faithful.pptx", "check": "chart labels switched off only where text boxes replace them",
                    "ok": deleted == want_deleted, "detail": f"point indexes {', '.join(deleted)}"})

    # Redesign: sorted by O&M share, ties by total, one series.
    ranked = sorted(rows, key=lambda r: (-int(r["om_pct"]), -int(r["total_musd"])))
    slide, chart = inspect(DECKS / "redesign.pptx", XL_CHART_TYPE.BAR_CLUSTERED, [r["redesign_label"] for r in ranked],
                           {"O&M share of planned FY2025 IT spending": [int(r["om_pct"]) for r in ranked]}, results)
    xml = chart.part.blob.decode("utf-8")
    shown = re.findall(r'<c:dLbl><c:idx val="(\d+)"/>.*?<c:showVal val="1"/>', xml)
    series_off = re.search(r'</c:dLbl><c:numFmt[^>]*/>.*?<c:showVal val="0"/>', xml, re.S) is not None
    labeled = [f"{ranked[int(i)]['redesign_label']} {ranked[int(i)]['om_pct']}%" for i in shown]
    results.append({"deck": "redesign.pptx", "check": "value labels only on the five extremes",
                    "ok": shown == ["0", "1", "2", "22", "23"] and series_off, "detail": "; ".join(labeled)})

    width = max(len(r["check"]) for r in results)
    for r in results:
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['deck']:14s} {r['check']:{width}s}  {r['detail']}")
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)} of {len(results)} inspector checks pass")
    if len(sys.argv) == 1:
        (ROOT / "data" / "inspect.json").write_text(json.dumps(
            {"passed": len(results) - len(failed), "total": len(results), "results": results}, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
