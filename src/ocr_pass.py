"""Pass C of the Figure 1 transcription: a machine read with tesseract OCR.

It finds the 24 bar rows and the top band by scanning one pixel column for the
O&M teal, then OCRs the dollar total and the two percent labels in each row.
Raw OCR strings are kept next to the parsed values, so a misread stays visible.

Usage: python3 src/ocr_pass.py <figure1.png> <out.csv>
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

TEAL = (64, 153, 147)  # O&M fill, sampled from the figure
SCAN_X = 900           # inside the teal part of every bar (the smallest O&M share is 60%)
DOLLAR_X = (678, 823)  # dollar column
BAR_X = (838, 1500)    # bars plus the outside labels at the right edge


def column_colors(png: Path, x: int) -> list[tuple[int, int, int]]:
    out = subprocess.run(
        ["magick", str(png), "-crop", f"1x100000+{x}+0", "+repage", "-depth", "8", "rgb:-"],
        capture_output=True, check=True,
    ).stdout
    return [tuple(out[i:i + 3]) for i in range(0, len(out), 3)]


def teal_runs(colors: list[tuple[int, int, int]], min_len: int = 30) -> list[tuple[int, int]]:
    runs, start = [], None
    for y, c in enumerate(colors + [(255, 255, 255)]):
        if c == TEAL and start is None:
            start = y
        elif c != TEAL and start is not None:
            if y - start >= min_len:
                runs.append((start, y - 1))
            start = None
    return runs


def ocr(png: Path, box: tuple[int, int, int, int], psm: int, chars: str) -> str:
    x0, y0, x1, y1 = box
    # Crops go to the repo's ignored scratch folder: tesseract could not read crops from the system temp dir here.
    scratch = Path(__file__).resolve().parent.parent / "scratch" / "ocr"
    scratch.mkdir(parents=True, exist_ok=True)
    crop = scratch / f"crop-{x0}-{y0}.png"
    subprocess.run(
        ["magick", str(png), "-crop", f"{x1 - x0}x{y1 - y0}+{x0}+{y0}", "+repage",
         "-colorspace", "Gray", "-threshold", "35%", "-bordercolor", "white", "-border", "20", str(crop)],
        check=True,
    )
    out = subprocess.run(
        ["tesseract", str(crop), "stdout", "--psm", str(psm), "-c", f"tessedit_char_whitelist={chars}"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
    ).stdout
    return out.decode("utf-8", errors="replace").strip()


def main() -> None:
    png, out_csv = Path(sys.argv[1]), Path(sys.argv[2])
    runs = teal_runs(column_colors(png, SCAN_X))
    if len(runs) != 26:  # band, 24 bars, legend swatch
        raise SystemExit(f"expected 26 teal runs (band, 24 bars, legend), found {len(runs)}")
    band, bars = runs[0], runs[1:25]
    rows = []

    band_text = ocr(png, (1175, band[0] - 4, 1455, band[1] + 4), 6, "0123456789%$,")
    total_text = ocr(png, (DOLLAR_X[0], band[0] - 4, DOLLAR_X[1], band[1] + 4), 7, "0123456789$,")
    pcts = re.findall(r"(\d+)%", band_text)
    rows.append({
        "row": 0, "y_fill": f"{band[0]}-{band[1]}", "ocr_total": total_text, "ocr_bar_labels": band_text.replace("\n", " / "),
        "total_musd": total_text.replace("$", "").replace(",", ""),
        "om_pct": pcts[0] if len(pcts) > 0 else "", "dme_pct": pcts[1] if len(pcts) > 1 else "",
    })

    for i, (y0, y1) in enumerate(bars, start=1):
        total_text = ocr(png, (DOLLAR_X[0], y0 - 2, DOLLAR_X[1], y1 + 3), 7, "0123456789$,")
        label_text = ocr(png, (BAR_X[0], y0 + 2, BAR_X[1], y1 - 1), 7, "0123456789%")
        pcts = re.findall(r"(\d+)%", label_text)
        rows.append({
            "row": i, "y_fill": f"{y0}-{y1}", "ocr_total": total_text, "ocr_bar_labels": label_text,
            "total_musd": total_text.replace("$", "").replace(",", ""),
            "om_pct": pcts[0] if len(pcts) > 0 else "", "dme_pct": pcts[1] if len(pcts) > 1 else "",
        })

    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out_csv} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
