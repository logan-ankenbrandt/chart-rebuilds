// Faithful rebuild of GAO-25-107795 Figure 1 on a 16:9 slide.
// One native 100% stacked bar chart (data embedded) plus a native table for the names and dollar totals.
// Every position below is a pixel measured on the 1500 x 1896 figure (300 ppi, printed 5.0 in wide),
// mapped to the slide at the same physical size, so point sizes match the report page.
//
// Usage: node src/build-faithful.js   ->   slides/figure1/faithful.pptx
const path = require('path');
const PptxGenJS = require('pptxgenjs');
const { ROOT, loadFigure1, dollars, writeDeck, chartPart } = require('./lib');

const { band, agencies } = loadFigure1();

// Figure pixels to slide inches. The figure's left edge is centered on the 13.333 in slide.
const PPI = 300;
// The origin is centered and lands on whole pixels at both 96 and 300 dpi, so renders compare pixel for pixel.
const FIG_X = 50 / 12; // 4.1667 in: (13.333 - 5.0) / 2
const FIG_Y = 8 / 12; // 0.6667 in
const RULE_TOP = FIG_Y - 0.482; // on the report page the thick rule starts 0.482 in above the figure image
const X = (px) => FIG_X + px / PPI;
const Y = (px) => FIG_Y + px / PPI;
const L = (px) => px / PPI; // a length

// Colors sampled from the figure's pixels (magick, exact palette values of the PDF image).
const OM = '409993';
const DME = '99CCFF';
const BAND = 'D7D7D7';
const INK = '000000';
const LINE_PT = 0.5; // bar and band outlines are 2 px at 300 ppi, about 0.5 pt

// Bar geometry, measured from line centers: bar 1 spans y 150 to 199, bars repeat every 60.609 px,
// and every bar spans x 835.0 (0%) to 1454.1 (100%).
const PITCH = (1546 - 152) / 23;
const BAR_H = 49;
const GAP = PITCH - BAR_H;
const PLOT_TOP = 150 - GAP / 2;
const PLOT_LEFT = 835.0;
const PLOT_RIGHT = 1454.1;
const BAND_TOP = 26.75;
const BAND_BOTTOM = 122.8;

// Text sits on measured baselines. A top-anchored box with zero insets puts the first baseline one ascent
// (0.905 em for Arial) below its top edge.
const ASC = 0.905;
const topForBaseline = (baselinePx, pt) => Y(baselinePx) - (ASC * pt) / 72;

// Calibration against the LibreOffice render (src/fit_offsets.py on a 300 dpi render): LibreOffice sets these
// lines 1 to 5 px (under 1.2 pt) away from where the ascent model puts them. [dx, dy] in figure px, right and down.
const NUDGE = {
  bandLabel: [0, 1], bandTotal: [2, -5], bandOmUsd: [2, -3], bandOmPct: [1, -2], bandDmeUsd: [3, -3], bandDmePct: [2, -2],
  table: [1.5, 0], outside: [0, -3.5], axisNumbers: [0, -2], axisTitle: [1, -2], legend: [1, -2], sourceLine: [1, -2],
};
const N = (key, i) => NUDGE[key][i];

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Logan Ankenbrandt';
pptx.title = 'GAO-25-107795 Figure 1, faithful rebuild';
pptx.subject = 'Portfolio reconstruction of a public GAO figure. Not a GAO product.';

const slide = pptx.addSlide();
slide.background = { color: 'FFFFFF' };
const text = (t, o) => slide.addText(t, { fontFace: 'Arial', color: INK, margin: 0, valign: 'top', wrap: false, ...o });
const rect = (x0, y0, x1, y1, fill, outline) => slide.addShape(pptx.ShapeType.rect, {
  x: X(x0), y: Y(y0), w: L(x1 - x0), h: L(y1 - y0),
  fill: { color: fill },
  line: outline ? { color: INK, width: LINE_PT } : { type: 'none' },
});

// Report caption block: the thick rule (page x 2.98 in to 8.005 in, 0.085 in tall) and the 9 pt bold caption.
slide.addShape(pptx.ShapeType.rect, {
  x: FIG_X - 0.02 + L(2), y: RULE_TOP, w: 5.025, h: 0.085, fill: { color: INK }, line: { type: 'none' }, // +2 px: calibration
});
text([
  { text: 'Figure 1: Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year', options: { breakLine: true } },
  { text: '2025, in millions of dollars' },
], {
  // caption baselines sit 0.2737 in and 0.1345 in above the figure image (page words at y 174.1 pt and 184.1 pt)
  x: FIG_X, y: FIG_Y - 0.2737 - 8.0 / 72 - L(1), w: 5.0, h: 0.3, fontSize: 9, bold: true, lineSpacing: 10, // -1 px: calibration
});

// Top band: gray label area, then the overall O&M and DME bar drawn at the printed 79% and 21%.
rect(0, BAND_TOP, PLOT_LEFT, BAND_BOTTOM, BAND, false);
for (const y of [BAND_TOP, BAND_BOTTOM]) {
  slide.addShape(pptx.ShapeType.line, { x: X(0), y: Y(y), w: L(PLOT_LEFT), h: 0, line: { color: INK, width: LINE_PT } });
}
const bandDivider = PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * (band.om / 100);
rect(PLOT_LEFT, BAND_TOP, bandDivider, BAND_BOTTOM, OM, true);
rect(bandDivider, BAND_TOP, PLOT_RIGHT, BAND_BOTTOM, DME, true);
text([
  { text: 'Total planned spending for', options: { breakLine: true } },
  { text: 'fiscal year 2025 (in millions)' },
], { x: X(9.5 + N('bandLabel', 0)), y: topForBaseline(67 + N('bandLabel', 1), 9), w: L(560), h: L(90), fontSize: 9, bold: true, lineSpacing: 9.84 });
text(dollars(band.total), { x: X(560 + N('bandTotal', 0)), y: topForBaseline(87 + N('bandTotal', 1), 10), w: L(813 - 560), h: L(45), fontSize: 10, bold: true, align: 'right' });
text(dollars(band.omUsd), { x: X(1100 + N('bandOmUsd', 0)), y: topForBaseline(72 + N('bandOmUsd', 1), 8), w: L(1307 - 1100), h: L(36), fontSize: 8, bold: true, align: 'right' });
text(`${band.om}%`, { x: X(1100 + N('bandOmPct', 0)), y: topForBaseline(105 + N('bandOmPct', 1), 7), w: L(1307 - 1100), h: L(32), fontSize: 7, align: 'right' });
text(dollars(band.dmeUsd), { x: X(1310 + N('bandDmeUsd', 0)), y: topForBaseline(72 + N('bandDmeUsd', 1), 8), w: L(1448 - 1310), h: L(36), fontSize: 8, bold: true, align: 'right' });
text(`${band.dme}%`, { x: X(1310 + N('bandDmePct', 0)), y: topForBaseline(105 + N('bandDmePct', 1), 7), w: L(1442 - 1310), h: L(32), fontSize: 7, align: 'right' });

// Names and dollar totals: one native table whose rows share the chart's category pitch.
// The figure sets these baselines about 5 px lower than a vertically centered line would sit.
const TABLE_SHIFT = 5.2;
slide.addTable(
  agencies.map((a) => [
    { text: a.agency, options: { bold: true, fontSize: 7, align: 'left' } },
    { text: dollars(a.total), options: { bold: true, fontSize: 8, align: 'right' } },
  ]),
  {
    // h: without it the table's frame records 1 in, not the 24 rows' height.
    x: X(8 + N('table', 0)), y: Y(PLOT_TOP + TABLE_SHIFT + N('table', 1)), w: L(813 - 8), h: L(24 * PITCH), colW: [L(680 - 8), L(813 - 680)],
    rowH: agencies.map(() => L(PITCH)), margin: 0, valign: 'middle', fontFace: 'Arial', color: INK,
    border: { type: 'none' }, fill: { color: 'FFFFFF', transparency: 100 },
  },
);

// The chart: 24 categories in the figure's order, top to bottom, two series of printed percents.
const CHART = { left: 820, right: 1500, top: 130, bottom: 1605 };
const CHART_DY = 1; // calibration: LibreOffice drew the bars 1 px high
const cw = CHART.right - CHART.left;
const ch = CHART.bottom - CHART.top;
slide.addChart(pptx.ChartType.bar, [
  { name: 'O&M', labels: agencies.map((a) => a.agency), values: agencies.map((a) => a.om) },
  { name: 'DME', labels: agencies.map((a) => a.agency), values: agencies.map((a) => a.dme) },
], {
  x: X(CHART.left), y: Y(CHART.top + CHART_DY), w: L(cw), h: L(ch),
  layout: { x: (PLOT_LEFT - CHART.left) / cw, y: (PLOT_TOP - CHART.top) / ch, w: (PLOT_RIGHT - PLOT_LEFT) / cw, h: (24 * PITCH) / ch },
  barDir: 'bar', barGrouping: 'percentStacked', barGapWidthPct: Math.round((100 * GAP) / BAR_H),
  chartColors: [OM, DME], dataBorder: { pt: LINE_PT, color: INK },
  catAxisOrientation: 'maxMin', catAxisHidden: true, valAxisHidden: true,
  valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, showLegend: false,
  showValue: true, dataLabelPosition: 'inEnd', dataLabelFormatCode: '0"%"',
  dataLabelFontFace: 'Arial', dataLabelFontSize: 7, dataLabelColor: INK,
  chartArea: { fill: { color: 'FFFFFF', transparency: 100 } }, plotArea: { fill: { color: 'FFFFFF', transparency: 100 } },
});

// Two DME labels sit outside their bars on the figure (HUD 3%, SBA 5%). The chart's own labels for those
// points are switched off in the chart XML below, and these text boxes carry the printed values instead.
const OUTSIDE = agencies.filter((a) => ['Department of Housing and Urban Development', 'Small Business Administration'].includes(a.agency));
for (const a of OUTSIDE) {
  const center = PLOT_TOP + (a.order - 0.5) * PITCH; // bar center
  text(`${a.dme}%`, { x: X(1455.8 + N('outside', 0)), y: topForBaseline(center + 12.4 + N('outside', 1), 7), w: L(44), h: L(32), fontSize: 7 });
}

// Axis: the thick rule under the bars (8 px, about 1.9 pt), the 0 to 100 numbers and the axis title.
slide.addShape(pptx.ShapeType.rect, { x: X(835.5), y: Y(1610), w: L(620), h: L(8), fill: { color: INK }, line: { type: 'none' } });
for (let k = 0; k <= 10; k++) {
  const cx = 834.5 + k * 62.0;
  text(String(k * 10), { x: X(cx - 30 + N('axisNumbers', 0)), y: topForBaseline(1671 + N('axisNumbers', 1), 7), w: L(60), h: L(32), fontSize: 7, bold: true, align: 'center' });
}
text('Percent of DME and O&M spending', { x: X(835.8 + N('axisTitle', 0)), y: topForBaseline(1720 + N('axisTitle', 1), 7), w: L(560), h: L(32), fontSize: 7, bold: true });

// Legend and source line.
rect(8, 1771, 107.8, 1819, DME, true);
// The figure sets each legend's '=' in bold and the rest in regular weight.
const legend = (key, rest) => [{ text: `${key} ` }, { text: '=', options: { bold: true } }, { text: ` ${rest}` }];
text(legend('DME', 'development, modernization, and enhancement'), { x: X(131.8 + N('legend', 0)), y: topForBaseline(1802 + N('legend', 1), 7), w: L(730), h: L(32), fontSize: 7 });
rect(872, 1771, 971.8, 1819, OM, true);
text(legend('O&M', 'operations and maintenance'), { x: X(997.6 + N('legend', 0)), y: topForBaseline(1802 + N('legend', 1), 7), w: L(490), h: L(32), fontSize: 7 });
text('Source: GAO analysis of IT Dashboard data.  |  GAO-25-107795', { x: X(3.8 + N('sourceLine', 0)), y: topForBaseline(1870 + N('sourceLine', 1), 6), w: L(760), h: L(28), fontSize: 6 });

// Slide footer, outside the figure. The figure fills the slide height at its printed size (its source line ends
// near y 6.92 in), so the footer takes the next 0.3 in and leaves a 0.28 in bottom margin, not the redesign's 0.5 in.
const FOOT = { y: 7.0, h: 0.22, fontSize: 10, color: '595959', valign: 'top' };
text('Source: GAO-25-107795, Figure 1, printed page 5 (July 2025). Rebuilt as a native PowerPoint chart with embedded data.',
  { x: 0.5, w: 7.6, ...FOOT });
text('Portfolio reconstruction of a public GAO figure. Not a GAO product.', { x: 8.3, w: 4.533, align: 'right', ...FOOT });

slide.addNotes([
  'Faithful rebuild of GAO-25-107795, Figure 1, "Planned IT Spending, as Reported on the IT Dashboard for Fiscal Year 2025, in millions of dollars" (PDF page 11, printed page 5).',
  'The bars are one native 100% stacked bar chart. Right-click it and choose Edit Data to see the 48 printed percents. Names and totals are a native table with the same row pitch as the chart.',
  'Every value is in data/figure1.csv with where it was printed. Checks are in checks.md: the 24 totals sum to $105,136 million, and $82,828 million is 78.78%, printed as 79%.',
  'Portfolio reconstruction of a public GAO figure. Not a GAO product. GAO: "This is a work of the U.S. government and is not subject to copyright protection in the United States."',
].join('\n\n'));

const out = path.join(ROOT, 'slides', 'figure1', 'faithful.pptx');
writeDeck(pptx, out, async (zip) => {
  const { name, xml } = await chartPart(zip);
  const series = xml.split('<c:ser>');
  if (series.length !== 3) throw new Error('expected two series in the chart');
  const off = OUTSIDE.map((a) => `<c:dLbl><c:idx val="${a.order - 1}"/><c:delete val="1"/></c:dLbl>`).join('');
  series[2] = series[2].replace('<c:dLbls>', `<c:dLbls>${off}`);
  zip.file(name, series.join('<c:ser>'));
}).then((f) => console.log('wrote', path.relative(ROOT, f)));
