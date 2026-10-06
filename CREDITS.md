# Credits

## Source

| Field | Value |
|---|---|
| Title | Information Technology: Agencies Need to Plan for Modernizing Critical Decades-Old Legacy Systems |
| Author | U.S. Government Accountability Office (GAO) |
| Agency | GAO, report to the Committee on Oversight and Government Reform, House of Representatives |
| Date | July 17, 2025 |
| ID | GAO-25-107795 |
| Used | Figure 1, "Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year 2025, in millions of dollars" (PDF page 11, printed page 5), and quoted text from PDF pages 2, 7 and 10 |
| URL | https://www.gao.gov/products/gao-25-107795 |
| License line | "This is a work of the U.S. government and is not subject to copyright protection in the United States. The published product may be reproduced and distributed in its entirety without further permission from GAO. However, because this work may contain copyrighted images or other material, permission from the copyright holder may be necessary if you wish to reproduce this material separately." (report page iii) |
| Left out | The report cover and the Highlights page images, which carry the GAO logo, and the Figure 2 photograph. No GAO logo or photograph appears anywhere in this repo. |

Figure 1 is a chart GAO drew from IT Dashboard data. Its source line reads "Source: GAO analysis of IT Dashboard data. | GAO-25-107795". File details and hashes are in [`source/SOURCE.md`](source/SOURCE.md).

Credit line used on the slides: "Source: GAO-25-107795, Figure 1 (July 2025)". Footer on every rebuilt slide: "Portfolio reconstruction of a public GAO figure. Not a GAO product."

This work is not affiliated with or endorsed by GAO.

## Software

| Tool | Used for | License |
|---|---|---|
| PptxGenJS 4.0.1 | Generating both decks | MIT |
| JSZip 3.10 | Editing chart XML that PptxGenJS cannot express | MIT or GPLv3 (dual) |
| python-pptx 1.0.2 | Inspecting the decks | MIT |
| LibreOffice 26.8 | Rendering the decks to PDF | MPL 2.0 |
| Poppler (pdftoppm, pdffonts) | Rasterizing PDFs and listing their fonts | GPL |
| ImageMagick 7 | Crops, measurements, blends and RMSE | ImageMagick License |
| Tesseract | Transcription pass C (OCR) | Apache 2.0 |

None of these tools is distributed in this repo.
