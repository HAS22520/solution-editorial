# 滑动窗口最大值

## 题意

给定长度 n 的整数序列 a 与窗口长度 k（1 ≤ k ≤ n ≤ 10^6，|a_i| ≤ 10^9），对每个长度恰为 k 的连续下标区间，输出其中元素的最大值。

## 思路

暴力做法是每个窗口扫一遍，O(nk)，在 n = 10^6 时必然超时。要利用"窗口右移一格只进一个、只出一个"这个结构。

观察：若 i < j 且 a_i ≤ a_j，则 i 在任何还包含 j 的窗口里都不可能成为最大值——它比 j 小，又比 j 先离开窗口。这类下标可以永久丢弃，每个元素只被"后来者"支配一次。

于是维护一个下标队列 q，满足两个不变量：q 中下标都落在当前窗口内，且 a[q] 严格递减。每个 i 到来时先弹出队尾所有 a 值不大于 a_i 的下标（它们被 i 支配），再把 i 入队；随后弹出已经滑出窗口的队首（q[head] ≤ i − k）。窗口成型后，队首即窗口最大值。

正确性：被弹出的元素被更新的更大元素支配，不可能成为任何后续窗口的最大值，故不会漏解；队首是队列中最大的下标，而所有可能比它大的元素都已被支配淘汰，故队首就是当前窗口的最大值，不会错解。

复杂度：每个下标至多入队、出队各一次，时间 O(n)；队列 O(n)，输入数组 O(n)。三份代码统一使用 1-based 下标，保证输出逐字节一致。

## 代码

### C++

```cpp
#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;

int n, k;
int a[MAXN], q[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n >> k;
    for (int i = 1; i <= n; i++) {
        cin >> a[i];
    }
    int head = 0, tail = 0;
    for (int i = 1; i <= n; i++) {
        while (head < tail && a[q[tail - 1]] <= a[i]) {
            tail--;
        }
        q[tail++] = i;
        if (q[head] <= i - k) {
            head++;
        }
        if (i >= k) {
            cout << a[q[head]];
            cout << (i == n ? "\n" : " ");
        }
    }
    return 0;
}
```

### C

```c
#include <stdio.h>

#define MAXN 1000005

int n, k;
int a[MAXN], q[MAXN];

int main(void) {
    scanf("%d%d", &n, &k);
    for (int i = 1; i <= n; i++) {
        scanf("%d", &a[i]);
    }
    int head = 0, tail = 0;
    for (int i = 1; i <= n; i++) {
        while (head < tail && a[q[tail - 1]] <= a[i]) {
            tail--;
        }
        q[tail++] = i;
        if (q[head] <= i - k) {
            head++;
        }
        if (i >= k) {
            printf("%d", a[q[head]]);
            printf("%s", i == n ? "\n" : " ");
        }
    }
    return 0;
}
```

### Python

```python
import sys
from collections import deque

def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, k = data[0], data[1]
    a = [0] + data[2:2 + n]
    q = deque()
    out = []
    for i in range(1, n + 1):
        while q and a[q[-1]] <= a[i]:
            q.pop()
        q.append(i)
        if q[0] <= i - k:
            q.popleft()
        if i >= k:
            out.append(str(a[q[0]]))
    sys.stdout.write(" ".join(out) + "\n")

main()
```
