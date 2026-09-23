"""最长公共子序列（LCS）匹配，实现 README 规定的选路规则。

规则：在所有最长公共子序列里，取「按 base 行号逐个比较最小」的那一个
（优先保留靠前的匹配）；base 侧确定后，另一侧的下标同样取最早可行位置，
保证同一份输入永远得到同一个结果。

实现：位并行 LCS（bit-parallel，把 Python 大整数当位向量），
复杂度 O(n * m / 64)，不是逐行两两比较的平方级。
"""

try:
    _popcount = int.bit_count  # Python 3.10+
except AttributeError:  # pragma: no cover
    def _popcount(x):
        return bin(x).count("1")


def common_subsequence_matches(a, b):
    """返回 (base 下标, 另一侧下标) 的匹配对列表（各自递增）。

    匹配对即选定的最长公共子序列；不在匹配里的 base 行是删除，
    不在匹配里的另一侧行是插入。
    """
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return []

    # 公共前缀直接匹配，缩小问题规模：a[0]==b[0] 时必存在包含 (0,0)
    # 的最长公共子序列，因此逐个匹配前缀与选路规则等价。
    # （公共后缀不能这样裁：末尾的匹配可能「抢走」按规则应属于
    # 更靠前 base 行的匹配，改变结果。）
    pre = 0
    limit = min(n, m)
    while pre < limit and a[pre] == b[pre]:
        pre += 1

    matches = [(i, i) for i in range(pre)]
    matches.extend((i + pre, j + pre) for i, j in _matches_core(a[pre:], b[pre:]))
    return matches


def _matches_core(a, b):
    """对去掉公共前后缀后的中段求匹配对。"""
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return []

    # 只出现在一侧的行不可能进入公共子序列，先过滤掉（保持相对顺序，
    # 下标单调映射，因此与「按 base 行号最小」的选法等价）。
    common = set(a) & set(b)
    if not common:
        return []
    a_idx = [i for i, v in enumerate(a) if v in common]
    b_idx = [j for j, v in enumerate(b) if v in common]
    af = [a[i] for i in a_idx]
    bf = [b[j] for j in b_idx]

    return [(a_idx[i], b_idx[j]) for i, j in _filtered_matches(af, bf)]


def _filtered_matches(af, bf):
    """位并行 LCS + 从头到尾的贪心匹配。"""
    from bisect import bisect_left

    n, m = len(af), len(bf)

    # 后缀 LCS 长度查询表：把两个序列都反转后做位并行前缀 DP。
    # ar = reversed(af)，br = reversed(bf)；处理完 br[:p] 后的状态 S 满足：
    # S 的低 q 位中置位数 == LCS(ar[:q], br[:p]) 的长度。
    # 于是 L(i, j) = LCS(af[i:], bf[j:]) = popcount(SR[m-j] & ((1<<(n-i))-1))。
    masks = {}
    for k, v in enumerate(reversed(af)):
        masks[v] = masks.get(v, 0) | (1 << k)

    rows = [0] * (m + 1)
    state = 0
    for p in range(1, m + 1):
        x = masks.get(bf[m - p], 0) | state
        state = x & ~(x - ((state << 1) | 1))
        rows[p] = state

    full = (1 << n) - 1

    def suffix_lcs_len(i, j):
        return _popcount(rows[m - j] & (full >> i))

    # 另一侧每个值出现的下标（有序），用于查「>= j 的最早出现位置」。
    positions = {}
    for j, v in enumerate(bf):
        positions.setdefault(v, []).append(j)

    # 贪心：base 当前行若能出现在某个最长公共子序列里，就匹配它
    # （取另一侧最早可行位置）；否则删除它。这正好给出
    # 「按 base 行号逐个比较最小」的最长公共子序列。
    matches = []
    i = j = 0
    while i < n and j < m:
        pos_list = positions[af[i]]
        k = bisect_left(pos_list, j)
        if k < len(pos_list):
            j2 = pos_list[k]
            if suffix_lcs_len(i, j) == 1 + suffix_lcs_len(i + 1, j2 + 1):
                matches.append((i, j2))
                i += 1
                j = j2 + 1
                continue
        i += 1
    return matches
