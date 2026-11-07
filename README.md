# solution-editorial

写算法题题解的技能（DSH / Claude Skill 格式）。产出固定三段：**数学化题意 → 思路与正确性 → C++/C/Python 三份代码**（语言顺序固定，代码不带注释）。

## 特点

- **不复述题目**：题意压到 3 行以内，只用符号和约束。
- **代码不带注释**：`//`、`/* */`、`#` 一个不写（但这是写作约束，不会写进题解正文当卖点）。
- **语言顺序固定**：C++ → C → Python。
- **左程云风格**：短变量名、全局静态数组、手写队列/堆、`while` 双指针、三元压行、固定 IO 模板。
- **可执行自检**：`lint_editorial.py` 查结构，`verify_triple.py` 真编译三份代码并比对输出。
- **直出 Word/PDF**：`md2docx.js` 把多题合成一份 docx（公式转 Word 原生公式），`docx2pdf.ps1` 导出 pdf，`check_docx.py` 验收。

## 目录

```
SKILL.md                       技能入口（路由 + 铁律 + 工作流 + 清单）
references/
  output-format.md             三段骨架逐节写法与正反例
  idea-writing.md              题意符号化、思路四段式、正确性论证模板
  style-rules.md               风格规则与源码证据
  style-cpp.md / style-c.md / style-python.md
  pitfalls.md                  9 条常见退化
  export-docx.md               md→docx→pdf 流水线与两个依赖坑
assets/skeleton.md             可直接复制的骨架
examples/example-sliding-window-max.md
scripts/lint_editorial.py
scripts/verify_triple.py
scripts/md2docx.js
scripts/docx2pdf.ps1
scripts/check_docx.py
```

## 用法

```powershell
# 1. 挂到 DSH 技能目录（一次性）
cmd /c mklink /J "$env:USERPROFILE\.dsh\skills\solution-editorial" "$env:USERPROFILE\.dsh\skills-src\solution-editorial"

# 2. 写完题解后自检
python scripts/lint_editorial.py 题解.md --strict
python scripts/verify_triple.py 题解.md --input in.txt

# 3. 要 Word：多题合成一份 docx，再导出 pdf
node scripts/md2docx.js out.docx _src\题解-A.md _src\题解-B.md --title "程序设计竞赛题解手册"
powershell -ExecutionPolicy Bypass -File scripts/docx2pdf.ps1 -Docx out.docx
python scripts/check_docx.py out.docx --pdf out.pdf
```

所有脚本返回非零退出码表示不通过，可直接接入自动检查。

## 已知边界（实测踩过的坑）

- `\begin{cases}` 转出来是没有花括号的矩阵，分段函数改用两条带条件的等式。
- `\quad`、`\hspace` 的间距会被丢弃，需要空隙写 `\ \ `。
- `\text{"  "}` 里的连续空格会被吞，要表达"两个空格"直接写汉字。
- temml 必须显式加载 `dist/temml.cjs`，否则在 Node 里是空对象，公式会静默退化成 LaTeX 原文。
- `docx` 必须与 `mathml-to-docx` 用同一个构建入口，否则输出 `<rootKey>` 垃圾。

详见 `references/export-docx.md`。

## 风格来源

结构风格取自 `D:\Desktop\algorithm-journey-main\src`（左程云算法课）的 Java 源码：1126 个 `.java` 中 596 个自带 `main` 对数器，是作者原生风格；仓库内的 `cpp/`、`src/class061/普利姆.*` 为他人转写，仅作语法参考，不作风格依据。

Java 写法不能逐字搬到 C/C++/Python，本技能只搬结构决策（常量、全局数组、手写结构、短名、循环形态），语法服从各语言习惯。详见 `references/style-rules.md`。

## 许可

自用技能，可随意修改。
