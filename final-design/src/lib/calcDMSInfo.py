"""
2.1.	计算二元离散无记忆信源（DMS）指标
模块输入
    信源输出消息序列文件
模块输出
	字节概率分布文件（CSV格式），即256元DMS的概率分布统计：P(0), ..., P(255)
	包含以下指标数值的文件（CSV格式）
	    数据比特概率分布（即二元DMS的概率分布统计）：P(0)
	    二元DMS的信息熵（信息比特/二元消息）
	    二元DSM的信源冗余度

"""

import os
import argparse
import numpy as np
import csv

bit_counts = np.uint8(bytearray(map(int.bit_count, range(256))))

def main(input_path, output_path, **kwgs) -> [float]:
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

    export_path = kwgs.get('export_p')
    if export_path:
        if kwgs.get('base_path'):
            export_path = os.path.join(kwgs['base_path'], export_path)
        if kwgs['message_state'] == 1:
            print('Export probability path:', export_path)
        if os.path.isfile(export_path):
            os.remove(export_path)

    infos = []
    for in_file in in_files:
        if in_file == output_path:
            continue
        if kwgs['message_state']:
            print('Processing "%s" ...' % in_file)
        pass            # do work for one single file `in_file`
        arr, x_size = read_input(in_file)
        p, info = compute_info(arr, x_size)
        if kwgs['message_state'] == 1:
            print('\tFileSize=%6dB, average-Entropy=%.6f' % (x_size, info[1]))
        write_output(output_path, in_file, info, x_size)
        if export_path:
            if kwgs['message_state'] == 1:
                print('\tProbability-Summary=%.5f' % p.sum())
            write_export(export_path, p)
        infos.append(info)

    return infos


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


def read_input(in_file_name) -> (np.ndarray, int):
    """使用numpy的fromfile函数读取文件并计算其信息熵"""
    # 使用 numpy.fromfile 以无符号整数形式读取文件
    arr = np.fromfile(in_file_name, dtype=np.uint8)
    return arr, len(arr)


def calc_probability(data) -> np.ndarray:
    """计算每个字节的近似概率"""
    file_size = len(data)
    byte_counts = np.histogram(data, bins=range(257))[0]
    probability = np.divide(byte_counts, file_size, dtype=np.float32)
    return probability


def calc_information(p: np.ndarray) -> np.ndarray:
    """计算每个字节的信息量（单位：比特）"""
    p = p.copy()
    np.clip(p, np.spacing(1), None, out=p)
    information = - np.log2(p, out=p)
    return information


def calc_entropy(p: np.ndarray) -> float:
    """计算信息熵，即平均每个字节的信息量"""
    entropy = (p * calc_information(p)).sum()
    return entropy


def calc_prob0(prob) -> float:
    return 1. - (prob * bit_counts).sum() / 8


def calc_redundancy(p0: float) -> float:
    return 1. - calc_entropy(np.float32([p0, 1-p0]))


def compute_info(arr, x_size) -> (np.ndarray, (float, float, float)):
    if x_size == 0:
        return (np.zeros(256, dtype=np.float32), (0.0, 0.0, 0.0))  # 避免空文件导致的问题

    # 计算每个字节的近似概率
    probability = calc_probability(arr[:x_size])
    # 计算信息熵
    prob0 = calc_prob0(probability)
    entropy = calc_entropy(np.float32([prob0, 1-prob0]))
    redundancy = calc_redundancy(prob0)

    return probability, (prob0, entropy, redundancy)


def write_output(out_file_name, in_file_name, info, x_size):
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
        out_file.write('"X(source)","P(0)","H(X)bit/bit","redundancy","msg length"\n')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        row = [in_file_name]
        for v in info:
            row.append("{:.6f}".format(v))
        row.append(x_size)
        writer.writerow(row)


def write_export(out_file_name, x):
    with open(out_file_name, 'w', newline='', encoding='utf-8') as out_file:
        write = csv.writer(out_file, quoting=csv.QUOTE_NONE)
        write.writerows([int(i), p] for i, p in enumerate(x) if p)


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for calcInfo.")
    parser.add_argument('input_path', nargs='?', help='Input file path')
    parser.add_argument('output_path', nargs='?', help='Output file path')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('--depth', type=int, default=1, help='Folder traversal depth (default: 1)')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('--export-p', type=str, help='Probability information output path')

    args = parser.parse_args()

    return dict(
        input_path=args.input_path,
        output_path=args.output_path,
        base_path=args.dir,
        message_state=1 if args.O else 2 if args.S else 0,
        depth=args.depth,
        test_flow=args.test,
        export_p=args.export_p,
    )


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['test_flow']:
        import byteSourceTest
        byteSourceTest.test_flow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
