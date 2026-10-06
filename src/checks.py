"""Arithmetic and pixel checks for GAO-25-107795 Figure 1. Writes checks.md and data/checks.json.

Every number here comes from data/figure1.csv (values printed on the figure) or from
pixels of source/gao-25-107795-figure1-masked-1500x1896.png. Exits non-zero if a check fails.

Usage: python3 src/checks.py
"""

import csv
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURE = ROOT / "source" / "gao-25-107795-figure1-masked-1500x1896.png"
W, H = 1500, 1896
TEAL, BLUE = (64, 153, 147), (153, 204, 255)  # O&M and DME fills, sampled from the figure
SCAN_X = 900  # inside the teal part of every bar


def load_rows() -> tuple[dict, list[dict]]:
    with (ROOT / "data" / "figure1.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    band = rows[0]
    agencies = [
        {"order": int(r["order"]), "agency": r["agency"], "label": r["redesign_label"],
         "total": int(r["total_musd"]), "om": int(r["om_pct"]), "dme": int(r["dme_pct"])}
        for r in rows[1:]
    ]
    return band, agencies


def pixels() -> list[tuple[int, int, int]]:
    raw = subprocess.run(["magick", str(FIGURE), "-depth", "8", "rgb:-"], capture_output=True, check=True).stdout
    return [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]


def runs_of(seq: list, value) -> list[tuple[int, int]]:
    runs, start = [], None
    for i, v in enumerate(seq + [None]):
        if v == value and start is None:
            start = i
        elif v != value and start is not None:
            runs.append((start, i - 1))
            start = None
    return runs


def bar_share(px: list, y: int) -> float:
    """O&M share of one drawn bar, between line centers, from the pure-fill runs along row y."""
    row = px[y * W:(y + 1) * W]
    teal = max(runs_of(row, TEAL), key=lambda r: r[1] - r[0])
    blue = max(runs_of(row, BLUE), key=lambda r: r[1] - r[0])
    half_line = (blue[0] - teal[1]) / 2  # the three lines (left edge, divider, right edge) are drawn alike
    left, divider, right = teal[0] - half_line, teal[1] + half_line, blue[1] + half_line
    return 100 * (divider - left) / (right - left)


def main() -> int:
    band, ag = load_rows()
    results, failures = [], []

    def check(name: str, ok: bool, detail: str) -> None:
        results.append({"check": name, "ok": ok, "detail": detail})
        if not ok:
            failures.append(name)

    records = []

    def record(name: str, detail: str) -> None:
        """A fact the logs cite. Not counted as a check, because it cannot fail."""
        records.append({"fact": name, "detail": detail})

    total, om_usd, dme_usd = int(band["total_musd"]), int(band["om_musd"]), int(band["dme_musd"])
    om_pct_band, dme_pct_band = int(band["om_pct"]), int(band["dme_pct"])
    n = len(ag)
    check("24 agency rows", n == 24, f"{n} agency rows in data/figure1.csv")

    s = sum(a["total"] for a in ag)
    check("Agency totals sum to the printed total", s == total,
          f"sum of the 24 printed totals = ${s:,}M; printed total = ${total:,}M; difference {s - total}")

    check("O&M plus DME equals the printed total", om_usd + dme_usd == total,
          f"${om_usd:,}M + ${dme_usd:,}M = ${om_usd + dme_usd:,}M; printed total ${total:,}M")

    om_share = 100 * om_usd / total
    dme_share = 100 * dme_usd / total
    check("O&M share rounds to the printed 79%", round(om_share) == om_pct_band,
          f"{om_usd:,} / {total:,} = {om_share:.2f}%, printed {om_pct_band}%")
    check("DME share rounds to the printed 21%", round(dme_share) == dme_pct_band,
          f"{dme_usd:,} / {total:,} = {dme_share:.2f}%, printed {dme_pct_band}%")

    bad = [a["agency"] for a in ag if a["om"] + a["dme"] != 100]
    check("Each agency's two printed shares add to 100", not bad,
          "all 24 rows add to 100" if not bad else "rows that do not: " + "; ".join(bad))

    weighted = sum(a["total"] * a["om"] for a in ag) / 100
    slack = sum(a["total"] * 0.5 for a in ag) / 100
    check("Rounded agency shares are consistent with the printed O&M dollars",
          abs(weighted - om_usd) <= slack,
          f"sum of total x printed O&M% = ${weighted:,.2f}M against printed ${om_usd:,}M "
          f"(difference {weighted - om_usd:+,.2f}); whole-percent rounding allows up to +/-${slack:,.2f}M")

    # Order of the figure: by total, largest first.
    totals = [a["total"] for a in ag]
    strictly = all(totals[i] > totals[i + 1] for i in range(n - 1))
    gaps = sorted((totals[i] - totals[i + 1], ag[i]["agency"], ag[i + 1]["agency"]) for i in range(n - 1))
    closest = "; ".join(f"{a} and {b}, ${g:,}M apart" for g, a, b in gaps[:2])
    check("Figure order is by total, largest first, with no ties", strictly,
          f"totals strictly decrease down the figure; closest pairs: {closest}")

    # Bars measured in pixels against their printed labels.
    px = pixels()
    col = [px[y * W + SCAN_X] for y in range(H)]
    fills = [r for r in runs_of(col, TEAL) if r[1] - r[0] >= 30]
    check("Teal runs found: band, 24 bars, legend swatch", len(fills) == 26, f"{len(fills)} teal runs down x = {SCAN_X}")
    band_bar = bar_share(px, fills[0][0] + 4)
    measured = [bar_share(px, f[0] + 4) for f in fills[1:25]]
    dev = [m - a["om"] for m, a in zip(measured, ag)]
    worst = max(range(n), key=lambda i: abs(dev[i]))
    check("Every bar matches its printed O&M label", max(abs(d) for d in dev) <= 0.5,
          f"largest gap {dev[worst]:+.2f} points ({ag[worst]['agency']}); limit 0.5")
    check("Bars are drawn from the rounded percents", max(abs(d) for d in dev) <= 0.15,
          f"all 24 bars sit within {max(abs(d) for d in dev):.2f} points of their printed whole percent, "
          f"so the drawing carries no sub-percent detail that could order ties")
    check("Top band bar is drawn at the printed 79%", abs(band_bar - om_pct_band) <= 0.15,
          f"band bar measures {band_bar:.2f}%; the exact share {om_share:.2f}% would sit "
          f"{(band_bar - om_share) * 619 / 100:.1f} px to the left at the figure's 300 ppi")

    # Redesign order: O&M share, highest first; ties keep the figure's order (largest total first).
    ranked = sorted(ag, key=lambda a: (-a["om"], -a["total"]))
    ties = {}
    for a in ag:
        ties.setdefault(a["om"], []).append(a)
    tie_groups = {k: v for k, v in ties.items() if len(v) > 1}
    tie_text = "; ".join(
        f"{k}%: " + ", ".join(f"{a['label']} (${a['total']:,}M)" for a in sorted(v, key=lambda a: -a["total"]))
        for k, v in sorted(tie_groups.items(), reverse=True)
    )
    fig_pos = {a["agency"]: i for i, a in enumerate(ag)}
    rank_pos = {a["agency"]: i for i, a in enumerate(ranked)}
    kept = all(
        sorted(g, key=lambda a: fig_pos[a["agency"]]) == sorted(g, key=lambda a: rank_pos[a["agency"]])
        for g in tie_groups.values()
    )
    check("Ties keep the figure's order in the redesign", kept,
          f"{len(tie_groups)} tie groups, each in the same order as on the figure (largest total first): {tie_text}")

    top3, bottom2 = ranked[:3], ranked[-2:]
    shares = [a["om"] for a in ag]
    median = statistics.median(shares)
    mean = statistics.mean(shares)
    above = sum(1 for x in shares if x > om_pct_band)
    at = sum(1 for x in shares if x == om_pct_band)
    below = sum(1 for x in shares if x < om_pct_band)
    expected = [("Housing and Urban Development", 97), ("Small Business Administration", 95), ("Homeland Security", 91),
                ("Treasury", 61), ("Transportation", 60)]
    got = [(a["label"], a["om"]) for a in top3 + bottom2]
    check("Extremes match the ones the redesign labels", got == expected,
          "highest: " + ", ".join(f"{a['label']} {a['om']}%" for a in top3)
          + "; lowest: " + ", ".join(f"{a['label']} {a['om']}%" for a in bottom2)
          + ("" if got == expected else f" (expected {expected})"))
    record("Spread around the overall share",
           f"{above} agencies above 79%, {at} at 79%, {below} below; median of the 24 shares {median:g}%, "
           f"unweighted mean {mean:.2f}%, dollar-weighted share {om_share:.2f}%")

    # Report text against the figure (quotes verified in source/gao-25-107795-quotes.md).
    check("Report text matches the figure", round(om_usd / 1000) == 83 and om_pct_band == 79 and dme_pct_band == 21,
          f"PDF p. 10 says 'about $83 billion (79 percent)' and footnote 11 says 'The other 21 percent'; "
          f"the figure prints ${om_usd:,}M (79%) and ${dme_usd:,}M (21%)")

    lines = [
        "# Checks: GAO-25-107795 Figure 1",
        "",
        "Generated by `src/checks.py` from `data/figure1.csv` (values printed on the figure) and the pixels of "
        "`source/gao-25-107795-figure1-masked-1500x1896.png`. Rerun it after any change to the data.",
        "",
        f"Result: {len(results) - len(failures)} of {len(results)} checks pass.",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    lines += [f"| {r['check']} | {'pass' if r['ok'] else 'FAIL'} | {r['detail']} |" for r in results]
    lines += ["", "## Recorded facts", "", "These are cited by the logs. They are not counted as checks.", "",
              "| Fact | Detail |", "|---|---|"]
    lines += [f"| {r['fact']} | {r['detail']} |" for r in records]
    lines += [
        "",
        "## Bar pixels, row by row",
        "",
        "Method: along the row 4 px below the top of each bar's fill (above the labels), the pure O&M and DME fill runs "
        "are found, and the three lines (left edge, divider, right edge) are placed half a line width outside them. "
        "Share = (divider - left) / (right - left). One pixel is 0.16 points.",
        "",
        "| Row | Agency | Printed O&M | Measured | Gap |",
        "|---|---|---|---|---|",
    ]
    lines += [f"| {a['order']} | {a['agency']} | {a['om']}% | {m:.2f}% | {m - a['om']:+.2f} |" for a, m in zip(ag, measured)]
    lines += [
        "",
        "## Redesign order",
        "",
        "Sorted by printed O&M share, highest first. Ties keep the figure's own order, which is by total, largest first, "
        "because the printed whole percents and the bars cannot rank them.",
        "",
        "| Rank | Agency | O&M | Total ($M) |",
        "|---|---|---|---|",
    ]
    lines += [f"| {i} | {a['label']} | {a['om']}% | {a['total']:,} |" for i, a in enumerate(ranked, start=1)]
    lines.append("")
    (ROOT / "checks.md").write_text("\n".join(lines))

    summary = {
        "sum_of_totals": s, "printed_total": total, "om_musd": om_usd, "dme_musd": dme_usd,
        "om_share_exact": round(om_share, 2), "dme_share_exact": round(dme_share, 2),
        "weighted_om_from_rounded": round(weighted, 2), "rounding_slack": round(slack, 2),
        "bar_max_gap": round(max(abs(d) for d in dev), 2), "band_bar": round(band_bar, 2),
        "median_share": median, "mean_share": round(mean, 2), "above": above, "at": at, "below": below,
        "ranked": [a["agency"] for a in ranked], "passed": len(results) - len(failures), "total_checks": len(results),
    }
    (ROOT / "data" / "checks.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"{len(results) - len(failures)} of {len(results)} checks pass -> checks.md, data/checks.json")
    for f in failures:
        print("FAIL:", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
