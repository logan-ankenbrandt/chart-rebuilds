"""Write data/figure1.csv from the reconciled transcription (pass A, after data/transcription/compare.md).

Every value in the output was printed on GAO-25-107795 Figure 1. Nothing is computed into it.
The *_from columns say where on the figure each value is printed.

Usage: python3 src/make_figure1_csv.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = "GAO-25-107795 Figure 1, PDF p. 11 (printed p. 5)"

# Short labels for the redesign slide. They are not printed on the figure.
REDESIGN_LABEL = {
    "Department of Defense": "Defense",
    "Department of Homeland Security": "Homeland Security",
    "Department of Health and Human Services": "Health and Human Services",
    "Department of the Treasury": "Treasury",
    "Department of Veterans Affairs": "Veterans Affairs",
    "Department of Transportation": "Transportation",
    "Department of Justice": "Justice",
    "Department of Energy": "Energy",
    "Department of Agriculture": "Agriculture",
    "Department of Commerce": "Commerce",
    "Department of State": "State",
    "National Aeronautics and Space Administration": "NASA",
    "Social Security Administration": "Social Security Administration",
    "Department of the Interior": "Interior",
    "Department of Education": "Education",
    "General Services Administration": "General Services Administration",
    "Department of Labor": "Labor",
    "Department of Housing and Urban Development": "Housing and Urban Development",
    "Office of Personnel Management": "Office of Personnel Management",
    "U.S. Agency for International Development": "USAID",
    "Environmental Protection Agency": "Environmental Protection Agency",
    "Small Business Administration": "Small Business Administration",
    "National Science Foundation": "National Science Foundation",
    "Nuclear Regulatory Commission": "Nuclear Regulatory Commission",
}

OUTSIDE_DME_LABEL = {"Department of Housing and Urban Development", "Small Business Administration"}


def main() -> None:
    with (ROOT / "data" / "transcription" / "pass-a.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    out_rows = []
    for r in rows:
        order = int(r["row"])
        if order == 0:
            out_rows.append({
                "order": 0,
                "agency": "All 24 agencies (top band)",
                "redesign_label": "",
                "total_musd": r["total_musd"],
                "om_pct": r["om_pct"],
                "dme_pct": r["dme_pct"],
                "om_musd": 82828,
                "dme_musd": 22308,
                "total_from": f"{FIG}, top band, 'Total planned spending for fiscal year 2025 (in millions)'",
                "om_from": f"{FIG}, top band, O&M segment ($82,828 over 79%)",
                "dme_from": f"{FIG}, top band, DME segment ($22,308 over 21%)",
                "reading": "passes A, B, C and D agree",
            })
            continue
        agency = r["agency"]
        out_rows.append({
            "order": order,
            "agency": agency,
            "redesign_label": REDESIGN_LABEL[agency],
            "total_musd": r["total_musd"],
            "om_pct": r["om_pct"],
            "dme_pct": r["dme_pct"],
            "om_musd": "",
            "dme_musd": "",
            "total_from": f"{FIG}, row {order}, dollar column",
            "om_from": f"{FIG}, row {order}, label inside the O&M segment",
            "dme_from": f"{FIG}, row {order}, label "
            + ("outside the bar, right of 100" if agency in OUTSIDE_DME_LABEL else "inside the DME segment"),
            "reading": "passes A, B and D agree; OCR read 21%, 6x zoom shows 91%" if order == 2
            else "passes A, B, C and D agree",
        })
    with (ROOT / "data" / "figure1.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote data/figure1.csv ({len(out_rows)} rows: the top band and {len(out_rows) - 1} agencies)")


if __name__ == "__main__":
    main()
