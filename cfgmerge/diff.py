"""行级 diff、hunk 划分与词级差异，以及文本渲染。"""

from collections import namedtuple

from ._lcs import edit_script

Hunk = namedtuple('Hunk', ['tag', 'base_start', 'base_count',
                           'other_start', 'other_count'])


def diff_hunks(base, other):
    """把 base -> other 的编辑脚本归并成连续的 equal/change hunk。

    所有下标为 0 起、左闭右开。纯插入 hunk 的 base_count 为 0，
    base_start 是插入点（前面 base 行的个数）；纯删除对称。
    """
    ops = edit_script(base, other)
    hunks = []
    i = j = 0
    p = 0
    while p < len(ops):
        if ops[p][0] == 'eq':
            bs, os_, count = i, j, 0
            while p < len(ops) and ops[p][0] == 'eq':
                p += 1
                i += 1
                j += 1
                count += 1
            hunks.append(Hunk('equal', bs, count, os_, count))
        else:
            bs, os_, bc, oc = i, j, 0, 0
            while p < len(ops) and ops[p][0] != 'eq':
                if ops[p][0] == 'del':
                    i += 1
                    bc += 1
                else:
                    j += 1
                    oc += 1
                p += 1
            hunks.append(Hunk('change', bs, bc, os_, oc))
    return hunks


def word_change(base_line, other_line):
    """两行之间的词级差异，返回 (删掉的词, 插入的词)，各自按顺序排列。

    词按空白切分（连续非空白字符为一个词），词级最小编辑脚本与并列
    取法同行级规则。
    """
    base_words = base_line.split()
    other_words = other_line.split()
    ops = edit_script(base_words, other_words)
    deleted = [base_words[op[1]] for op in ops if op[0] == 'del']
    inserted = [other_words[op[1]] for op in ops if op[0] == 'ins']
    return deleted, inserted


def _hunk_header(hunk):
    return '{},{},{},{},{}'.format(
        hunk.tag,
        hunk.base_start + 1,
        hunk.base_count,
        hunk.other_start + 1,
        hunk.other_count,
    )


def diff_text(base, other):
    """按 README 规定的文本格式渲染 base -> other 的 diff。"""
    lines = []
    for hunk in diff_hunks(base, other):
        lines.append(_hunk_header(hunk))
        if hunk.tag != 'change':
            continue
        for k in range(max(hunk.base_count, hunk.other_count)):
            has_base = k < hunk.base_count
            has_other = k < hunk.other_count
            bno = str(hunk.base_start + k + 1) if has_base else ''
            ono = str(hunk.other_start + k + 1) if has_other else ''
            if has_base and has_other:
                deleted, inserted = word_change(
                    base[hunk.base_start + k],
                    other[hunk.other_start + k],
                )
            elif has_base:
                deleted = base[hunk.base_start + k].split()
                inserted = []
            else:
                deleted = []
                inserted = other[hunk.other_start + k].split()
            lines.append('words,{},{},{},{}'.format(
                bno, ono, ' '.join(deleted), ' '.join(inserted)))
    return ''.join(line + '\n' for line in lines)
