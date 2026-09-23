"""命令行入口：

    python -m configmerge diff  <base> <other>
    python -m configmerge merge <base> <ours> <theirs>
"""

import sys

from .diff import render_diff, split_lines
from .merge import render_merge


def _read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return split_lines(f.read())


def main(argv):
    if len(argv) >= 2 and argv[1] == "diff" and len(argv) == 4:
        sys.stdout.write(render_diff(_read(argv[2]), _read(argv[3])))
        return 0
    if len(argv) >= 2 and argv[1] == "merge" and len(argv) == 5:
        sys.stdout.write(render_merge(_read(argv[2]), _read(argv[3]), _read(argv[4])))
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
