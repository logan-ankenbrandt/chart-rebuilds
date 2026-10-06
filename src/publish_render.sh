#!/usr/bin/env bash
# Copy a rendered deck's PDF into the repo and rasterize it at exactly 1280 x 720 (96 dpi for a 13.333 x 7.5 in slide).
# LibreOffice writes the page as 960.009 x 540 pt, so a plain 96 dpi render rounds up to 1281 px wide.
# Usage: src/publish_render.sh <render-dir> <name> <dest-dir>   (after _tools/render.sh wrote <render-dir>/<name>.pdf)
set -euo pipefail
src="$1/$2.pdf"
dest="$3"
mkdir -p "$dest"
cp "$src" "$dest/$2.pdf"
pdftoppm -png -singlefile -scale-to-x 1280 -scale-to-y 720 "$dest/$2.pdf" "$dest/$2"
magick identify -format '%f %wx%h\n' "$dest/$2.png"
