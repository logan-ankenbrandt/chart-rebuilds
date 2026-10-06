"""Build slides/figure1/source.png and overlay.png, and measure how closely the faithful rebuild matches.

source.png is GAO's figure as published (the PDF's own image plus the caption and rule from the report
page), placed on a blank 16:9 canvas exactly where the faithful slide puts its rebuild, with a credit line.
overlay.png blends the rebuild render over it at 50 percent (the shared _tools/overlay.sh).

RMSE is measured three ways (0 is identical, 1 is opposite): the whole 96 dpi slide, the figure region at
96 dpi, and the figure region at 300 dpi, where the source image is used at its native resolution.

Usage: python3 src/make_overlay.py   (after rendering slides/figure1/faithful.pdf and faithful.png)
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "slides" / "figure1"
SCRATCH = ROOT / "scratch" / "overlay"
FIGURE = ROOT / "source" / "gao-25-107795-figure1-masked-1500x1896.png"
PAGE200 = ROOT / "source" / "gao-25-107795-page-11-masked-200dpi.png"
OVERLAY_SH = ROOT.parent / "_tools" / "overlay.sh"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

# Figure origin on the slide at 300 dpi (4.1667 in, 0.6667 in), as in src/build-faithful.js.
FIG_X300, FIG_Y300 = 1250, 200
# On the report page the figure image starts at 2.6933 in, so page y maps to slide y - 2.0267 in.
PAGE_TO_SLIDE_Y = 2.6933 - 8 / 12
# The credit sits in the empty top-left margin, where the rebuild has nothing, so the overlay keeps both readable.
CREDIT = ("As published in GAO-25-107795 (July 2025),\nFigure 1, printed page 5 (PDF page 11).\n"
          "Work of the U.S. government, not subject\nto copyright in the United States.")


def run(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def rmse(a: Path, b: Path) -> float:
    out = subprocess.run(["compare", "-metric", "RMSE", str(a), str(b), "null:"], capture_output=True, text=True)
    return float(re.search(r"\(([\d.]+)\)", out.stderr).group(1))


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    caption = SCRATCH / "caption-300.png"
    # Rule and caption: page x 2.95 to 8.05 in, y 2.19 to 2.65 in, from the 200 dpi page render, scaled to 300 dpi.
    run("magick", str(PAGE200), "-crop", "1020x92+590+438", "+repage", "-resize", "150%", str(caption))
    cap_x = round((2.95 + 50 / 12 - 3.0) * 300)
    cap_y = round((2.19 - PAGE_TO_SLIDE_Y) * 300)
    canvas300 = SCRATCH / "source-300.png"
    run("magick", "-size", "4000x2250", "xc:white",
        str(FIGURE), "-geometry", f"+{FIG_X300}+{FIG_Y300}", "-composite",
        str(caption), "-geometry", f"+{cap_x}+{cap_y}", "-composite",
        "-font", FONT, "-density", "300", "-pointsize", "10", "-fill", "#595959",
        "-annotate", f"+150+{round(0.5 * 300 + 0.905 * 10 / 72 * 300)}", CREDIT,
        "-alpha", "off", str(canvas300))
    source = OUT / "source.png"
    run("magick", str(canvas300), "-resize", "1280x720!", "-alpha", "off", "-depth", "8", "-strip", str(source))

    render = OUT / "faithful.png"
    overlay = OUT / "overlay.png"
    printed = run("bash", str(OVERLAY_SH), str(source), str(render), str(overlay))
    full96 = float(re.search(r"\(([\d.]+)\)", printed).group(1))
    run("magick", str(overlay), "-depth", "8", "-strip", str(overlay))

    fig_src96, fig_reb96 = SCRATCH / "fig-src-96.png", SCRATCH / "fig-reb-96.png"
    for src, dst in ((source, fig_src96), (render, fig_reb96)):
        run("magick", str(src), "-crop", "480x607+400+64", "+repage", "-alpha", "off", str(dst))
    fig96 = rmse(fig_src96, fig_reb96)

    run("pdftoppm", "-r", "300", "-png", "-singlefile", str(OUT / "faithful.pdf"), str(SCRATCH / "faithful-300"))
    fig_reb300, fig_src300 = SCRATCH / "fig-reb-300.png", SCRATCH / "fig-src-300.png"
    run("magick", str(SCRATCH / "faithful-300.png"), "-crop", f"1500x1896+{FIG_X300}+{FIG_Y300}", "+repage", "-alpha", "off", str(fig_reb300))
    run("magick", str(FIGURE), "-alpha", "off", str(fig_src300))
    fig300 = rmse(fig_src300, fig_reb300)

    result = {"rmse_slide_96dpi": round(full96, 4), "rmse_figure_96dpi": round(fig96, 4), "rmse_figure_300dpi": round(fig300, 4)}
    (ROOT / "data" / "overlay.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
