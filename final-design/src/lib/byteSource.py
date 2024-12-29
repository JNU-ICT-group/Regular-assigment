#!python3
#coding=utf-8
"""
生成任意指定概率分布和长度的符号序列.
限制最大为256进制。
"""
__version__ = '1.1'

import os
import argparse
import numpy as np
import csv


def main(input_path, output_path, msg_length, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('Input path:', input_path)
        print('Output path:', output_path)
    if not os.path.exists(input_path):
        raise RuntimeError("input_path must be an exist folder or file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    if os.path.isfile(input_path):
        in_files = iter([input_path])
    else:
        in_files = spand_files(input_path, kwgs['depth'])

    if msg_length<=0:
        raise ValueError("Message length must be a positive number.")
    for in_file in in_files:
        if in_file == output_path:
            continue
        if kwgs['message_state']:
            print('Processing "%s" ...' % in_file)

        symbol_prob = read_input(in_file)          # do work for one single file `in_file`
        msg = random_sequence(symbol_prob, msg_length)

        if kwgs['message_state'] == 1:
            print()
        write_output(output_path, msg)


def spand_files(root, depth):
    """
    walk root directory and return files step by step.
    """
    roots = [root]
    roots_next = []
    for i in range(depth):
        for root in roots:
            base_path, dirs, files = next(os.walk(root))
            for file in files:
                yield os.path.join(base_path, file)
            roots_next.extend(dirs)
            dirs.clear()

        roots, roots_next = roots_next, roots
        roots_next.clear()


def read_input(input_path) -> np.ndarray:
    """
    从CSV文件中读取符号概率分布。

    Parameters:
        input_path (str): 输入符号概率分布的CSV文件路径。

    Returns:
        numpy.ndarray: 符号的概率分布数组。
    """
    symbol_prob = np.zeros(256, dtype=np.float32)  # 初始化一个大小为256的数组来保存概率分布
    with open(input_path, 'r') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
        for row in reader:
            symbol, prob = int(row[0]), float(row[1])
            symbol_prob[symbol] = prob

    # 检查概率分布是否符合要求（所有概率之和应为1）
    csum = symbol_prob.sum()
    if not np.isclose(csum, 1.0, rtol=1e-5, atol=0):
        raise ValueError("输入的概率分布不符合要求，所有概率之和必须为1，但是得到了%.6f。" % csum)

    symbol_prob *= 1/csum                          # 归一化
    return symbol_prob


def write_output(output_path, sequence):
    """
    将生成的符号序列保存为二进制文件。

    Parameters:
        output_path (str): 输出文件的路径。
        sequence (numpy.ndarray): 生成的符号序列。
    """
    with open(output_path, 'wb') as out_file:
        # 将符号序列转换为字节形式并写入文件
        out_file.write(bytearray(sequence))


def random_sequence(symbol_prob, msg_len) -> np.ndarray:
    """
    使用 np.searchsorted 生成符合指定概率分布的随机序列（蒙特卡罗法）

    Parameters:
        symbol_prob (numpy.ndarray): 符号的概率分布。
        msg_len (int): 生成的消息长度（符号数量）。

    Returns:
        numpy.ndarray: 生成的符号序列。
    """
    # 计算累积概率分布 F(i)
    symbol_cumsum = symbol_prob.cumsum()

    # 生成符合均匀分布的随机数，并通过累积概率分布查找对应符号
    msg_len = int(msg_len)
    symbol_random = np.random.uniform(size=msg_len)
    msg = np.searchsorted(symbol_cumsum, symbol_random)
    return msg.astype(np.uint8)


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for calcInfo.")
    parser.add_argument('input_path', nargs='?', help='Input file path')
    parser.add_argument('output_path', nargs='?', help='Output file path')
    parser.add_argument('msg_length', type=int, default=0, nargs='?', help='Real Size of Sequence.')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('--depth', type=int, default=1, help='Folder traversal depth (default: 1)')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    parser.add_argument('--export-p', type=str, help='Probability information output path')

    args = parser.parse_args()

    return dict(
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


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['show_version']:
        print(__version__)

    if kwgs['test_flow']:
        import byteChannelTest
        byteChannelTest.test_flow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
