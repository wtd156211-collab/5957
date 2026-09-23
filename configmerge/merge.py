"""三方合并：base + ours + theirs -> 合并结果（含冲突标记与冲突清单）。"""

from collections import namedtuple

from .diff import diff_hunks

Block = namedtuple("Block", ["start", "end", "side", "content"])
# 变更块：base 的半开区间 [start, end) 被替换成 content。
# 纯插入的块 start == end（空区间，位置 = 插入点前面已有的 base 行数）。


def _change_blocks(base, other, side):
    return [
        Block(h.base_start, h.base_start + h.base_count, side,
              other[h.other_start:h.other_start + h.other_count])
        for h in diff_hunks(base, other)
        if h.tag == "change"
    ]


def _collides(block, cs, ce):
    """block 是否与簇的 base 跨度 [cs, ce) 撞上（README 合并规则 4、5）。"""
    if block.start == block.end:  # 纯插入
        p = block.start
        if cs == ce:
            return p == cs          # 两个插入落在同一位置
        return cs < p < ce          # 插入落在被改动区间内部才算撞上
    if cs == ce:
        return block.start < cs < block.end
    return block.start < ce and cs < block.end  # 区间有重叠才算，相邻不算


def _apply(base, cs, ce, blocks):
    """把一侧落在 [cs, ce) 内的变更块应用到 base 该段上。"""
    out = []
    p = cs
    for b in blocks:
        out.extend(base[p:b.start])
        out.extend(b.content)
        p = b.end
    out.extend(base[p:ce])
    return out


def merge(base, ours, theirs):
    """三方合并。返回 (合并后的行列表, [(冲突起行, 涉及行数), ...])。

    判定顺序固定：先按位置找撞上的块聚成簇，簇内两边都动了再比内容，
    内容完全一样则自动合，否则标冲突。
    """
    blocks = _change_blocks(base, ours, "ours") + _change_blocks(base, theirs, "theirs")
    blocks.sort(key=lambda b: (b.start, b.end, b.side))

    # 按 base 位置把互相撞上的块聚成簇（簇跨度为成员区间的并）。
    clusters = []  # 每项 [cs, ce, ours 块列表, theirs 块列表]
    for b in blocks:
        if clusters and _collides(b, clusters[-1][0], clusters[-1][1]):
            cl = clusters[-1]
            cl[0] = min(cl[0], b.start)
            cl[1] = max(cl[1], b.end)
        else:
            cl = [b.start, b.end, [], []]
            clusters.append(cl)
        cl[2 if b.side == "ours" else 3].append(b)

    out = []
    conflicts = []
    pos = 0
    for cs, ce, ours_blocks, theirs_blocks in clusters:
        out.extend(base[pos:cs])
        if ours_blocks and theirs_blocks:
            ours_seg = _apply(base, cs, ce, ours_blocks)
            theirs_seg = _apply(base, cs, ce, theirs_blocks)
            if ours_seg == theirs_seg:
                out.extend(ours_seg)  # 两边改成完全一样的内容，只留一份
            else:
                out.append("<<<<<<< ours")
                out.extend(ours_seg)
                out.append("||||||| base")
                out.extend(base[cs:ce])
                out.append("=======")
                out.extend(theirs_seg)
                out.append(">>>>>>> theirs")
                conflicts.append((cs + 1, ce - cs))
        else:
            out.extend(_apply(base, cs, ce, ours_blocks or theirs_blocks))
        pos = ce
    out.extend(base[pos:])
    return out, conflicts


def render_merge(base, ours, theirs):
    """合并输出文本：合并内容 + （有冲突时）# conflicts 与冲突清单。"""
    lines, conflicts = merge(base, ours, theirs)
    if conflicts:
        lines = lines + ["# conflicts"]
        lines += ["conflict,%d,%d" % (start, count) for start, count in conflicts]
    return "\n".join(lines) + "\n" if lines else ""
