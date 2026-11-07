# 左程云风格：通用规则

本文件是从 `D:\Desktop\algorithm-journey-main\src` 的 Java 源码归纳出来的。注意：该仓库 **1126 个 .java 里 596 个自带 `main`**，是他的原生风格；`cpp/` 与 `class061/普利姆.*` 是他人转写，不作为风格依据。

## 一、证据

| 特征 | 出处 | 原文 |
|---|---|---|
| 头部注释四件套：中文名、复杂度、测试链接、提交说明 | `class021/Code01_MergeSort.java:3-7` | `// 归并排序，acm练习风格` / `// 测试链接 : https://...` / `// 提交以下的code，提交时请把类名改成"Main"` |
| 全局静态数组 + MAXN | 同上 `:18-22` | `public static int MAXN = 100001;` / `public static int[] arr = new int[MAXN];` |
| 多返回值用静态字段 | `class022/...partition`、`class061/Code02_PrimStatic.java:97-99` | `public static int u;` / `public static int w;` |
| 短变量名 | `Code01_MergeSort.java:85-88` | `int i = l; int a = l; int b = m + 1;` |
| 循环内声明 | `Code01_MergeSort.java:68` | `for (int l, m, r, step = 1; step < n; step <<= 1)` |
| 三元压行 | `Code01_MergeSort.java:90` | `help[i++] = arr[a] <= arr[b] ? arr[a++] : arr[b++];` |
| while 做双指针 | 同上 `:89-98` | `while (a <= m && b <= r) { ... }` |
| 手写堆/队列 | `Code02_PrimStatic.java:43-123` | `public static int[][] heap`、`where[]`、`heapInsert/heapify` |
| 定长 IO 模板 | `Code01_MergeSort.java:26-45` | BufferedReader + StreamTokenizer + PrintWriter |
| 注释只写"为什么" | `Code01_MergeSort.java:47-52` | 用 master 公式推导复杂度，不解释语法 |

## 二、映射到 C++ / C / Python

Java 的写法不能逐字搬，只搬**结构决策**：

| 决策 | Java 原样 | C++ | C | Python |
|---|---|---|---|---|
| 常量 | `static int MAXN` | `const int MAXN` | `#define MAXN` | 模块级 `MAXN = ...` |
| 大数组 | `static int[] a` | 全局 `int a[MAXN];` | 全局 `int a[MAXN];` | 模块级 `a = [0] * MAXN` |
| 多返回值 | 静态字段 | 全局变量或引用参数 | 指针传出 | 返回 tuple |
| 队列 | 手写 `int[] q` + `head/tail` | 同左 | 同左 | `collections.deque` |
| 堆 | 手写 `heap[]` | 手写或 `priority_queue` | 手写 | `heapq`（大顶堆存负数） |
| 输入 | StreamTokenizer | `ios::sync_with_stdio(false)` | `scanf` | `sys.stdin.buffer.read().split()` |

**关键原则**：结构上保持"朴素 + 手写"，语法上服从各语言习惯。把 Java 的 class 壳子搬到 C++ 叫移植失败；把 C++ 的 `std::function` 递归搬到 Python 叫过度设计。

## 三、命名

固定短名表，按语义取，不按题目取：

| 语义 | 用 |
|---|---|
| 规模 | `n m k q` |
| 下标/边界 | `i j l r mid` |
| 双指针 | `a b p1 p2 left right` |
| 图/边 | `u v w ei head nxt to weight` |
| 队列/堆 | `q head tail hp size cnt` |
| 答案/累加 | `ans pre cur sum mx mn` |
| 节点 | `x y fa sz dep` |

禁止：`nums`、`target`、`matrix`、`intervals`、`result`、`temp`、`data` 这类题目原词和通用词。它们既不短，也不携带语义。

## 四、函数

- 按**调用顺序**从上往下排，`main` 在最后或最前，二者择一，全篇一致。
- 一个函数一件事，参数不超过 4 个；超过就说明该用全局数组了。
- 边界用早返回：`if (l >= r) return;`，不要写 `if (l < r) { ... }` 再套一整层。

## 五、格式

- 缩进 4 空格，不用 Tab（Java 源用 Tab，转写到 C/C++/Python 统一 4 空格，避免粘贴错位）。
- K&R 大括号：`if (x) {` 同行，`}` 独行。C 语言里单语句可以省大括号，但题解里统一保留。
- 逻辑块之间一个空行，不空两行，不加分隔线注释。
- 一段代码不超过 60 行；超了就是函数没拆。

## 六、注释

**零**。这是本技能与普通题解最大的差别：

- 不写 `// 初始化`、`# 读入`。
- 不写分节线 `// ----------`。
- 不写 `// TODO`、`// 这里注意`。
- 需要解释的东西，写进"思路"段，不写进代码。

## 七、常见误判

| 以为 | 实际 |
|---|---|
| 左程云风格 = Java | 风格是结构决策，不是语言。C++ 一样能写出这个味道 |
| 短名 = 难读 | 短名 + 小作用域 + 单函数单职责，比长名还好读 |
| 手写堆=炫技 | 他手写是因为要控制 `where[]` 做 decrease-key，库堆做不到；能给库就用库 |
