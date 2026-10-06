"""Measure how far each element of the faithful rebuild sits from the same element in the source figure.

Both images must be the figure at 300 ppi and the same size (1500 x 1896): the source is the PDF's
embedded image, the rebuild is a 300 dpi render of faithful.pdf cropped at the figure origin
(x 1250, y 200). For each named region, the script finds the shift (dx, dy) within +/-8 px that best
lands the rebuild's ink on the source's ink, and the share of source ink pixels covered at that shift.
A shift of (0, 0) means the element is where GAO drew it.

Usage: python3 src/fit_offsets.py <source.png> <rebuild.png> [out.json]
"""

import json
import subprocess
import sys

W, H = 1500, 1896

REGIONS = {
    "band label, line 1": (10, 36, 500, 70),
    "band label, line 2": (10, 78, 510, 118),
    "band total $105,136": (640, 50, 815, 96),
    "band O&M $82,828": (1185, 42, 1310, 78),
    "band O&M 79%": (1245, 80, 1310, 108),
    "band DME $22,308": (1328, 42, 1450, 78),
    "band DME 21%": (1383, 80, 1445, 108),
    "band bar outline": (830, 20, 1200, 130),
    "row 1 bar outline": (830, 145, 1200, 205),
    "row 1 divider": (1340, 147, 1362, 203),
    "row 24 bar outline": (830, 1540, 1200, 1600),
    "row 24 divider": (1340, 1542, 1362, 1598),
    "row 1 name": (8, 160, 330, 200),
    "row 1 total": (690, 160, 815, 200),
    "row 1 O&M label": (1200, 158, 1345, 190),
    "row 1 DME label": (1355, 158, 1450, 190),
    "row 12 name": (8, 826, 670, 868),
    "row 12 total": (690, 827, 815, 868),
    "row 12 O&M label": (1220, 825, 1370, 858),
    "row 24 name": (8, 1556, 460, 1596),
    "row 24 total": (690, 1554, 815, 1596),
    "row 24 O&M label": (1200, 1553, 1345, 1586),
    "HUD 3% (outside)": (1455, 1190, 1497, 1222),
    "SBA 5% (outside)": (1455, 1433, 1497, 1465),
    "axis rule": (830, 1605, 1460, 1622),
    "axis numbers": (825, 1645, 1480, 1675),
    "axis title": (835, 1695, 1325, 1728),
    "legend": (0, 1765, 1470, 1825),
    "source line": (3, 1848, 716, 1876),
}


def gray(path: str) -> bytes:
    raw = subprocess.run(["magick", path, "-colorspace", "Gray", "-depth", "8", "gray:-"],
                         capture_output=True, check=True).stdout
    if len(raw) != W * H:
        raise SystemExit(f"{path} is not {W} x {H}")
    return raw


def best_shift(src: bytes, reb: bytes, box: tuple[int, int, int, int], reach: int = 8) -> tuple[int, int, float]:
    x0, y0, x1, y1 = box
    ink = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if src[y * W + x] < 90]
    best = (-1, 0, 0)
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            hits = sum(1 for x, y in ink if reb[(y + dy) * W + x + dx] < 90)
            if hits > best[0]:
                best = (hits, dx, dy)
    return best[1], best[2], best[0] / len(ink)


def main() -> None:
    src, reb = gray(sys.argv[1]), gray(sys.argv[2])
    print(f"{'element':24s} {'dx':>4s} {'dy':>4s}  covered")
    found = {}
    for name, box in REGIONS.items():
        dx, dy, cover = best_shift(src, reb, box)
        found[name] = {"dx": dx, "dy": dy, "covered": round(cover, 2)}
        print(f"{name:24s} {dx:4d} {dy:4d}  {cover:.2f}")
    if len(sys.argv) > 3:
        with open(sys.argv[3], "w") as f:
            json.dump(found, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
