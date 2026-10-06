"""Compare the four transcriptions of GAO-25-107795 Figure 1, value by value.

Pass A: read by eye from the 1500 x 1896 PDF image, top to bottom.
Pass B: read by eye from GAO's 600 x 759 web JPEG, column by column, bottom to top.
Pass C: tesseract OCR of the 1500 x 1896 image (src/ocr_pass.py).
Pass D: the sources agent's separate transcription, opened only after A, B and C were saved.

Writes data/transcription/compare.md and exits non-zero if a disagreement has no
recorded resolution in RESOLVED below.

Usage: python3 src/compare_passes.py
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "data" / "transcription"

PASSES = {
    "A": (T / "pass-a.csv", {"total": "total_musd", "om": "om_pct", "dme": "dme_pct"}),
    "B": (T / "pass-b.csv", {"total": "total_musd", "om": "om_pct", "dme": "dme_pct"}),
    "C": (T / "pass-c-ocr.csv", {"total": "total_musd", "om": "om_pct", "dme": "dme_pct"}),
    "D": (T / "pass-d-sources-agent.csv", {"total": "total_musd_printed", "om": "om_pct_printed", "dme": "dme_pct_printed"}),
}

# Every disagreement must be listed here with the value kept and the evidence for it.
RESOLVED = {
    (2, "om"): (
        "91",
        "OCR read '21%'. A 6x zoom of the label (crop 140 x 56 at x 1300, y 207, point filter) shows '91%'. "
        "The DME label beside it reads 9%, and 91 + 9 = 100.",
    ),
}

FIELDS = {"total": "total ($M)", "om": "O&M %", "dme": "DME %"}


def load(path: Path, cols: dict[str, str]) -> dict[int, dict[str, str]]:
    with path.open(newline="") as f:
        return {int(r["row"]): {k: r[v].strip() for k, v in cols.items()} for r in csv.DictReader(f)}


def main() -> int:
    data = {name: load(path, cols) for name, (path, cols) in PASSES.items()}
    rows = sorted(data["A"])
    disagreements, unresolved = [], []
    compared = 0
    for row in rows:
        for field in FIELDS:
            values = {name: data[name][row][field] for name in data}
            compared += 1
            if len(set(values.values())) > 1:
                fix = RESOLVED.get((row, field))
                disagreements.append((row, field, values, fix))
                if fix is None:
                    unresolved.append((row, field, values))

    lines = [
        "# Figure 1 transcription: four passes compared",
        "",
        "Every printed value in GAO-25-107795 Figure 1 (PDF page 11, printed page 5) was read four times:",
        "",
        "| Pass | File | Method |",
        "|---|---|---|",
        "| A | `pass-a.csv` | Read by eye from the 1500 x 1896 image embedded in the report PDF, in full-resolution strips, top to bottom. |",
        "| B | `pass-b.csv` | Read by eye from GAO's 600 x 759 web JPEG (a separate raster), upscaled 3x, one column at a time (dollars, then bars, then names), bottom to top. |",
        "| C | `pass-c-ocr.csv` | tesseract OCR of the 1500 x 1896 image, one row at a time (`src/ocr_pass.py`). Raw OCR text is kept in the file. |",
        "| D | `pass-d-sources-agent.csv` | The sources agent's separate transcription, opened only after A, B and C were saved. |",
        "",
        "Limit on independence: passes A and B were read by the same agent in one session, so B is a second reading from a different file in a different order, not a second person. Passes C and D do not depend on that agent's reading.",
        "",
        f"Values compared: {compared} (25 rows, the total band and 24 agencies, with 3 values each). "
        f"Disagreements: {len(disagreements)}. Unresolved: {len(unresolved)}.",
        "",
    ]
    if disagreements:
        lines += ["| Row | Value | A | B | C | D | Kept | Evidence |", "|---|---|---|---|---|---|---|---|"]
        for row, field, values, fix in disagreements:
            kept, why = fix if fix else ("UNRESOLVED", "")
            lines.append(
                f"| {row} | {FIELDS[field]} | {values['A']} | {values['B']} | {values['C']} | {values['D']} | {kept} | {why} |"
            )
        lines.append("")
    lines += [
        "The band's dollar values ($82,828 for O&M and $22,308 for DME) were read the same way in passes A, B and C "
        "(C's raw OCR text: `$82,828$22,308 / 79%21%`).",
        "",
    ]
    out = T / "compare.md"
    out.write_text("\n".join(lines))
    (T / "compare.json").write_text(json.dumps({
        "values_compared": compared, "disagreements": len(disagreements), "unresolved": len(unresolved),
        "resolved": [{"row": r, "value": FIELDS[f], "passes": v, "kept": fix[0], "evidence": fix[1]}
                     for r, f, v, fix in disagreements if fix],
    }, indent=2) + "\n")
    print(f"compared {compared} values: {len(disagreements)} disagreements, {len(unresolved)} unresolved -> {out.relative_to(ROOT)}")
    for row, field, values in unresolved:
        print(f"UNRESOLVED row {row} {field}: {values}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
