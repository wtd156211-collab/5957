import random
import time
import unittest

from configmerge import render_diff, render_merge

LINES = 20000
LIMIT_SECONDS = 3.0


def _make_base():
    return ["key_%05d: value_%d" % (i, i % 97) for i in range(LINES)]


def _mutate(base, seed, changes):
    rng = random.Random(seed)
    lines = base[:]
    for _ in range(changes):
        op = rng.randrange(3)
        pos = rng.randrange(len(lines))
        if op == 0:
            lines[pos] = "key_%05d: changed_%d" % (pos, seed)
        elif op == 1:
            del lines[pos]
        else:
            lines.insert(pos, "inserted_%d_%d" % (seed, pos))
    return lines


class TestPerformance(unittest.TestCase):
    def test_diff_20k_lines(self):
        base = _make_base()
        other = _mutate(base, seed=1, changes=2000)
        start = time.perf_counter()
        render_diff(base, other)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, LIMIT_SECONDS)

    def test_merge_20k_lines(self):
        base = _make_base()
        ours = _mutate(base, seed=2, changes=2000)
        theirs = _mutate(base, seed=3, changes=2000)
        start = time.perf_counter()
        render_merge(base, ours, theirs)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, LIMIT_SECONDS)

    def test_diff_completely_different_files(self):
        base = ["a_%d" % i for i in range(LINES)]
        other = ["b_%d" % i for i in range(LINES)]
        start = time.perf_counter()
        render_diff(base, other)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, LIMIT_SECONDS)


if __name__ == "__main__":
    unittest.main()
