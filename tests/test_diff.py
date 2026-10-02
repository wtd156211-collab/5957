import random
import unittest

from cfgmerge import diff_hunks, diff_text, edit_script, word_change


def brute_lcs_base_indices(a, b):
    """暴力求「按 a 下标字典序最小」的最长公共子序列（仅用于小输入对照）。"""
    n, m = len(a), len(b)
    length = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                length[i][j] = length[i + 1][j + 1] + 1
            else:
                length[i][j] = max(length[i + 1][j], length[i][j + 1])
    indices = []
    i = j = 0
    while i < n and j < m and length[i][j] > 0:
        found = False
        for ip in range(i, n):
            for jp in range(j, m):
                if a[ip] == b[jp] and length[ip][jp] == length[i][j]:
                    indices.append(ip)
                    i, j = ip + 1, jp + 1
                    found = True
                    break
            if found:
                break
    return indices


def apply_script(a, b, ops):
    """把编辑脚本应用到 a，应得到 b。"""
    result = []
    for op in ops:
        if op[0] == 'eq':
            assert a[op[1]] == b[op[2]]
            result.append(a[op[1]])
        elif op[0] == 'ins':
            result.append(b[op[1]])
    return result


class EditScriptTest(unittest.TestCase):
    def test_readme_tiebreak_example(self):
        # README：base = x a，另一侧 = a x，取「保留 base 第 1 行的 x」
        ops = edit_script(['x', 'a'], ['a', 'x'])
        kept = [i for op in ops if op[0] == 'eq' for i in [op[1]]]
        self.assertEqual(kept, [0])
        self.assertEqual(apply_script(['x', 'a'], ['a', 'x'], ops), ['a', 'x'])

    def test_minimal_script_length(self):
        rng = random.Random(2024)
        for _ in range(300):
            a = [rng.randrange(4) for _ in range(rng.randrange(9))]
            b = [rng.randrange(4) for _ in range(rng.randrange(9))]
            ops = edit_script(a, b)
            edits = sum(1 for op in ops if op[0] != 'eq')
            lcs_len = len(brute_lcs_base_indices(a, b))
            self.assertEqual(edits, len(a) + len(b) - 2 * lcs_len)
            self.assertEqual(apply_script(a, b, ops), b)

    def test_tiebreak_matches_brute_force(self):
        rng = random.Random(7)
        for _ in range(500):
            a = [rng.randrange(3) for _ in range(rng.randrange(9))]
            b = [rng.randrange(3) for _ in range(rng.randrange(9))]
            ops = edit_script(a, b)
            kept = [op[1] for op in ops if op[0] == 'eq']
            self.assertEqual(kept, brute_lcs_base_indices(a, b),
                             msg='a={} b={}'.format(a, b))

    def test_deterministic(self):
        rng = random.Random(99)
        for _ in range(50):
            a = [rng.randrange(5) for _ in range(rng.randrange(20))]
            b = [rng.randrange(5) for _ in range(rng.randrange(20))]
            self.assertEqual(edit_script(a, b), edit_script(a, b))

    def test_empty_inputs(self):
        self.assertEqual(edit_script([], []), [])
        self.assertEqual(edit_script([], ['a']), [('ins', 0)])
        self.assertEqual(edit_script(['a'], []), [('del', 0)])


class HunkTest(unittest.TestCase):
    def test_pure_insertion_header(self):
        hunks = diff_hunks(['a', 'b'], ['a', 'x', 'b'])
        self.assertEqual([(h.tag, h.base_start, h.base_count,
                           h.other_start, h.other_count) for h in hunks],
                         [('equal', 0, 1, 0, 1),
                          ('change', 1, 0, 1, 1),
                          ('equal', 1, 1, 2, 1)])

    def test_pure_deletion_header(self):
        hunks = diff_hunks(['a', 'x', 'b'], ['a', 'b'])
        self.assertEqual([(h.tag, h.base_start, h.base_count,
                           h.other_start, h.other_count) for h in hunks],
                         [('equal', 0, 1, 0, 1),
                          ('change', 1, 1, 1, 0),
                          ('equal', 2, 1, 1, 1)])

    def test_identical_files(self):
        self.assertEqual(diff_text(['a', 'b'], ['a', 'b']),
                         'equal,1,2,1,2\n')
        self.assertEqual(diff_text([], []), '')

    def test_diff_text_renders_words(self):
        text = diff_text(['timeout: 30'], ['timeout: 60'])
        self.assertEqual(text, 'change,1,1,1,1\nwords,1,1,30,60\n')

    def test_diff_text_one_sided_words(self):
        text = diff_text(['a', 'gone line'], ['a'])
        self.assertEqual(
            text,
            'equal,1,1,1,1\n'
            'change,2,1,2,0\n'
            'words,2,,gone line,\n')

    def test_diff_text_insertion_words(self):
        text = diff_text(['a'], ['a', 'new line'])
        self.assertEqual(
            text,
            'equal,1,1,1,1\n'
            'change,2,0,2,1\n'
            'words,,2,,new line\n')


class WordChangeTest(unittest.TestCase):
    def test_single_number_change(self):
        deleted, inserted = word_change('  timeout: 30', '  timeout: 60')
        self.assertEqual(deleted, ['30'])
        self.assertEqual(inserted, ['60'])

    def test_no_change(self):
        self.assertEqual(word_change('a b c', 'a b c'), ([], []))

    def test_inserted_word(self):
        deleted, inserted = word_change('key: value', 'key: value extra')
        self.assertEqual(deleted, [])
        self.assertEqual(inserted, ['extra'])


if __name__ == '__main__':
    unittest.main()
