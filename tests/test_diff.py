import unittest

from configmerge import diff_hunks, render_diff, split_lines, word_diff


class TestSplitLines(unittest.TestCase):
    def test_empty_file_is_zero_lines(self):
        self.assertEqual(split_lines(""), [])

    def test_trailing_newline_does_not_add_line(self):
        self.assertEqual(split_lines("a\nb\n"), ["a", "b"])

    def test_no_trailing_newline(self):
        self.assertEqual(split_lines("a\nb"), ["a", "b"])

    def test_blank_lines_kept(self):
        self.assertEqual(split_lines("a\n\nb\n"), ["a", "", "b"])


class TestWordDiff(unittest.TestCase):
    def test_single_number_change_is_word_level(self):
        deleted, inserted = word_diff("  timeout: 30", "  timeout: 60")
        self.assertEqual(deleted, ["30"])
        self.assertEqual(inserted, ["60"])

    def test_no_change(self):
        self.assertEqual(word_diff("a b c", "a b c"), ([], []))

    def test_insert_word(self):
        self.assertEqual(word_diff("a c", "a b c"), ([], ["b"]))


class TestDiffHunks(unittest.TestCase):
    def test_readme_example_script(self):
        # base = x a, other = a x：保留 x，删除 a，插入 x（插到最前的是 a）
        hunks = diff_hunks(["x", "a"], ["a", "x"])
        self.assertEqual(
            hunks,
            [
                ("change", 0, 0, 0, 1),
                ("equal", 0, 1, 1, 1),
                ("change", 1, 1, 2, 0),
            ],
        )

    def test_pure_insertion_hunk(self):
        hunks = diff_hunks(["a", "b"], ["a", "x", "b"])
        self.assertEqual(
            hunks,
            [("equal", 0, 1, 0, 1), ("change", 1, 0, 1, 1), ("equal", 1, 1, 2, 1)],
        )

    def test_pure_deletion_hunk(self):
        hunks = diff_hunks(["a", "x", "b"], ["a", "b"])
        self.assertEqual(
            hunks,
            [("equal", 0, 1, 0, 1), ("change", 1, 1, 1, 0), ("equal", 2, 1, 1, 1)],
        )

    def test_empty_files(self):
        self.assertEqual(diff_hunks([], []), [])
        self.assertEqual(render_diff([], []), "")


class TestRenderDiff(unittest.TestCase):
    def test_equal_only(self):
        self.assertEqual(render_diff(["a", "b"], ["a", "b"]), "equal,1,2,1,2\n")

    def test_change_with_words(self):
        out = render_diff(["server:", "  timeout: 30"], ["server:", "  timeout: 60"])
        self.assertEqual(
            out,
            "equal,1,1,1,1\n"
            "change,2,1,2,1\n"
            "words,2,2,30,60\n",
        )

    def test_pure_insertion_rendering(self):
        out = render_diff(["a", "b"], ["a", "x y", "b"])
        self.assertEqual(
            out,
            "equal,1,1,1,1\n"
            "change,2,0,2,1\n"
            "words,,2,,x y\n"
            "equal,2,1,3,1\n",
        )

    def test_pure_deletion_rendering(self):
        out = render_diff(["a", "x y", "b"], ["a", "b"])
        self.assertEqual(
            out,
            "equal,1,1,1,1\n"
            "change,2,1,2,0\n"
            "words,2,,x y,\n"
            "equal,3,1,2,1\n",
        )

    def test_extra_lines_on_one_side(self):
        out = render_diff(["a", "b"], ["a", "b", "c", "d"])
        self.assertEqual(
            out,
            "equal,1,2,1,2\n"
            "change,3,0,3,2\n"
            "words,,3,,c\n"
            "words,,4,,d\n",
        )

    def test_paired_and_unpaired_lines(self):
        # 一对位置对应的变更行 + 另一侧多出一行
        out = render_diff(["k: 1", "z"], ["k: 2", "y", "w"])
        self.assertEqual(
            out,
            "change,1,2,1,3\n"
            "words,1,1,1,2\n"
            "words,2,2,z,y\n"
            "words,,3,,w\n",
        )


if __name__ == "__main__":
    unittest.main()
