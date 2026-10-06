"""Measure where the redesign's reference line landed in the rendered PDF.

Renders slides/figure1/redesign.pdf at 300 dpi, finds the 0% axis line and the 20% to 100% gridlines along a
row that falls between two bars, and reports the line's position as a percent of the axis. The target is the
all-agency share from the printed dollars: 82,828 / 105,136 = 78.78%.

Usage: python3 src/check_reference_line.py   (writes data/reference-line.json; exits non-zero if off by > 0.2 points)
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "slides" / "figure1" / "redesign.pdf"
OUT_PNG = ROOT / "scratch" / "reference-line" / "redesign-300"
W = 4000  # 13.333 in at 300 dpi
GRID = (0xE3, 0xE6, 0xEA)
AXIS = (0x9C, 0xA3, 0xAF)
LINE = (0xD5, 0x5E, 0x00)


def near(c, ref, tol):
    return all(abs(c[i] - ref[i]) <= tol for i in range(3))


def runs(xs):
    out = []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return [(a + b) / 2 for a, b in out]


def main() -> int:
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(PDF), str(OUT_PNG)], check=True)
    raw = subprocess.run(["magick", f"{OUT_PNG}.png", "-depth", "8", "rgb:-"], capture_output=True, check=True).stdout
    px = lambda x, y: tuple(raw[(y * W + x) * 3:(y * W + x) * 3 + 3])
    # A row inside the plot that crosses no bar: white just right of the 0% axis line.
    probe_x = int(3.35 * 300)
    y = next(y for y in range(int(2.3 * 300), int(6.3 * 300)) if px(probe_x, y) == (255, 255, 255))
    row = [px(x, y) for x in range(W)]
    zero = runs([x for x, c in enumerate(row) if near(c, AXIS, 10)])
    grid = runs([x for x, c in enumerate(row) if c == GRID])
    line = runs([x for x, c in enumerate(row) if near(c, LINE, 14)])
    axis0 = [x for x in zero if x > 1000][0]
    per_pct = (grid[-1] - axis0) / 100
    measured = (line[0] - axis0) / per_pct
    with (ROOT / "data" / "figure1.csv").open(newline="") as f:
        band = next(csv.DictReader(f))
    target = 100 * int(band["om_musd"]) / int(band["total_musd"])
    result = {"row_y_px": y, "axis_0_px": axis0, "axis_100_px": grid[-1], "line_px": line[0],
              "measured_pct": round(measured, 2), "target_pct": round(target, 2), "gap_points": round(measured - target, 2)}
    (ROOT / "data" / "reference-line.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return 0 if abs(measured - target) <= 0.2 else 1


if __name__ == "__main__":
    sys.exit(main())
