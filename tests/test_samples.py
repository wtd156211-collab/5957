import pathlib
import unittest

from configmerge import render_merge, split_lines

SAMPLES = pathlib.Path(__file__).resolve().parent.parent / "samples"


class TestSamples(unittest.TestCase):
    def test_all_cases_match_expected(self):
        case_dirs = sorted(d for d in SAMPLES.iterdir() if d.is_dir())
        self.assertEqual(len(case_dirs), 8)
        for d in case_dirs:
            with self.subTest(case=d.name):
                read = lambda name: split_lines((d / name).read_text(encoding="utf-8"))
                got = render_merge(read("base.txt"), read("ours.txt"), read("theirs.txt"))
                want = (d / "expected.txt").read_text(encoding="utf-8")
                self.assertEqual(got, want)


if __name__ == "__main__":
    unittest.main()
