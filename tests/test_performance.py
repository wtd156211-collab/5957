import time
import unittest

from cfgmerge import diff_text, merge_text

LINE_COUNT = 20000
TIME_LIMIT = 3.0


def make_inputs():
    base = ['key{}: value{}'.format(i, i) for i in range(LINE_COUNT)]
    ours = list(base)
    theirs = list(base)
    for i in range(0, LINE_COUNT, 100):
        ours[i] = 'key{}: ours{}'.format(i, i)
    for i in range(50, LINE_COUNT, 100):
        theirs[i] = 'key{}: theirs{}'.format(i, i)
    for i in range(1000, LINE_COUNT, 2000):
        ours[i:i] = ['inserted_by_ours_{}'.format(i)]
    for i in range(1500, LINE_COUNT, 2000):
        del theirs[i]
    return base, ours, theirs


class PerformanceTest(unittest.TestCase):
    def test_diff_under_time_limit(self):
        base, ours, _ = make_inputs()
        start = time.perf_counter()
        diff_text(base, ours)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, TIME_LIMIT,
                        'diff 耗时 {:.2f}s'.format(elapsed))

    def test_merge_under_time_limit(self):
        base, ours, theirs = make_inputs()
        start = time.perf_counter()
        merge_text(base, ours, theirs)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, TIME_LIMIT,
                        'merge 耗时 {:.2f}s'.format(elapsed))


if __name__ == '__main__':
    unittest.main()
