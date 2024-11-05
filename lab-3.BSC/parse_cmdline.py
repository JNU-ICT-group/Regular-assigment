import os
import sys
import typing
import argparse


class ARGS(typing.TypedDict):
    input_path: str | None
    output_path: str | None
    base_path: str | None
    show_help: bool
    show_version: bool
    test_flow: bool
    message_state: int
    msg_length: int
    depth: int
    export_p: str | None


_args = None
_read = False


def parse_sys_args() -> ARGS:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    global _read, _args

    if _read:
        return _args

    _read = True

    parser = argparse.ArgumentParser(description="Process some commands for calcInfo.")
    parser.add_argument('input_path', nargs='?', help='Input file path')
    parser.add_argument('output_path', nargs='?', help='Output file path')
    parser.add_argument('msg_length', type=int, nargs='?', help='Real Size of Sequence.')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('--depth', type=int, default=1, help='Folder traversal depth (default: 1)')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    parser.add_argument('--export-p', type=str, help='Probability information output path')

    args = parser.parse_args()

    _args = ARGS(
        input_path=args.input_path,
        output_path=args.output_path,
        base_path=args.dir,
        show_help=False,
        show_version=args.version,
        test_flow=args.test,
        message_state=1 if args.O else 2 if args.S else 0,
        depth=args.depth,
        msg_length=args.msg_length,
        export_p=args.export_p,
    )

    return _args
