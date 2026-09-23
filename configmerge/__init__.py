"""配置仓库的行级 diff 与三方合并库（只用标准库）。"""

from .diff import Hunk, diff_hunks, render_diff, split_lines, word_diff
from .merge import merge, render_merge

__all__ = [
    "Hunk",
    "diff_hunks",
    "render_diff",
    "split_lines",
    "word_diff",
    "merge",
    "render_merge",
]
