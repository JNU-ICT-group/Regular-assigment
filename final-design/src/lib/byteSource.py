#!python3
#coding=utf-8
"""
生成任意指定概率分布和长度的符号序列.
限制最大为256进制。

v1.3 增加padding功能
v1.4 改为无扩展二元信源
模块输入
	信源消息概率分布P(0)
	消息序列的大小（字节）
模块输出
	信源输出消息序列文件

"""
__version__ = '1.4'

import os
import argparse
import numpy as np
import csv

bit_counts = np.float32(bytearray(map(int.bit_count, range(256))))

def generate(ones):
    probs = []
    for p in ones:
        w1 = p ** bit_counts
        w2 = (1-p) ** (8 - bit_counts)
        probs.append(w1 * w2)
    return probs


def main(prob0s, output_path, msg_length, **kwgs):
    ones = [1.-float(p0) for p0 in prob0s.split(',')]
    prob0s = generate(ones)
    output_paths = path_split(output_path)

    for (prob, output_path) in zip(prob0s, output_paths):
        if kwgs['message_state']:
            print('Processing "%s" ...' % output_path)
        work_flow(prob, output_path, msg_length, **kwgs)


def work_flow(symbol_prob, output_path, msg_length, **kwgs):
    if kwgs.get('base_path'):
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('Output path:', output_path)
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    if msg_length<=0:
        raise ValueError("Message length must be a positive number.")

    msg = random_sequence(symbol_prob, msg_length)
    pad_left, v1, pad_right, v2 = kwgs.get('pad', (0,0,0,0))
    if pad_left or pad_right:
        msg = np.pad(msg, (pad_left, pad_right), constant_values=(v1, v2))

    if kwgs['message_state'] == 1:
        print()
    write_output(output_path, msg)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


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
    parser.add_argument('--p0', help='Probability of binary-symbol 0.')
    parser.add_argument('output_path', help='Output file path')
    parser.add_argument('msg_length', type=int, help='Real Size of Sequence.')
    parser.add_argument('-p', type=lambda string: tuple(map(int, string[1:-1].split(','))), default=(0,0,0,0), help='Padding the two side with a const value, '
                        'like (pad-left,bool,pad-right,bool).')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('--depth', type=int, default=1, help='Folder traversal depth (default: 1)')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')

    args = parser.parse_args()

    return dict(
        prob0s=args.p0,
        output_path=args.output_path,
        base_path=args.dir,
        pad=args.p,
        show_help=False,
        show_version=args.version,
        test_flow=args.test,
        message_state=1 if args.O else 2 if args.S else 0,
        depth=args.depth,
        msg_length=args.msg_length,
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

    if kwgs['output_path']:
        main(**kwgs)
