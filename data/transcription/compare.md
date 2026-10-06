# Figure 1 transcription: four passes compared

Every printed value in GAO-25-107795 Figure 1 (PDF page 11, printed page 5) was read four times:

| Pass | File | Method |
|---|---|---|
| A | `pass-a.csv` | Read by eye from the 1500 x 1896 image embedded in the report PDF, in full-resolution strips, top to bottom. |
| B | `pass-b.csv` | Read by eye from GAO's 600 x 759 web JPEG (a separate raster), upscaled 3x, one column at a time (dollars, then bars, then names), bottom to top. |
| C | `pass-c-ocr.csv` | tesseract OCR of the 1500 x 1896 image, one row at a time (`src/ocr_pass.py`). Raw OCR text is kept in the file. |
| D | `pass-d-sources-agent.csv` | The sources agent's separate transcription, opened only after A, B and C were saved. |

Limit on independence: passes A and B were read by the same agent in one session, so B is a second reading from a different file in a different order, not a second person. Passes C and D do not depend on that agent's reading.

Values compared: 75 (25 rows, the total band and 24 agencies, with 3 values each). Disagreements: 1. Unresolved: 0.

| Row | Value | A | B | C | D | Kept | Evidence |
|---|---|---|---|---|---|---|---|
| 2 | O&M % | 91 | 91 | 21 | 91 | 91 | OCR read '21%'. A 6x zoom of the label (crop 140 x 56 at x 1300, y 207, point filter) shows '91%'. The DME label beside it reads 9%, and 91 + 9 = 100. |

The band's dollar values ($82,828 for O&M and $22,308 for DME) were read the same way in passes A, B and C (C's raw OCR text: `$82,828$22,308 / 79%21%`).
