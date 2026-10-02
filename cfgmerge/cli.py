"""命令行入口：python -m cfgmerge diff|merge ..."""

import argparse
import sys

from .diff import diff_text
from .merge import merge_text


def read_lines(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    lines = content.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='cfgmerge',
        description='配置文件的行级/词级 diff 与三方合并',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    diff_parser = subparsers.add_parser('diff', help='渲染 base -> other 的 diff')
    diff_parser.add_argument('base')
    diff_parser.add_argument('other')

    merge_parser = subparsers.add_parser('merge', help='三方合并')
    merge_parser.add_argument('base')
    merge_parser.add_argument('ours')
    merge_parser.add_argument('theirs')

    args = parser.parse_args(argv)
    if args.command == 'diff':
        text = diff_text(read_lines(args.base), read_lines(args.other))
    else:
        text = merge_text(
            read_lines(args.base),
            read_lines(args.ours),
            read_lines(args.theirs),
        )
    sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
