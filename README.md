# solution-editorial

写算法题题解的技能（DSH / Claude Skill 格式）。产出固定三段：**数学化题意 → 思路与正确性 → C++/C/Python 三段零注释代码**。

## 特点

- **不复述题目**：题意压到 3 行以内，只用符号和约束。
- **代码零注释**：`//`、`/* */`、`#` 一个不写。
- **语言顺序固定**：C++ → C → Python。
- **左程云风格**：短变量名、全局静态数组、手写队列/堆、`while` 双指针、三元压行、固定 IO 模板。
- **可执行自检**：`lint_editorial.py` 查结构，`verify_triple.py` 真编译三份代码并比对输出。

## 目录

```
SKILL.md                       技能入口（路由 + 铁律 + 工作流 + 清单）
references/
  output-format.md             三段骨架逐节写法与正反例
  idea-writing.md              题意符号化、思路四段式、正确性论证模板
  style-rules.md               风格规则与源码证据
  style-cpp.md / style-c.md / style-python.md
  pitfalls.md                  9 条常见退化
assets/skeleton.md             可直接复制的骨架
examples/example-sliding-window-max.md
scripts/lint_editorial.py
scripts/verify_triple.py
```

## 用法

```powershell
# 1. 挂到 DSH 技能目录（一次性）
cmd /c mklink /J "$env:USERPROFILE\.dsh\skills\solution-editorial" "$env:USERPROFILE\.dsh\skills-src\solution-editorial"

# 2. 写完题解后自检
python scripts/lint_editorial.py 题解.md --strict
python scripts/verify_triple.py 题解.md --input in.txt
```

两条脚本都返回非零退出码表示不通过，可直接接入自动检查。

## 风格来源

结构风格取自 `D:\Desktop\algorithm-journey-main\src`（左程云算法课）的 Java 源码：1126 个 `.java` 中 596 个自带 `main` 对数器，是作者原生风格；仓库内的 `cpp/`、`src/class061/普利姆.*` 为他人转写，仅作语法参考，不作风格依据。

Java 写法不能逐字搬到 C/C++/Python，本技能只搬结构决策（常量、全局数组、手写结构、短名、循环形态），语法服从各语言习惯。详见 `references/style-rules.md`。

## 许可

自用技能，可随意修改。
