// Redesign of GAO-25-107795 Figure 1 for a 16:9 executive slide.
// One message under an action title in GAO's own numbers: 79% of planned FY2025 IT spending is for O&M.
// A native bar chart of each agency's O&M share, sorted highest first, a line at the all-agency share,
// and direct labels only on the extremes printed on the figure.
//
// Usage: node src/build-redesign.js   ->   slides/figure1/redesign.pptx
const path = require('path');
const PptxGenJS = require('pptxgenjs');
const { ROOT, loadFigure1, writeDeck, chartPart } = require('./lib');

const { band, agencies } = loadFigure1();

// Sorted by printed O&M share, highest first. Equal shares keep GAO's order (largest total first),
// because the printed whole percents cannot rank them (checks.md).
const ranked = [...agencies].sort((a, b) => b.om - a.om || b.total - a.total);
const EXTREMES = ['Housing and Urban Development', 'Small Business Administration', 'Homeland Security', 'Treasury', 'Transportation'];
const extremeIdx = ranked.map((a, i) => (EXTREMES.includes(a.label) ? i : -1)).filter((i) => i >= 0);
if (extremeIdx.join() !== '0,1,2,22,23') throw new Error(`extremes are not the top 3 and bottom 2: ${extremeIdx}`);

// The all-agency share, from the printed dollars: 82,828 / 105,136 = 78.78%, printed as 79%.
const overall = (100 * band.omUsd) / band.total;

// Design tokens: one light background, one dark ink, a blue for the bars and an orange for the reference line.
// #2B5D96 is the nearest blue to #2F5D8A that passes the dataviz palette validator's chroma floor with #D55E00.
const C = { bg: 'FFFFFF', ink: '1F2933', ink2: '4B5563', muted: '6B7280', grid: 'E3E6EA', axis: '9CA3AF', bar: '2B5D96', accent: 'D55E00' };
const FONT = 'Arial';

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
pptx.author = 'Logan Ankenbrandt';
pptx.title = 'GAO-25-107795 Figure 1, redesigned';
pptx.subject = 'Portfolio reconstruction of a public GAO figure. Not a GAO product.';

const slide = pptx.addSlide();
slide.background = { color: C.bg };
const text = (t, o) => slide.addText(t, { fontFace: FONT, color: C.ink, margin: 0, valign: 'top', ...o });

// Action title and subtitle, 0.5 in margins.
text('Agencies planned 79% of FY2025 IT spending, about $83 billion, for operations and maintenance', {
  x: 0.5, y: 0.4, w: 12.333, h: 0.92, fontSize: 28, bold: true,
});
text("Share of each agency's planned FY2025 IT spending that goes to operations and maintenance (O&M)", {
  x: 0.5, y: 1.42, w: 12.333, h: 0.3, fontSize: 16, color: C.ink2,
});

// Chart frame and plot area (inches). Category labels sit left of the plot inside the frame.
const F = { x: 0.5, y: 1.95, w: 8.75, h: 4.75 };
const P = { left: 3.25, right: 8.45, top: 2.12, bottom: 6.42 }; // plot: 0% at left, 100% at right
slide.addChart(pptx.ChartType.bar, [
  { name: 'O&M share of planned FY2025 IT spending', labels: ranked.map((a) => a.label), values: ranked.map((a) => a.om) },
], {
  x: F.x, y: F.y, w: F.w, h: F.h,
  layout: { x: (P.left - F.x) / F.w, y: (P.top - F.y) / F.h, w: (P.right - P.left) / F.w, h: (P.bottom - P.top) / F.h },
  barDir: 'bar', barGapWidthPct: 70, chartColors: [C.bar],
  catAxisOrientation: 'maxMin', catAxisCrossesAt: 'max', catAxisLabelFrequency: 1, // never skip an agency name
  catAxisLabelFontFace: FONT, catAxisLabelFontSize: 12, catAxisLabelColor: C.ink,
  catAxisLineShow: true, catAxisLineColor: C.axis, catAxisLineSize: 0.75, catAxisMajorTickMark: 'none',
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20, valAxisLabelFormatCode: '0"%"', valAxisLabelPos: 'nextTo',
  valAxisLabelFontFace: FONT, valAxisLabelFontSize: 11, valAxisLabelColor: C.muted,
  valAxisLineShow: false, valAxisMajorTickMark: 'none',
  valGridLine: { color: C.grid, size: 0.75, style: 'solid' }, catGridLine: { style: 'none' },
  showLegend: false, showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0"%"',
  dataLabelFontFace: FONT, dataLabelFontSize: 12, dataLabelFontBold: true, dataLabelColor: C.ink,
  chartArea: { fill: { color: C.bg, transparency: 100 } }, plotArea: { fill: { color: C.bg, transparency: 100 } },
});

// Reference line at the all-agency share, drawn over the plot at the computed position, with a direct label.
const lineX = P.left + ((P.right - P.left) * overall) / 100;
slide.addShape(pptx.ShapeType.line, { x: lineX, y: P.top - 0.06, w: 0, h: P.bottom - P.top + 0.06, line: { color: C.accent, width: 2 } });
text('All 24 agencies: 79%', { x: lineX - 1.2, y: P.top - 0.31, w: 2.4, h: 0.24, fontSize: 12, bold: true, align: 'center' });

// Notes column: what the line is, the separate "about 80 percent" statement, and GAO's legacy caveat.
const NOTE = { x: 9.55, w: 3.283, fontSize: 14, color: C.ink2 };
text(`79% is all 24 agencies combined: $${band.omUsd.toLocaleString('en-US')} million of $${band.total.toLocaleString('en-US')} million (${overall.toFixed(1)}%). The other ${band.dme}% is for development, modernization and enhancement.`,
  { ...NOTE, y: P.top, h: 1.35 });
text('GAO\'s report (page 1) also says agencies have typically reported spending about 80 percent on O&M. That general statement is separate from these FY2025 plans.',
  { ...NOTE, y: 3.65, h: 1.6 });
text('GAO notes it is uncertain how much O&M spending goes to legacy technology (report page 4).',
  { ...NOTE, y: 5.35, h: 0.75 });

// Source line and footer.
const FOOT = { y: 6.78, h: 0.22, fontSize: 10, color: C.muted };
text('Source: GAO-25-107795, Figure 1 (July 2025); GAO analysis of IT Dashboard data, 24 CFO Act agencies.', { x: 0.5, w: 7.4, ...FOOT });
text('Portfolio reconstruction of a public GAO figure. Not a GAO product.', { x: 8.1, w: 4.733, align: 'right', ...FOOT });

slide.addNotes([
  'Redesign of GAO-25-107795, Figure 1 (PDF page 11, printed page 5), for a slide read at a distance.',
  `Title numbers are GAO's: about $83 billion (79 percent) of planned FY2025 IT spending for operations and maintenance (report page 4). The figure prints $${band.omUsd.toLocaleString('en-US')} million of $${band.total.toLocaleString('en-US')} million; the exact share is ${overall.toFixed(2)}%.`,
  'The bars are one native bar chart: right-click and choose Edit Data. Shares are the printed whole percents. Agencies with equal shares keep GAO\'s order, largest total first.',
  'The orange line is a drawn line at the computed 78.78% position of the axis. It does not move if the data change.',
  'Portfolio reconstruction of a public GAO figure. Not a GAO product.',
].join('\n\n'));

// Chart XML: show value labels only on the five extremes (bars 1 to 3 and 23 to 24).
const out = path.join(ROOT, 'slides', 'figure1', 'redesign.pptx');
writeDeck(pptx, out, async (zip) => {
  const { name, xml } = await chartPart(zip);
  const m = xml.match(/<c:dLbls>([\s\S]*?)<c:showLegendKey val="0"\/>([\s\S]*?)<\/c:dLbls>/);
  if (!m) throw new Error('series data labels not found');
  const head = m[1]; // numFmt, txPr and dLblPos as pptxgenjs wrote them for the series
  const pointLabel = (i) => `<c:dLbl><c:idx val="${i}"/>${head}<c:showLegendKey val="0"/><c:showVal val="1"/>`
    + '<c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbl>';
  const seriesLevel = m[2].replace('<c:showVal val="1"/>', '<c:showVal val="0"/>');
  const dLbls = `<c:dLbls>${extremeIdx.map(pointLabel).join('')}${head}<c:showLegendKey val="0"/>${seriesLevel}</c:dLbls>`;
  zip.file(name, xml.replace(m[0], dLbls));
}).then((f) => console.log('wrote', path.relative(ROOT, f)));
