# Python 模板与规则

## 模板

```python
import sys
from collections import deque

def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    a = data[1:1 + n]
    q = deque()
    out = []
    for i in range(n):
        while q and a[q[-1]] <= a[i]:
            q.pop()
        q.append(i)
        if q[0] <= i - 1:
            q.popleft()
        if i >= 1:
            out.append(str(a[q[0]]))
    sys.stdout.write(" ".join(out) + "\n")

main()
```

顶层 `def main()` + 最后一行 `main()`。不用类，不用 `if __name__ == "__main__"`（题解场景下多余）。

## 硬规则

- 不写类型注解、不写 dataclass、不写装饰器。保持朴素。
- 不用类包装解法。需要多个返回值就返回 tuple。
- 循环里避免切片（`a[l:r]` 每次复制 O(n)），用下标。
- 输出用 `sys.stdout.write` 或 `" ".join(...)` 一次性写；避免循环 `print`（1e5 行时明显慢）。
- 缩进 4 空格，不用 Tab。

## 输入

| 场景 | 写法 |
|---|---|
| 全部是整数、一次读完 | `data = list(map(int, sys.stdin.buffer.read().split()))` |
| 按行读、行内有结构 | `sys.stdin.buffer.readline()` |
| 单行若干整数 | `n, m = map(int, sys.stdin.buffer.readline().split())` |
| 字符串矩阵 | `[input().strip() for _ in range(n)]` 配 `sys.stdin.readline` |

`input = sys.stdin.readline` 可以简写，但注意它返回带换行的字符串。

## 递归

```python
sys.setrecursionlimit(1 << 25)
```

默认递归深度 1000，DFS 深度到 1e5 必爆。两条路：

1. 加 `setrecursionlimit`，同时确认内存够（每层栈帧几十字节到几百字节）。
2. 改迭代：显式栈 `stack = [(u, fa)]`。

题解里优先写迭代，或在思路里点明"深度 O(n)，已提高递归上限"。

## 踩坑清单

| 坑 | 说明 | 正确写法 |
|---|---|---|
| `//` 是向下取整 | `-3 // 2 == -2`，不是 -1 | 截断用 `int(a / b)` 或 `-(-a // b)` |
| `[0] * n` 的二维 | `[[0] * m] * n` 是同一行引用 | `[[0] * m for _ in range(n)]` |
| 大顶堆 | `heapq` 是小顶堆 | 存 `-x`，取出再取负 |
| `float` 精度 | 涉及比较时别用浮点 | 交叉相乘或用 `Fraction` |
| 默认参数可变 | `def f(a=[])` 会跨调用共享 | 用 `None` 占位 |
| 深浅拷贝 | `b = a` 是引用 | 需要副本用 `a[:]` 或 `copy.deepcopy` |
| 字符串拼接 | 循环里 `s += x` 是 O(n²) | 收集到 list 再 `join` |

## 语言特性的取舍

| 场景 | 建议 |
|---|---|
| 最短路、图论 | 手写 `dist` 数组 + `heapq`，不要 `networkx` |
| 并查集 | 列表 `fa` + 路径压缩，10 行 |
| 高精度 | Python 自带大整数，直接用 |
| 位运算 | 直接用 `&`、`|`、`^`、`~`、`<<`、`>>`，注意 `~x == -x - 1` |
| 排序 | `a.sort()`；需要多关键字用 `key=lambda x: (x[0], -x[1])` |
| 计数 | `collections.Counter` 可以，但数组计数更快 |

## 性能底线

| 数据量 | 允许 | 不允许 |
|---|---|---|
| n ≤ 1e5 | O(n log n) 正常 | O(n²) |
| n ≤ 1e6 | O(n) 且常数小 | 循环里做 `in list`、切片、字符串拼接 |
| n ≤ 1e7 | 基本只能纯数组 + 位运算 | 任何对象创建 |

PyPy 下常数快 3~10 倍，但题解按 CPython 写保守版本。

## 不要做的事

- ❌ 把 C++ 的 `for (int i = 0; i < n; i++)` 直译成带 `while` 和下标自增的怪写法。
- ❌ 用 `class Solution` 包一层（LeetCode 才需要，题解里不需要）。
- ❌ 注释。一个都不写。
