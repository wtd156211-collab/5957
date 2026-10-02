"""最小编辑脚本，并列选择规则固定，结果确定且可复现。

规则（见 README）：在所有最长公共子序列中，取「按 base 一侧下标逐个
比较最小」的那一个，即尽量早地保留 base 里的元素。

算法：把 LCS 归约为最长上升子序列（LIS）——按 base 顺序列出每个元素
在另一侧出现的位置（同一段内位置降序），则 LCS 一一对应于该序列的
LIS。「base 下标字典序最小」对应「LIS 元素位置字典序最小」，用
Fenwick 树求出每个位置向后能延伸的最长上升长度后，从左到右贪心选取
可行位置即可精确构造，不是近似的并列启发式。

复杂度：O((n + r) log m)，其中 r 是两个序列中值相同的元素对总数；
配置文件里行基本唯一，r ≈ n，实际接近线性。
"""


def edit_script(a, b):
    """计算 a -> b 的最小编辑脚本。

    返回操作列表：('eq', i, j) 保留 a[i]（对应 b[j]）、('del', i) 删除
    a[i]、('ins', j) 插入 b[j]。同一空档内先删后插；空档内部顺序不影响
    hunk 划分与词级配对。
    """
    n, m = len(a), len(b)

    # 只能裁公共前缀：规则要求尽量早地保留 base 元素，公共前缀必然
    # 出现在选定的子序列里；公共后缀则未必（重复元素时规则会选中靠前
    # 的出现而不是靠后的），裁后缀会改变结果。
    start = 0
    while start < n and start < m and a[start] == b[start]:
        start += 1

    pairs = [(t, t) for t in range(start)]
    pairs.extend(
        (i + start, j + start)
        for i, j in _matched_pairs(a[start:], b[start:])
    )

    ops = []
    pa = pb = 0
    for i, j in pairs:
        while pa < i:
            ops.append(('del', pa))
            pa += 1
        while pb < j:
            ops.append(('ins', pb))
            pb += 1
        ops.append(('eq', i, j))
        pa = i + 1
        pb = j + 1
    while pa < n:
        ops.append(('del', pa))
        pa += 1
    while pb < m:
        ops.append(('ins', pb))
        pb += 1
    return ops


def _matched_pairs(a, b):
    """返回规则选定的公共子序列，元素为 (a 下标, b 下标)，按下标升序。"""
    positions = {}
    for j, value in enumerate(b):
        positions.setdefault(value, []).append(j)

    seq_val = []   # 每个匹配候选的 b 下标
    seq_ai = []    # 每个匹配候选的 a 下标
    for i, value in enumerate(a):
        found = positions.get(value)
        if found:
            for j in reversed(found):
                seq_val.append(j)
                seq_ai.append(i)

    size = len(seq_val)
    if size == 0:
        return []

    m = len(b)
    # Fenwick 树，坐标取 c = m - 1 - j，把「j 严格更大」变成前缀最大值查询
    bit = [0] * (m + 1)
    length = [0] * size

    for p in range(size - 1, -1, -1):
        c = m - 1 - seq_val[p]
        best = 0
        q = c
        while q > 0:
            if bit[q] > best:
                best = bit[q]
            q -= q & -q
        current = best + 1
        length[p] = current
        q = c + 1
        while q <= m:
            if current > bit[q]:
                bit[q] = current
            q += q & -q

    total = 0
    for p in range(size):
        if length[p] > total:
            total = length[p]

    pairs = []
    remaining = total
    min_j = -1
    pos = -1
    while remaining > 0:
        p = pos + 1
        # 线性扫描被跳过的位置都排在已选位置之前，之后不会再看，
        # 因此整个贪心合计 O(r)。
        while seq_val[p] <= min_j or length[p] < remaining:
            p += 1
        pairs.append((seq_ai[p], seq_val[p]))
        min_j = seq_val[p]
        pos = p
        remaining -= 1
    return pairs
