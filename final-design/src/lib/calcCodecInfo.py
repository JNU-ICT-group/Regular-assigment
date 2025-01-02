"""
2.3.	信源编码指标计算模块
模块输入
	编码前的文件
	编码后的文件
模块输出
	包含以下指标数值的文件（CSV格式）
	    压缩比（编码前文件字节数/编码后文件字节数）
	    平均码长（码字数据比特/信源字节）
	    编码效率
	    编码前的文件的信息熵（信息比特/字节）
	    编码后的文件的信息熵（信息比特/字节）

"""

import os
import argparse
import numpy as np
import csv

bit_counts = np.uint8(bytearray(map(int.bit_count, range(256))))

def main(input_path, encode_path, output_path, **kwgs):
    input_paths = path_split(input_path)
    encode_paths = path_split(encode_path)
    output_paths = path_split(output_path)

    for (input_path, encode_path, output_path) in zip(input_paths, encode_paths, output_paths):
        if kwgs['message_state']:
            print('Processing "%s" ...' % input_path)
        work_flow(input_path, encode_path, output_path, **kwgs)


def work_flow(input_path, encode_path, output_path, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        encode_path = os.path.join(kwgs['base_path'], encode_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('Input path:', input_path)
        print('Output path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    source, x_size = read_input(input_path)
    encoded, y_size = read_input(encode_path)
    header_size = kwgs['header_size']
    encoded, y_size = encoded[header_size:], y_size - header_size
    p_source = calc_probability(source)
    p_encode = calc_probability(encoded)
    entropy_source = calc_entropy(p_source)     # bit/byte
    entropy_encode = calc_entropy(p_encode)     # bit/byte
    ratio = calc_compress_ratio(x_size, y_size)
    avlen = calc_code_avlen(x_size, y_size)
    efficiency = calc_efficiency(ratio)
    info = [ratio, avlen, efficiency, entropy_source, entropy_encode]
    if kwgs['message_state'] == 1:
        print('\tFileSize=%6dB, Encoded=%6dB, av-Code-Len=%.6fbit/byte\n' % (x_size, y_size, info[1]))
    write_output(output_path, input_path, encode_path, info)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


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


def calc_compress_ratio(size0, size1) -> float:
    return size0 / size1

def calc_code_avlen(size0, size1) -> float:
    return 8 * size1 / size0

def calc_efficiency(ratio: float) -> float:
    return (1. - 1/ratio) * 100

def write_output(out_file_name, in_file_name, encode_file_name, info):
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
        out_file.write('"X(source)","Y(encoded)","compression ratio","L(avg code len)bit/byte","η(efficiency)%","H(X)","H(Y)"\n')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        row = [in_file_name, encode_file_name]
        for v in info:
            row.append("{:.6f}".format(v))
        writer.writerow(row)


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for calcInfo.")
    parser.add_argument('SOURCE', nargs='?', help='Input file path')
    parser.add_argument('ENCODE', nargs='?', help='Encoded file path')
    parser.add_argument('OUTPUT', nargs='?', help='Output csv file path')
    parser.add_argument('-p', type=int, default=0, help='Header size')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('--depth', type=int, default=1, help='Folder traversal depth (default: 1)')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')

    args = parser.parse_args()

    return dict(
        input_path=args.SOURCE,
        encode_path=args.ENCODE,
        header_size=args.p,
        base_path=args.dir,
        message_state=1 if args.O else 2 if args.S else 0,
        depth=args.depth,
        output_path=args.OUTPUT,
    )


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['encode_path']:
        main(**kwgs)
