import os
import unittest

from cfgmerge.cli import read_lines
from cfgmerge import merge_text

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), os.pardir, 'samples')


class SampleCasesTest(unittest.TestCase):
    def test_all_sample_cases(self):
        case_dirs = sorted(
            name for name in os.listdir(SAMPLES_DIR)
            if name.startswith('case-')
        )
        self.assertTrue(case_dirs, 'samples 目录为空')
        for name in case_dirs:
            case_dir = os.path.join(SAMPLES_DIR, name)
            with self.subTest(case=name):
                base = read_lines(os.path.join(case_dir, 'base.txt'))
                ours = read_lines(os.path.join(case_dir, 'ours.txt'))
                theirs = read_lines(os.path.join(case_dir, 'theirs.txt'))
                with open(os.path.join(case_dir, 'expected.txt'),
                          encoding='utf-8', newline='') as f:
                    expected = f.read()
                self.assertEqual(merge_text(base, ours, theirs), expected)


if __name__ == '__main__':
    unittest.main()
