"""行级 diff（hunk 划分 + 词级差异 + 文本渲染）。"""

from collections import namedtuple

from .lcs import common_subsequence_matches

Hunk = namedtuple("Hunk", ["tag", "base_start", "base_count", "other_start", "other_count"])
# tag: "equal" | "change"；start 为 0 起下标，count 为行数（可为 0）。


def split_lines(text):
    """按 \\n 切分；空文件视为 0 行；文件末尾的换行不产生空行。"""
    if text == "":
        return []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def diff_hunks(base, other):
    """把 base -> other 的最小编辑脚本划分成 equal / change 相间的 hunk。"""
    matches = common_subsequence_matches(base, other)
    hunks = []
    bi = oi = 0
    k = 0
    while k < len(matches):
        i, j = matches[k]
        if i > bi or j > oi:
            hunks.append(Hunk("change", bi, i - bi, oi, j - oi))
        run = 1
        while k + run < len(matches) and matches[k + run] == (i + run, j + run):
            run += 1
        hunks.append(Hunk("equal", i, run, j, run))
        bi = i + run
        oi = j + run
        k += run
    if bi < len(base) or oi < len(other):
        hunks.append(Hunk("change", bi, len(base) - bi, oi, len(other) - oi))
    return hunks


def word_diff(base_line, other_line):
    """行内词级差异：返回 (删除的词列表, 插入的词列表)。词按空白切分。"""
    base_words = base_line.split()
    other_words = other_line.split()
    matches = common_subsequence_matches(base_words, other_words)
    matched_b = {i for i, _ in matches}
    matched_o = {j for _, j in matches}
    deleted = [w for t, w in enumerate(base_words) if t not in matched_b]
    inserted = [w for t, w in enumerate(other_words) if t not in matched_o]
    return deleted, inserted


def render_diff(base, other):
    """diff 的文本渲染（README「输出结构」一节定义的格式）。

    hunk 头：<tag>,<base 起行>,<base 行数>,<另一侧起行>,<另一侧行数>
    change hunk 内每对位置对应的变更行（以及某一侧多出来的行）跟一行：
    words,<base 行号>,<另一侧行号>,<删除的词>,<插入的词>
    行号 1 起；空区间（行数 0）的起行 = 区间前已有行数 + 1。
    """
    out = []
    for h in diff_hunks(base, other):
        out.append(
            "%s,%d,%d,%d,%d"
            % (h.tag, h.base_start + 1, h.base_count, h.other_start + 1, h.other_count)
        )
        if h.tag != "change":
            continue
        for k in range(max(h.base_count, h.other_count)):
            has_b = k < h.base_count
            has_o = k < h.other_count
            bno = str(h.base_start + k + 1) if has_b else ""
            ono = str(h.other_start + k + 1) if has_o else ""
            if has_b and has_o:
                deleted, inserted = word_diff(
                    base[h.base_start + k], other[h.other_start + k]
                )
            elif has_b:
                deleted, inserted = base[h.base_start + k].split(), []
            else:
                deleted, inserted = [], other[h.other_start + k].split()
            out.append(
                "words,%s,%s,%s,%s" % (bno, ono, " ".join(deleted), " ".join(inserted))
            )
    return "\n".join(out) + "\n" if out else ""
