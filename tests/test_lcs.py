import random
import unittest

from configmerge.lcs import common_subsequence_matches


def brute_force_matches(a, b):
    """用 O(n*m) 动态规划直接实现 README 的选路规则，作为对照 oracle。"""
    n, m = len(a), len(b)
    # L[i][j] = LCS(a[i:], b[j:]) 的长度
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                L[i][j] = max(L[i + 1][j], L[i][j + 1], L[i + 1][j + 1] + 1)
            else:
                L[i][j] = max(L[i + 1][j], L[i][j + 1])
    matches = []
    i = j = 0
    while i < n and j < m:
        matched = False
        for t in range(j, m):
            if b[t] == a[i] and L[i][j] == 1 + L[i + 1][t + 1]:
                matches.append((i, t))
                i += 1
                j = t + 1
                matched = True
                break
        if not matched:
            i += 1
    return matches, L[0][0]


class TestLcsRule(unittest.TestCase):
    def test_readme_example(self):
        # README：base = x a，另一侧 = a x，取「保留 x，删除 a，插入 x」
        self.assertEqual(common_subsequence_matches(["x", "a"], ["a", "x"]), [(0, 1)])

    def test_empty(self):
        self.assertEqual(common_subsequence_matches([], []), [])
        self.assertEqual(common_subsequence_matches(["a"], []), [])
        self.assertEqual(common_subsequence_matches([], ["a"]), [])

    def test_identical(self):
        lines = ["a", "b", "c"]
        self.assertEqual(common_subsequence_matches(lines, lines), [(0, 0), (1, 1), (2, 2)])

    def test_no_common_lines(self):
        self.assertEqual(common_subsequence_matches(["a", "b"], ["c", "d"]), [])

    def test_earliest_base_match_wins(self):
        # LCS 长度都是 2：{base1,base3}=a a 与 {base2,base3}=b a，取 base 下标更小者
        matches = common_subsequence_matches(["a", "b", "a"], ["b", "a", "a"])
        self.assertEqual(matches, [(0, 1), (2, 2)])

    def test_matches_brute_force_on_random_inputs(self):
        rng = random.Random(20260923)
        for _ in range(600):
            n = rng.randint(0, 10)
            m = rng.randint(0, 10)
            a = [rng.choice("abcd") for _ in range(n)]
            b = [rng.choice("abcd") for _ in range(m)]
            expected, max_len = brute_force_matches(a, b)
            got = common_subsequence_matches(a, b)
            self.assertEqual(got, expected, msg=f"a={a} b={b}")
            # 合法性：下标递增、值相等、长度达到最长
            self.assertEqual(len(got), max_len)
            for (i, j) in got:
                self.assertEqual(a[i], b[j])
            self.assertEqual([i for i, _ in got], sorted(i for i, _ in got))
            self.assertEqual([j for _, j in got], sorted(j for _, j in got))

    def test_deterministic(self):
        rng = random.Random(7)
        a = [str(rng.randint(0, 50)) for _ in range(300)]
        b = [str(rng.randint(0, 50)) for _ in range(300)]
        self.assertEqual(common_subsequence_matches(a, b), common_subsequence_matches(a, b))


if __name__ == "__main__":
    unittest.main()
