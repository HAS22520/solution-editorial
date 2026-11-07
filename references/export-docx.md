# 出 Word / PDF

题解最终形态通常是「一份 Word + 一份由它导出的 PDF」。本文记录流水线、两个必须知道的坑，以及交付前的机器验收。

## 一、流水线

```powershell
# 1) md 源（可以放 _src/ 或临时目录，不是交付物）
#    每题一个 md，结构见 references/output-format.md

# 2) 多份 md 合成一份 docx（公式转 Word 原生公式）
node scripts/md2docx.js "D:\out\题解手册.docx" `
  "_src\题解-A.md" "_src\题解-B.md" "_src\题解-C.md" `
  --title "程序设计竞赛题解手册"

# 3) 由 docx 导出 pdf（优先 Word，其次 WPS）
powershell -ExecutionPolicy Bypass -File scripts/docx2pdf.ps1 -Docx "D:\out\题解手册.docx"

# 4) 机器验收
python scripts/check_docx.py "D:\out\题解手册.docx"
```

一次交付只要 **一个 docx + 一个 pdf**。用户没说要 Word 时，直接给 md，别顺手做 docx。

## 二、两个坑

### 坑 1：`require('docx')` 与转换器拿到的是两个不同构建

`mathml-to-docx.js` 内部 `require('docx')`，解析到 `node_modules/docx/dist/index.cjs`；而脚本里直接 `require('<绝对路径>/node_modules/docx')` 会走 `package.json` 的 `main`，拿到 `index.umd.cjs`。两个构建的类是不同的构造函数，`instanceof` 失败后 docx 会把公式子节点当成普通对象，输出一堆 `<rootKey>` 垃圾——**表面上看生成了 docx，打开却是空白或乱码**。

正确写法（`md2docx.js` 已内置）：

```js
const { createRequire } = require('module');
const req = createRequire('<...>/mathml-to-docx.js');   // 绑定到转换器所在位置
const docx = req('docx');                              // 同一个实例
const { mathmlToDocxChildren } = req('./mathml-to-docx.js');
```

### 坑 2：`require('temml')` 在 Node 里是空对象

temml 的 `exports.require` 指向 `dist/temml.cjs`，但裸 require 常常解析到 `dist/temml.js`（浏览器 UMD 构建），在 Node 里导出空对象，`renderToString` 不存在。脚本若没做检查，就会静默退化成「把 LaTeX 原文当文本塞进段落」——这正是公式显示成 `\text{cell}(i,j)=\begin{cases}...` 的原因。

```js
const temml = require('<...>/temml/dist/temml.cjs');   // 显式指定 CJS 构建
if (typeof temml.renderToString !== 'function') throw new Error('temml 构建不对');
```

## 三、公式写法约定

| 写法 | 结果 |
|---|---|
| `$$...$$` 独占一行 | 转成居中 Word 公式（独立段落） |
| 行内 `$...$` | 转成行内 Word 公式 |
| `\text{中文}` | 正常，Word 用中文字体回退 |
| `\quad` / `\hspace` | **间距被丢弃**，`a,\quad b` 变成 `a,b` |
| `\ \ `（两个控制空格） | 间距保留，且不影响斜体 —— 推荐 |
| `\begin{cases}` | 变成无花括号的 2×2 矩阵，视觉上不像分段函数 |
| `p++` | 渲染成 `p + +`，运算符间被加了间距 |

因此：

- 分段函数**不用 `cases`**，写成两条带条件的等式：
  ```latex
  $$\text{cell}(i,j)=\text{format}(p++),\ \ j\ge n-1-i$$
  $$\text{cell}(i,j)=\text{两个连续空格},\ \ j<n-1-i$$
  ```
- 需要空隙就用 `\ \ `，不要用 `\quad`。
- 字面里的连续空格会被吞掉（`\text{"  "}` 渲染成 `""`），要表达"两个空格"就写汉字。
- `i++` 这类连写无法避免 `i + +`，可接受；不要在公式里写大段 C 代码。

## 四、验收清单

`check_docx.py` 会做这些检查（退出码 0 通过 / 1 失败）：

1. `document.xml` 里 LaTeX 残留数（`\text`、`\begin`、`\frac`、`\ge` 等）必须为 0
2. `oMath` 个数 > 0（有公式时），且没有 `<rootKey>` 垃圾
3. 不得出现"零注释""无注释"字样
4. 若给了 pdf：页数、每页是否有内容

机器检查通过后，**仍要人眼看**：把 pdf 渲成图，至少看含公式的页、第一页和最后一页。

```powershell
python -c "import pymupdf; d=pymupdf.open(r'x.pdf'); [d[i].get_pixmap(dpi=110).save(rf'p{i+1}.png') for i in range(d.page_count)]"
```

## 五、导出失败怎么办

| 现象 | 原因 | 处理 |
|---|---|---|
| `EBUSY: resource busy or locked` | 文件正被 Word/WPS 打开 | 关掉再生成；或先输出到 `-修正版.docx` |
| `docx2pdf.ps1` 报 ParserError / 中文乱码 | 用 Windows PowerShell 5.1 读了无 BOM 的 UTF-8 脚本 | 脚本已存为 UTF-8 with BOM；自己改脚本后要重新加 BOM |
| `没有可用的 Office/WPS COM 引擎` | 本机没装 Office/WPS | 装一个，或用 `office-export-pdf` 技能（LibreOffice Kit） |
