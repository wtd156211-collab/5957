"""配置仓库专用的行级/词级 diff 与三方合并库（只用标准库）。"""

from ._lcs import edit_script
from .diff import Hunk, diff_hunks, diff_text, word_change
from .merge import Block, change_blocks, merge3, merge_text

__all__ = [
    'edit_script',
    'Hunk',
    'diff_hunks',
    'diff_text',
    'word_change',
    'Block',
    'change_blocks',
    'merge3',
    'merge_text',
]
