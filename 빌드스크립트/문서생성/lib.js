// BuildOne 2.0 기획서 공통 서식 — V1 기획문서와 같은 모양(맑은 고딕 · 남색 제목 · 연한 파랑 상자)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, ImageRun, Footer, PageNumber, LevelFormat, PageBreak, VerticalAlign, TableLayoutType,
} = require('docx');

const FONT = '맑은 고딕';
const NAVY = '1F3864', BLUE = '2E5496', GRAY = '444444', SUB = '6B727C';
const W = 9632; // 본문 너비 (Letter 12240 - 좌우 여백 1304*2)
const IMG_DIR = path.join(__dirname, 'img');

// **굵게** 표시를 TextRun 여러 개로
function runs(text, base = {}) {
  const out = [];
  String(text).split(/(\*\*[^*]+\*\*)/).forEach(seg => {
    if (!seg) return;
    const b = seg.startsWith('**') && seg.endsWith('**');
    out.push(new TextRun({ text: b ? seg.slice(2, -2) : seg, bold: b || base.bold, color: base.color, size: base.size, italics: base.italics, font: FONT }));
  });
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), alignment: o.align, spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 300 }, keepNext: o.keepNext });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })], pageBreakBefore: false });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const B = (t, lvl = 0) => new Paragraph({ children: runs(t), numbering: { reference: 'bul', level: lvl }, spacing: { after: 80, line: 290 } });
const N = (t) => new Paragraph({ children: runs(t), numbering: { reference: 'num', level: 0 }, spacing: { after: 80, line: 290 } });
const PB = () => new Paragraph({ children: [new PageBreak()] });

const border = { style: BorderStyle.SINGLE, size: 4, color: 'C9D2E3' };
const borders = { top: border, bottom: border, left: border, right: border };
const noB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };

function cell(content, w, o = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map(c => typeof c === 'string'
    ? new Paragraph({ children: runs(c, { bold: o.bold, color: o.color, size: o.size ?? 19 }), alignment: o.align, spacing: { after: 40, line: 270 } })
    : c);
  return new TableCell({
    children: paras, width: { size: w, type: WidthType.DXA }, borders: o.borders || borders,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 }, verticalAlign: o.valign || VerticalAlign.CENTER,
  });
}
// 표: headers 배열, rows 배열의 배열, weights(비율)
function T(headers, rows, weights) {
  const tot = weights.reduce((a, b) => a + b, 0);
  const ws = weights.map(x => Math.floor(W * x / tot)); ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  const head = new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, ws[i], { fill: NAVY, color: 'FFFFFF', bold: true, align: AlignmentType.CENTER })) });
  const body = rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, ws[i], { fill: ri % 2 ? 'F7F9FC' : 'FFFFFF', bold: i === 0 && r.length > 2 ? false : false })) }));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, rows: [head, ...body], layout: TableLayoutType.FIXED }), P('', { after: 60 })];
}
// 강조 상자 (info: 연한 파랑, warn: 연한 노랑, tip: 연한 회청)
function BOX(title, lines, kind = 'info') {
  const fill = kind === 'warn' ? 'FFF7E0' : kind === 'tip' ? 'EDF1F8' : 'EAF2FB';
  const kids = [];
  if (title) kids.push(new Paragraph({ children: runs(title, { bold: true, color: kind === 'warn' ? 'B35C00' : NAVY, size: 21 }), spacing: { after: 80 } }));
  lines.forEach(l => kids.push(new Paragraph({ children: runs(l, { size: 20 }), spacing: { after: 60, line: 290 } })));
  const lb = { style: BorderStyle.SINGLE, size: 24, color: kind === 'warn' ? 'F0A030' : BLUE };
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ children: [new TableCell({
    children: kids, width: { size: W, type: WidthType.DXA }, shading: { fill, type: ShadingType.CLEAR, color: 'auto' },
    borders: { top: noB, bottom: noB, right: noB, left: lb }, margins: { top: 140, bottom: 120, left: 220, right: 200 } })] })] }), P('', { after: 60 })];
}
// 흐름 상자: [['대표','교육 공지'], ...]
function FLOW(steps) {
  const n = steps.length, arrowW = 380, boxW = Math.floor((W - arrowW * (n - 1)) / n);
  const ws = []; steps.forEach((s, i) => { ws.push(boxW); if (i < n - 1) ws.push(arrowW); }); ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  const cells = []; let k = 0;
  steps.forEach((s, i) => {
    cells.push(new TableCell({ width: { size: ws[k++], type: WidthType.DXA }, shading: { fill: NAVY, type: ShadingType.CLEAR, color: 'auto' }, borders: { top: noB, bottom: noB, left: noB, right: noB },
      margins: { top: 100, bottom: 100, left: 60, right: 60 }, verticalAlign: VerticalAlign.CENTER,
      children: s.map((l, j) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: l, font: FONT, color: j ? 'FFFFFF' : 'BFD3F2', bold: !!j, size: j ? 19 : 16 })] })) }));
    if (i < n - 1) cells.push(new TableCell({ width: { size: ws[k++], type: WidthType.DXA }, borders: { top: noB, bottom: noB, left: noB, right: noB }, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '▶', font: FONT, color: BLUE, size: 20 })] })] }));
  });
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, rows: [new TableRow({ children: cells })], layout: TableLayoutType.FIXED }), P('', { after: 80 })];
}
// 그림: 파일, 원래 픽셀 크기, 캡션
function IMG(file, w, h, caption, maxW = 600, maxH = 520) {
  let sw = Math.min(maxW, w), sh = Math.round(h * sw / w); if (sh > maxH) { sh = maxH; sw = Math.round(w * sh / h); }
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 40 }, keepNext: true,
    children: [new ImageRun({ type: 'jpg', data: fs.readFileSync(path.join(IMG_DIR, file)), transformation: { width: sw, height: sh },
      altText: { title: caption, description: caption, name: file } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: runs(caption, { size: 17, color: SUB }) })];
}
// 표지
function COVER(c) {
  const out = [];
  out.push(P('', { after: 600 }));
  out.push(new Paragraph({ children: [new TextRun({ text: 'BuildOne 2.0', font: FONT, bold: true, size: 84, color: NAVY })], spacing: { after: 120 } }));
  out.push(new Paragraph({ children: [new TextRun({ text: c.module, font: FONT, bold: true, size: 38, color: BLUE })], spacing: { after: 80 } }));
  out.push(new Paragraph({ children: [new TextRun({ text: c.kind, font: FONT, size: 30, color: GRAY })], spacing: { after: 60 } }));
  out.push(new Paragraph({ children: [new TextRun({ text: c.sub, font: FONT, size: 21, color: SUB })], spacing: { after: 360 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 8 } } }));
  out.push(P('**한 줄 요약**', { color: NAVY, size: 22, after: 80 }));
  c.oneLine.forEach(l => out.push(P(l, { size: 23, after: 60 })));
  out.push(P('', { after: 280 }));
  out.push(...T(['항목', '내용'], c.meta, [1, 4]));
  out.push(PB());
  return out;
}

function build(file, title, content) {
  const doc = new Document({
    creator: 'BuildOne', title, description: title,
    styles: {
      default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT, cs: FONT }, size: 20, color: '222222' } } },
      paragraphStyles: [
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { font: FONT, size: 30, bold: true, color: NAVY }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true,
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'C9D2E3', space: 4 } } } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { font: FONT, size: 24, bold: true, color: BLUE }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1, keepNext: true } },
      ],
    },
    numbering: { config: [
      { reference: 'bul', levels: [
        { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
        { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 260 } } } }] },
      { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } }] },
    ] },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1247, right: 1304, bottom: 1134, left: 1304, header: 720, footer: 720 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: title + '  ·  ', font: FONT, size: 16, color: SUB }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: SUB }) ] })] }) },
      children: content,
    }],
  });
  return Packer.toBuffer(doc).then(buf => { fs.writeFileSync(file, buf); return file; });
}

module.exports = { P, H1, H2, B, N, PB, T, BOX, FLOW, IMG, COVER, build };
