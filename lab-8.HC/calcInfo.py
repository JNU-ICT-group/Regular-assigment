#!python3
#coding=utf-8
"""
计算任意指定的一个文件“平均每个字节的信息量（比特）
"""
__version__ = '1.0'

import os
import parse_cmdline
from typing import Iterator, AnyStr, SupportsFloat
import numpy as np
from collections import Counter
import csv
from typing import Tuple

def main(input_path, output_path, **kwgs) -> Iterator[float]:
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
            print('\tFileSize=%6dB, average-Entropy=%.6f' % (x_size, info))
        write_output(output_path, in_file, info, x_size)
        if export_path:
            if kwgs['message_state'] == 1:
                print('\tProbability-Summary=%.5f' % p.sum())
            write_export(export_path, p)
        infos.append(info)

    return infos


def spand_files(root, depth) -> Iterator[AnyStr]:
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


def read_input(in_file_name) -> Tuple[np.ndarray, int]:
    """使用numpy的fromfile函数读取文件并计算其信息熵"""
    # 使用 numpy.fromfile 以无符号整数形式读取文件
    arr = np.fromfile(in_file_name, dtype=np.uint8)
    return arr, len(arr)


def calc_probability(data) -> np.ndarray:
    """计算每个字节的近似概率"""
    file_size = len(data)
    byte_counts = Counter(data)
    probability = np.zeros(256, dtype=np.float32)
    for byte, count in byte_counts.items():
        probability[byte] = count
    probability /= file_size
    return probability


def calc_information(p: np.ndarray) -> np.ndarray:
    """计算每个字节的信息量（单位：比特）"""
    p = p.copy()
    np.putmask(p, p == 0, np.spacing(1))
    information = - np.log2(p, out=p)
    return information


def calc_entropy(p: np.ndarray) -> float:
    """计算信息熵，即平均每个字节的信息量"""
    entropy = (p * calc_information(p)).sum()
    return entropy


def compute_info(arr, x_size) -> Tuple[np.ndarray, float]:
    if x_size == 0:
        return np.uint8([]), 0  # 避免空文件导致的问题

    # 计算每个字节的近似概率
    probability = calc_probability(arr[:x_size])
    # 计算信息熵
    entropy = calc_entropy(probability)

    return probability, entropy


def write_output(out_file_name, in_file_name, info, x_size):
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        writer.writerow([in_file_name, "{:.6f}".format(info), x_size])


def write_export(out_file_name, x):
    with open(out_file_name, 'w', newline='', encoding='utf-8') as out_file:
        write = csv.writer(out_file, quoting=csv.QUOTE_NONE)
        write.writerows([int(i), '%.8f' % p] for i, p in enumerate(x) if p)


def test_workflow():
    import unittest
    import test_module
    unittest.main(test_module, argv=['test_module'], exit=False)


if __name__ == "__main__":
    kwgs = parse_cmdline.parse_sys_args()

    if kwgs['show_version']:
        print(__version__)

    if kwgs['test_flow']:
        test_workflow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
