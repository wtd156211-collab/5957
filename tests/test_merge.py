import unittest

from cfgmerge import merge3, merge_text


class MergeRuleTest(unittest.TestCase):
    def test_disjoint_regions_auto_merge(self):
        base = ['a', 'b', 'c', 'd']
        ours = ['A', 'b', 'c', 'd']
        theirs = ['a', 'b', 'c', 'D']
        lines, conflicts = merge3(base, ours, theirs)
        self.assertEqual(lines, ['A', 'b', 'c', 'D'])
        self.assertEqual(conflicts, [])

    def test_adjacent_lines_not_conflict(self):
        base = ['a', 'b', 'c']
        ours = ['a', 'B', 'c']
        theirs = ['a', 'b', 'C']
        lines, conflicts = merge3(base, ours, theirs)
        self.assertEqual(lines, ['a', 'B', 'C'])
        self.assertEqual(conflicts, [])

    def test_identical_change_merged_once(self):
        base = ['a', 'b']
        ours = ['a', 'X']
        theirs = ['a', 'X']
        lines, conflicts = merge3(base, ours, theirs)
        self.assertEqual(lines, ['a', 'X'])
        self.assertEqual(conflicts, [])

    def test_only_one_side_changed(self):
        base = ['a', 'b']
        lines, conflicts = merge3(base, base, ['a', 'B'])
        self.assertEqual(lines, ['a', 'B'])
        self.assertEqual(conflicts, [])
        lines, conflicts = merge3(base, ['A', 'b'], base)
        self.assertEqual(lines, ['A', 'b'])
        self.assertEqual(conflicts, [])

    def test_same_line_conflict(self):
        lines, conflicts = merge3(['a', 'b'], ['a', 'X'], ['a', 'Y'])
        self.assertEqual(lines, [
            'a',
            '<<<<<<< ours',
            'X',
            '||||||| base',
            'b',
            '=======',
            'Y',
            '>>>>>>> theirs',
        ])
        self.assertEqual(conflicts, [(2, 1)])

    def test_pure_insert_conflict_line_number(self):
        base = ['a', 'b', 'c']
        lines, conflicts = merge3(base,
                                  ['a', 'b', 'X', 'c'],
                                  ['a', 'b', 'Y', 'c'])
        self.assertEqual(conflicts, [(3, 0)])
        self.assertEqual(lines, [
            'a', 'b',
            '<<<<<<< ours',
            'X',
            '||||||| base',
            '=======',
            'Y',
            '>>>>>>> theirs',
            'c',
        ])

    def test_insert_at_end_of_file_conflict_line_number(self):
        base = ['a', 'b']
        _, conflicts = merge3(base, ['a', 'b', 'X'], ['a', 'b', 'Y'])
        self.assertEqual(conflicts, [(3, 0)])

    def test_same_insert_same_content_merged(self):
        lines, conflicts = merge3(['a'], ['a', 'X'], ['a', 'X'])
        self.assertEqual(lines, ['a', 'X'])
        self.assertEqual(conflicts, [])

    def test_insert_inside_changed_region_conflicts(self):
        base = ['a', 'b', 'c', 'd']
        ours = ['a', 'B', 'C', 'd']
        theirs = ['a', 'b', 'X', 'c', 'd']
        _, conflicts = merge3(base, ours, theirs)
        self.assertEqual(conflicts, [(2, 2)])

    def test_insert_at_region_boundary_no_conflict(self):
        base = ['a', 'b', 'c']
        ours = ['a', 'B', 'c']
        theirs = ['a', 'X', 'b', 'c']
        lines, conflicts = merge3(base, ours, theirs)
        self.assertEqual(lines, ['a', 'X', 'B', 'c'])
        self.assertEqual(conflicts, [])

        theirs2 = ['a', 'b', 'X', 'c']
        lines, conflicts = merge3(base, ours, theirs2)
        self.assertEqual(lines, ['a', 'B', 'X', 'c'])
        self.assertEqual(conflicts, [])

    def test_delete_vs_edit_conflict(self):
        base = ['a', 'b', 'c']
        lines, conflicts = merge3(base, ['a', 'c'], ['a', 'B', 'c'])
        self.assertEqual(conflicts, [(2, 1)])
        self.assertEqual(lines, [
            'a',
            '<<<<<<< ours',
            '||||||| base',
            'b',
            '=======',
            'B',
            '>>>>>>> theirs',
            'c',
        ])

    def test_both_delete_same_line(self):
        lines, conflicts = merge3(['a', 'b', 'c'], ['a', 'c'], ['a', 'c'])
        self.assertEqual(lines, ['a', 'c'])
        self.assertEqual(conflicts, [])

    def test_multiple_conflicts_listed_in_order(self):
        base = ['a', 'b', 'c', 'd', 'e']
        ours = ['A', 'b', 'C', 'd', 'e']
        theirs = ['a1', 'b', 'C1', 'd', 'e']
        _, conflicts = merge3(base, ours, theirs)
        self.assertEqual(conflicts, [(1, 1), (3, 1)])

    def test_overlapping_regions_same_result_merged(self):
        base = ['a', 'b', 'c']
        ours = ['x', 'y']
        theirs = ['x', 'y']
        lines, conflicts = merge3(base, ours, theirs)
        self.assertEqual(lines, ['x', 'y'])
        self.assertEqual(conflicts, [])

    def test_empty_base(self):
        lines, conflicts = merge3([], ['x'], ['y'])
        self.assertEqual(conflicts, [(1, 0)])
        lines2, conflicts2 = merge3([], ['x'], ['x'])
        self.assertEqual(lines2, ['x'])
        self.assertEqual(conflicts2, [])

    def test_merge_text_appends_conflict_summary(self):
        text = merge_text(['a', 'b'], ['a', 'X'], ['a', 'Y'])
        self.assertTrue(text.endswith('# conflicts\nconflict,2,1\n'))
        text_clean = merge_text(['a'], ['a'], ['a'])
        self.assertEqual(text_clean, 'a\n')
        self.assertNotIn('# conflicts', text_clean)

    def test_deterministic(self):
        base = ['k%d: v%d' % (i, i) for i in range(50)]
        ours = base[:]
        theirs = base[:]
        ours[10] = 'k10: ours'
        ours[30:31] = ['k30: ours', 'extra: 1']
        theirs[20] = 'k20: theirs'
        theirs[40] = 'k40: theirs'
        first = merge_text(base, ours, theirs)
        second = merge_text(base, ours, theirs)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
