import unittest

from configmerge import merge, render_merge


class TestMergeRules(unittest.TestCase):
    def test_disjoint_regions_auto_merge(self):
        base = ["a", "b", "c"]
        ours = ["A", "b", "c"]
        theirs = ["a", "b", "C"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(lines, ["A", "b", "C"])
        self.assertEqual(conflicts, [])

    def test_adjacent_lines_not_a_conflict(self):
        # 一个改第 2 行、另一个改第 3 行：紧挨着但不相撞
        base = ["a", "b", "c", "d"]
        ours = ["a", "B", "c", "d"]
        theirs = ["a", "b", "C", "d"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(lines, ["a", "B", "C", "d"])
        self.assertEqual(conflicts, [])

    def test_identical_changes_merge_once(self):
        base = ["a", "b"]
        ours = ["a", "B"]
        theirs = ["a", "B"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(lines, ["a", "B"])
        self.assertEqual(conflicts, [])

    def test_only_one_side_changed(self):
        base = ["a", "b"]
        lines, conflicts = merge(base, base, ["a", "B"])
        self.assertEqual(lines, ["a", "B"])
        self.assertEqual(conflicts, [])

    def test_same_line_same_position_conflicts(self):
        base = ["a", "b", "c"]
        lines, conflicts = merge(base, ["a", "X", "c"], ["a", "Y", "c"])
        self.assertEqual(
            lines,
            ["a", "<<<<<<< ours", "X", "||||||| base", "b", "=======", "Y",
             ">>>>>>> theirs", "c"],
        )
        self.assertEqual(conflicts, [(2, 1)])

    def test_pure_insert_conflict_position(self):
        # 同一位置各插不同内容：起行 = 插入点后面那一行，行数 0
        base = ["a", "b", "c"]
        lines, conflicts = merge(base, ["a", "b", "X", "c"], ["a", "b", "Y", "c"])
        self.assertEqual(conflicts, [(3, 0)])
        self.assertEqual(
            lines,
            ["a", "b", "<<<<<<< ours", "X", "||||||| base", "=======", "Y",
             ">>>>>>> theirs", "c"],
        )

    def test_insert_at_end_conflict_start_line(self):
        # 插在文件末尾：起行 = base 行数 + 1
        base = ["a", "b"]
        lines, conflicts = merge(base, ["a", "b", "X"], ["a", "b", "Y"])
        self.assertEqual(conflicts, [(3, 0)])

    def test_delete_vs_edit_same_line_conflicts(self):
        base = ["a", "b", "c"]
        lines, conflicts = merge(base, ["a", "c"], ["a", "B", "c"])
        self.assertEqual(conflicts, [(2, 1)])
        self.assertEqual(
            lines,
            ["a", "<<<<<<< ours", "||||||| base", "b", "=======", "B",
             ">>>>>>> theirs", "c"],
        )

    def test_insert_at_edge_of_changed_region_is_fine(self):
        # ours 改第 2 行；theirs 在第 2 行前面插入：不算撞上
        base = ["a", "b", "c"]
        ours = ["a", "B", "c"]
        theirs = ["a", "N", "b", "c"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(lines, ["a", "N", "B", "c"])
        self.assertEqual(conflicts, [])

    def test_insert_inside_changed_region_conflicts(self):
        # ours 改第 2、3 行；theirs 插到这段内部：撞上
        base = ["a", "b", "c", "d"]
        ours = ["a", "B", "C", "d"]
        theirs = ["a", "b", "N", "c", "d"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(conflicts, [(2, 2)])

    def test_same_insertion_same_content_merges(self):
        base = ["a", "b"]
        lines, conflicts = merge(base, ["a", "N", "b"], ["a", "N", "b"])
        self.assertEqual(lines, ["a", "N", "b"])
        self.assertEqual(conflicts, [])

    def test_overlapping_multi_line_conflict_span(self):
        # ours 改 2-3 行，theirs 改 3-4 行：区间重叠，冲突覆盖 base 2-4 行
        base = ["a", "b", "c", "d", "e"]
        ours = ["a", "B", "C", "d", "e"]
        theirs = ["a", "b", "C2", "D", "e"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(conflicts, [(2, 3)])
        self.assertEqual(
            lines,
            ["a", "<<<<<<< ours", "B", "C", "d", "||||||| base", "b", "c", "d",
             "=======", "b", "C2", "D", ">>>>>>> theirs", "e"],
        )

    def test_multiple_conflicts_listed_in_order(self):
        base = ["a", "b", "c", "d", "e"]
        ours = ["A", "b", "c", "D", "e"]
        theirs = ["A2", "b", "c", "D2", "e"]
        lines, conflicts = merge(base, ours, theirs)
        self.assertEqual(conflicts, [(1, 1), (4, 1)])

    def test_empty_base(self):
        lines, conflicts = merge([], ["x"], ["y"])
        self.assertEqual(conflicts, [(1, 0)])
        lines2, conflicts2 = merge([], ["x"], ["x"])
        self.assertEqual((lines2, conflicts2), (["x"], []))

    def test_render_includes_conflict_summary(self):
        base = ["a", "b", "c"]
        out = render_merge(base, ["a", "X", "c"], ["a", "Y", "c"])
        self.assertTrue(out.endswith("# conflicts\nconflict,2,1\n"))

    def test_render_no_conflicts_has_no_summary(self):
        out = render_merge(["a"], ["a"], ["a"])
        self.assertEqual(out, "a\n")

    def test_deterministic(self):
        base = ["k%d: %d" % (i, i) for i in range(200)]
        ours = base[:]
        theirs = base[:]
        ours[50] = "k50: ours"
        theirs[50] = "k50: theirs"
        theirs[120] = "k120: theirs"
        first = render_merge(base, ours, theirs)
        second = render_merge(base, ours, theirs)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
