"""三方合并（base / ours / theirs）。"""

from collections import namedtuple

from .diff import diff_hunks

Block = namedtuple('Block', ['start', 'end', 'lines'])


def change_blocks(base, other):
    """base -> other 的变更块列表，按 base 位置排列。

    每个块表示 base 的 [start, end) 被替换成 lines；纯插入时
    start == end（空区间），位置是插入点前面 base 行的个数。
    """
    blocks = []
    for hunk in diff_hunks(base, other):
        if hunk.tag != 'change':
            continue
        blocks.append(Block(
            hunk.base_start,
            hunk.base_start + hunk.base_count,
            list(other[hunk.other_start:hunk.other_start + hunk.other_count]),
        ))
    return blocks


def _collides(s1, e1, s2, e2):
    """两个块是否撞上，规则见 README。"""
    if s1 == e1 and s2 == e2:
        return s1 == s2
    if s1 == e1:
        return s2 < s1 < e2
    if s2 == e2:
        return s1 < s2 < e1
    return s1 < e2 and s2 < e1


def _apply(base, start, end, blocks):
    """把一侧的块应用到 base[start:end)，返回合并后的行。"""
    result = []
    pos = start
    for block in blocks:
        result.extend(base[pos:block.start])
        result.extend(block.lines)
        pos = block.end
    result.extend(base[pos:end])
    return result


def merge3(base, ours, theirs):
    """三方合并，返回 (合并行列表, 冲突列表)。

    冲突列表每项为 (base 起行 1 起, 涉及 base 行数)，纯插入为 0。
    """
    ours_blocks = change_blocks(base, ours)
    theirs_blocks = change_blocks(base, theirs)
    entries = sorted(
        [(b.start, b.end, 0, b) for b in ours_blocks]
        + [(b.start, b.end, 1, b) for b in theirs_blocks],
        key=lambda item: (item[0], item[1]),
    )

    # 每个连通分量：[start, end, {side: [blocks]}]
    components = []
    for start, end, side, block in entries:
        if components and _collides(
                components[-1][0], components[-1][1], start, end):
            comp = components[-1]
            if start < comp[0]:
                comp[0] = start
            if end > comp[1]:
                comp[1] = end
            comp[2][side].append(block)
        else:
            components.append([start, end, ([], [])])
            components[-1][2][side].append(block)

    output = []
    conflicts = []
    pos = 0
    for start, end, sides in components:
        output.extend(base[pos:start])
        ours_side, theirs_side = sides
        if not theirs_side:
            output.extend(_apply(base, start, end, ours_side))
        elif not ours_side:
            output.extend(_apply(base, start, end, theirs_side))
        else:
            ours_text = _apply(base, start, end, ours_side)
            theirs_text = _apply(base, start, end, theirs_side)
            if ours_text == theirs_text:
                output.extend(ours_text)
            else:
                output.append('<<<<<<< ours')
                output.extend(ours_text)
                output.append('||||||| base')
                output.extend(base[start:end])
                output.append('=======')
                output.extend(theirs_text)
                output.append('>>>>>>> theirs')
                conflicts.append((start + 1, end - start))
        pos = end
    output.extend(base[pos:])
    return output, conflicts


def merge_text(base, ours, theirs):
    """三方合并并按 README 格式渲染（冲突块 + 冲突清单），逐行 LF 结尾。"""
    lines, conflicts = merge3(base, ours, theirs)
    if conflicts:
        lines = lines + ['# conflicts']
        lines.extend('conflict,{},{}'.format(s, c) for s, c in conflicts)
    return ''.join(line + '\n' for line in lines)
