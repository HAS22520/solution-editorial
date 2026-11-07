#!/usr/bin/env node
/**
 * md2docx.js — 把一份或多份题解 markdown 编译成一份 Word（.docx）
 *
 * 设计目标：一次交付一份文档，不再为每题落 .md 中间产物之外的任何东西；
 * 公式一律转成 Word 原生公式（OMML），不允许出现裸 LaTeX 文本。
 *
 * 用法：
 *   node md2docx.js 输出.docx 题解1.md [题解2.md ...]
 *   node md2docx.js 输出.docx 题解1.md --title "程序设计竞赛题解手册"
 *
 * 退出码：0 成功；1 参数错误；2 依赖缺失；3 有公式无法转换（已退化为文本）
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');

// ── 依赖解析 ────────────────────────────────────────────────────────────────
// 两个坑：
//  1) docx 必须和 mathml-to-docx 内部 require('docx') 拿到同一个模块实例，
//     否则 instanceof 判断失败，Math 的子节点会被序列化成 <rootKey> 垃圾。
//     做法：createRequire 绑定到 mathml-to-docx 自己的文件，再 req('docx')。
//  2) temml 裸 require 解析到 dist/temml.js（UMD 浏览器构建），在 Node 里是空对象，
//     renderToString 不存在。必须显式加载 dist/temml.cjs。
function firstExisting(cands) {
  for (const c of cands) {
    try { if (fs.existsSync(c)) return c; } catch (e) { /* ignore */ }
  }
  return null;
}

function globalNpmRoot() {
  try {
    const { execSync } = require('child_process');
    return execSync('npm root -g', { encoding: 'utf8' }).trim();
  } catch (e) {
    return null;
  }
}

function findMathLib() {
  const cands = [
    path.resolve(__dirname, '../node_modules/docx-editor-cn/scripts/mathml-to-docx.js'),
    'C:/Users/HAS/.dsh/skills-src/docx-skill-4-cn-paper/docx-editor-cn/scripts/mathml-to-docx.js',
    path.resolve(__dirname, '../../docx-skill-4-cn-paper/docx-editor-cn/scripts/mathml-to-docx.js'),
  ];
  return firstExisting(cands);
}

function findTemml() {
  const root = globalNpmRoot();
  const cands = [
    path.resolve(__dirname, '../node_modules/temml/dist/temml.cjs'),
    'C:/Users/HAS/.dsh/skills-src/docx-skill-4-cn-paper/docx-editor-cn/node_modules/temml/dist/temml.cjs',
    root ? path.join(root, 'temml/dist/temml.cjs') : null,
  ].filter(Boolean);
  return firstExisting(cands);
}

const mathLibPath = findMathLib();
if (!mathLibPath) {
  console.error('✗ 找不到 mathml-to-docx.js，请先安装 docx-editor-cn 技能');
  process.exit(2);
}
const req = createRequire(mathLibPath);
const docx = req('docx');
const { mathmlToDocxChildren } = req('./mathml-to-docx.js');

const temmlPath = findTemml();
const temml = temmlPath ? require(temmlPath) : null;

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  BorderStyle, WidthType, AlignmentType, LineRuleType, HeadingLevel,
  Footer, PageNumber, PageBreak, Math,
} = docx;

// ── 样式常量 ────────────────────────────────────────────────────────────────
const BORDER = { style: BorderStyle.SINGLE, size: 4, color: 'D0D7DE' };
const CELL_BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };
const SANS = 'SimHei';
const SERIF = 'SimSun';
const MONO = 'Consolas';

let failedMath = 0;

function textRun(text, opts = {}) {
  return new TextRun({
    text,
    size: opts.size || 21,
    bold: !!opts.bold,
    font: opts.font || { ascii: 'Cambria', eastAsia: SERIF, hAnsi: 'Cambria' },
    color: opts.color || '24292F',
  });
}

function createTitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 120 },
    children: [textRun(text, { size: 44, bold: true, font: { ascii: SANS, eastAsia: SANS, hAnsi: SANS }, color: '1F2328' })],
  });
}

function createSubtitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 360 },
    children: [textRun(text, { size: 24, color: '57606A' })],
  });
}

function createHeading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 240, after: 120 },
    indent: { firstLine: 0 },
    children: [textRun(text, { size: 32, bold: true, font: { ascii: SANS, eastAsia: SANS, hAnsi: SANS }, color: '1F2328' })],
  });
}

function createHeading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 },
    indent: { firstLine: 0 },
    children: [textRun(text, { size: 28, bold: true, font: { ascii: SANS, eastAsia: SANS, hAnsi: SANS }, color: '1F2328' })],
  });
}

function createHeading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 160, after: 80 },
    indent: { firstLine: 0 },
    children: [textRun(text, { size: 22, bold: true, font: { ascii: SANS, eastAsia: SANS, hAnsi: SANS }, color: '24292F' })],
  });
}

// ── 公式 ────────────────────────────────────────────────────────────────────
function latexToMathRuns(latex) {
  if (!temml) throw new Error('temml 不可用');
  const mathml = temml.renderToString(latex, { displayMode: true, throwOnError: false, strict: false });
  const children = mathmlToDocxChildren(mathml, {});
  if (!children || !children.length) throw new Error('MathML 为空');
  return children;
}

function createFormulaParagraph(latex) {
  let runs;
  try {
    runs = latexToMathRuns(latex);
  } catch (e) {
    failedMath++;
    console.warn(`! 公式转换失败，已退化为纯文本：${latex.slice(0, 50)}（${e.message}）`);
    return new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 100, after: 100 },
      children: [textRun(latex, { size: 22, color: '0969DA' })],
    });
  }
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 140, after: 140, line: 300, lineRule: LineRuleType.AUTO },
    children: [new Math({ children: runs })],
  });
}

// 行内公式：把 "前 $x_i$ 后" 拆成文本/公式交替的 run 列表
function buildInlineChildren(text) {
  const parts = text.split(/(\$[^$]+\$)/g).filter((s) => s !== '');
  const out = [];
  for (const part of parts) {
    if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
      try {
        out.push(new Math({ children: latexToMathRuns(part.slice(1, -1)) }));
        continue;
      } catch (e) {
        failedMath++;
        console.warn(`! 行内公式转换失败，保留原文：${part}`);
      }
    }
    out.push(textRun(part));
  }
  return out;
}

function createBodyParagraph(text) {
  return new Paragraph({
    spacing: { before: 40, after: 80, line: 320, lineRule: LineRuleType.AUTO },
    indent: { firstLine: 420 },
    children: buildInlineChildren(text),
  });
}

function createCodeBlock(codeText) {
  const lines = codeText.replace(/\s+$/, '').split(/\r?\n/);
  const paragraphs = lines.map((line) => new Paragraph({
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    indent: { firstLine: 0 },
    children: [textRun(line.length ? line : ' ', { size: 19, font: { ascii: MONO, eastAsia: SERIF, hAnsi: MONO } })],
  }));

  return new Table({
    width: { size: 9070, type: WidthType.DXA },
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: 9070, type: WidthType.DXA },
        shading: { fill: 'F6F8FA' },
        borders: CELL_BORDERS,
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        children: paragraphs,
      })],
    })],
  });
}

// ── markdown 解析 ───────────────────────────────────────────────────────────
function parseEditorial(mdPath) {
  const lines = fs.readFileSync(mdPath, 'utf8').split(/\r?\n/);
  const sections = { 题意: [], 思路: [], 代码: { cpp: '', c: '', python: '' } };
  let title = '';
  let current = '';
  let currentLang = '';
  let inCode = false;
  let buffer = [];

  for (const raw of lines) {
    const line = raw;
    const trimmed = line.trim();

    if (trimmed.startsWith('```')) {
      if (!inCode) { inCode = true; buffer = []; }
      else {
        inCode = false;
        if (currentLang && sections.代码[currentLang] !== undefined) sections.代码[currentLang] = buffer.join('\n');
      }
      continue;
    }
    if (inCode) { buffer.push(line); continue; }

    if (trimmed.startsWith('### ')) {
      const lang = trimmed.slice(4).trim().toLowerCase();
      if (lang === 'c++' || lang === 'cpp') currentLang = 'cpp';
      else if (lang === 'c') currentLang = 'c';
      else if (lang === 'python') currentLang = 'python';
      continue;
    }
    if (trimmed.startsWith('## ')) { current = trimmed.slice(3).trim(); continue; }
    if (trimmed.startsWith('# ')) { title = trimmed.slice(2).trim(); continue; }

    if ((current === '题意' || current === '思路') && trimmed) {
      sections[current].push(trimmed);
    }
  }
  return { title: title || path.basename(mdPath, '.md'), sections };
}

// ── 主流程 ──────────────────────────────────────────────────────────────────
function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('用法: node md2docx.js 输出.docx 题解1.md [题解2.md ...] [--title 标题]');
    process.exit(1);
  }

  let docTitle = '题解';
  const files = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--title') { docTitle = args[++i]; continue; }
    files.push(args[i]);
  }
  const outPath = path.resolve(files.shift());
  const mdPaths = files.map((f) => path.resolve(f));

  for (const p of mdPaths) {
    if (!fs.existsSync(p)) { console.error(`✗ 找不到 ${p}`); process.exit(1); }
  }

  const children = [createTitle(docTitle)];
  if (mdPaths.length > 1) {
    children.push(createSubtitle(`${mdPaths.length} 道题目 · 题意 · 思路与正确性 · C++ / C / Python 实现`));
  }

  mdPaths.forEach((md, idx) => {
    if (idx > 0) children.push(new Paragraph({ children: [new PageBreak()] }));
    const { title, sections } = parseEditorial(md);
    children.push(createHeading1(mdPaths.length > 1 ? `题目 ${idx + 1}：${title}` : title));

    children.push(createHeading2('一、题意'));
    for (const p of sections.题意) children.push(createBodyParagraph(p));

    children.push(createHeading2('二、思路'));
    for (const p of sections.思路) {
      const m = p.match(/^\$\$(.*)\$\$$/);
      if (m) children.push(createFormulaParagraph(m[1].trim()));
      else children.push(createBodyParagraph(p));
    }

    children.push(createHeading2('三、代码'));
    const langs = [['cpp', 'C++ 实现'], ['c', 'C 语言实现'], ['python', 'Python 实现']];
    for (const [key, label] of langs) {
      if (!sections.代码[key]) continue;
      children.push(createHeading3(label));
      children.push(createCodeBlock(sections.代码[key]));
    }
  });

  const doc = new Document({
    sections: [{
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, right: 1418, bottom: 1418, left: 1418 } },
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            indent: { firstLine: 0 },
            children: [textRun('', { size: 18 }), new TextRun({ children: [PageNumber.CURRENT], size: 18, font: { ascii: SERIF, eastAsia: SERIF, hAnsi: SERIF } })],
          })],
        }),
      },
      children,
    }],
  });

  Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(outPath, buf);
    console.log(`✓ 写出 ${outPath}（${mdPaths.length} 题，${(buf.length / 1024).toFixed(1)} KB）`);
    if (failedMath) {
      console.error(`✗ 有 ${failedMath} 个公式退化为纯文本，请检查`);
      process.exit(3);
    }
  }).catch((e) => {
    console.error('✗ 生成失败：', e.message);
    process.exit(1);
  });
}

if (!temml) console.warn('! temml 不可用，公式将退化为纯文本');
main();
