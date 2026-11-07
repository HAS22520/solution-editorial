# C++ 模板与规则

## 模板

```cpp
#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;

int n, m;
int a[MAXN];

void read() {
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; i++) {
        scanf("%d", &a[i]);
    }
}

int solve() {
    int ans = 0;
    for (int i = 1; i <= n; i++) {
        if (a[i] > ans) {
            ans = a[i];
        }
    }
    return ans;
}

int main() {
    read();
    printf("%d\n", solve());
    return 0;
}
```

`read` / `solve` / `main` 三段是骨架，题目简单就合并，不要为了凑结构硬拆。

## 硬规则

- 常量大写 `MAXN`，值取题目上限 +2（防 `+1` 越界）。
- 大数组放全局：函数内开 `int a[100005]` 会爆栈。
- 下标从 1 开始（图、DP、树），从 0 开始（纯数组扫描）。同一篇里保持一致。
- 变量在**首次使用处**声明；`for` 里直接声明循环变量。
- 用 `while` 写双指针，用 `for` 写定次数扫描。不要用 `while` 硬凑 `for`。
- 三元能压一行就压：`ans = max(ans, pre + a[i]);` 比四行 `if` 好。
- 输出用 `'\n'`，不用 `endl`（每次 flush）。

## 输入输出

| 场景 | 写法 |
|---|---|
| 数据量大（≥1e5） | `ios::sync_with_stdio(false); cin.tie(nullptr);` + `cin/cout` |
| 混合格式、需要精确控制 | `scanf/printf` |
| 读到文件尾 | `while (cin >> n >> m) { ... }` |
| 多组数据 | 每组开头重置全局数组（`memset` 或 `fill`），并重置计数器 |

`scanf` 与 `cin` **不要混用**：关掉同步之后混用是未定义行为。

## 类型与溢出

| 判断 | 做法 |
|---|---|
| 和可能超过 2×10^9 | `long long` |
| 有乘法 | `1LL * a * b`，先转再乘 |
| 有减法取模 | `(x % MOD + MOD) % MOD` |
| 计数 | `long long`，读完再取模 |

`int` 上限约 2.1×10^9，`unsigned int` 约 4.2×10^9；题解说"答案对 1e9+7 取模"时中间量也要开 `long long`。

## 数据结构选型

| 需求 | 用什么 |
|---|---|
| 定长队列/栈 | 数组 + `head/tail`，不用 `std::queue` |
| 滑动窗口最值 | 数组手写单调队列 |
| 动态最值 | `priority_queue`，需要改键时手写堆 + `where[]` |
| 图 | 链式前向星：`head[] / nxt[] / to[] / weight[] / cnt` |
| 有序集合 | `set`、`map`；能离散化就用数组 |
| 并查集 | `fa[]` + 路径压缩 + 按大小合并 |

## 不要做的事

- ❌ `std::function` 递归、lambda 捕获、`auto` 泛滥。读者要一眼看懂。
- ❌ `vector<vector<int>>` 建大图（1e6 边时会 TLE 在分配上），用前向星。
- ❌ 模板元编程、宏函数、`#pragma`。
- ❌ 用 `std::sort` + 自定义比较器写复杂贪心时不用 `const&` 传参。
- ❌ 注释。一个都不写。

## bits/stdc++.h 的使用边界

题解里默认可用（洛谷、Codeforces、Nowcoder 的 g++ 都支持）。若用户明确说目标是 MSVC 或某平台不支持，改为显式头文件：

```cpp
#include <iostream>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <vector>
#include <queue>
```
