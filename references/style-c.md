# C 模板与规则

## 模板

```c
#include <stdio.h>
#include <string.h>

#define MAXN 100005

int n, m;
int a[MAXN];

int main(void) {
    scanf("%d%d", &n, &m);
    for (int i = 1; i <= n; i++) {
        scanf("%d", &a[i]);
    }
    int ans = 0;
    for (int i = 1; i <= n; i++) {
        if (a[i] > ans) {
            ans = a[i];
        }
    }
    printf("%d\n", ans);
    return 0;
}
```

## 硬规则

- 常量用 `#define MAXN ...` 或 `enum { MAXN = ... }`；不用 `const int` 开数组（部分编译器下不能作数组长度）。
- 数组一律全局，函数内大数组爆栈。
- `int main(void)`，末尾 `return 0;`。
- C99 起允许 `for (int i = 0; ...)`；若目标编译器很老，把声明提到块首。
- 没有 `bool`：用 `int`（0/1）。真要 `bool` 就 `#include <stdbool.h>`，全文统一。
- 没有引用、没有 `auto`、没有模板、没有 `//` 注释（本技能本来就零注释）。

## 与 C++ 的隔离检查

从 C++ 改写成 C 时最容易漏这四处，写完逐条过：

| C++ 写法 | C 里必须改成 |
|---|---|
| `#include <bits/stdc++.h>` | 具体头文件：`stdio.h`、`string.h`、`stdlib.h`、`math.h` |
| `vector<int> v(n)` | `int v[MAXN];` 或 `malloc(n * sizeof(int))` |
| `bool` | `int` 或 `#include <stdbool.h>` |
| `cin >> x` / `cout << x` | `scanf` / `printf` |
| 引用参数 `int &x` | 指针 `int *x` |
| 默认参数、重载 | 拆成不同函数名或加参数 |

**验证**：`gcc -std=c11 -O2 -Wall x.c -o x` 必须零错误；有 `bool` 没头文件、有 `//`、有 VLA 都会在这里暴露。

## 输入输出

| 类型 | 格式 |
|---|---|
| `int` | `%d` |
| `long long` | `%lld`（MSVC 用 `%I64d`，评测机一般是 gcc，用 `%lld`） |
| `double` | `%lf` 读入，`%f` 输出 |
| 字符串 | `%s`，不要用 `gets`；要读整行用 `fgets` |
| 字符 | `%c`，注意前面残留的换行 |

多组数据要 `while (scanf("%d", &n) != EOF)` 或 `while (~scanf("%d", &n))`，不要写成只读一次。

**大输出**：`printf` 循环调用在 1e6 行时会慢，缓存到 `char buf[]` 再一次性 `fwrite`。

## 内存

| 需求 | 写法 |
|---|---|
| 清零 | `memset(a, 0, sizeof(a))` |
| 设 INF | `memset(d, 0x3f, sizeof(d))`（得到 1.06e9 量级） |
| 判 INF | `d[x] == 0x3f3f3f3f` |
| 二维数组 | `int g[MAXN][MAXN]` 只在 N ≤ 2000 时用，否则换邻接表 |

`memset` 按字节赋值，只能可靠地设 0、-1、0x3f；不要用 `memset` 设 1 或其它数。

## 不要做的事

- ❌ VLA（`int a[n];` 且 n 是变量）：老编译器不支持，且爆栈难查。
- ❌ `gets`：已废弃，缓冲区溢出。
- ❌ `scanf` 不检查返回值导致读入错位。
- ❌ 用 `int` 存 `long long` 范围的答案。
- ❌ 注释。一个都不写。
