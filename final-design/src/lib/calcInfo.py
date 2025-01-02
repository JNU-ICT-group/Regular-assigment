#!python3
#coding=utf-8
"""

3.1.	待测指标的理论值推导
输入
    二元信源分布概率P(0)
    二元对称信道错误传输概率p
    信源的数据率rs
    重复编码重复次数
    二元DMS信源输出文件
    信源编码输出文件
    信道编码输出文件
    二元BSC信道输出文件
    信道解码输出文件
    信源解码输出文件
输出
    包含以下待测指标的理论和实际值的CSV文件：
	    信源的信息率RS（信息比特/秒）
	    信道的数据率rc（数据比特/秒）
	    信道的输入信息率Rci（信息比特/秒）
	    信道的输出信息率Rco（信息比特/秒）
	    信宿关于信源的信息率RI（信息比特/秒）
	    信宿的误码率er

"""

import os
import argparse
import numpy as np
import csv


bit_counts = np.uint8(bytearray(map(int.bit_count, range(256))))

def main(source_info, source_codec_info, channel_codec_info, output_path, **kwgs):
    if kwgs.get('base_path'):
        source_info = os.path.join(kwgs['base_path'], source_info)
        source_codec_info = os.path.join(kwgs['base_path'], source_codec_info)
        channel_codec_info = os.path.join(kwgs['base_path'], channel_codec_info)
        output_path = os.path.join(kwgs['base_path'], output_path)
        if kwgs.get('source_codec_header'):
            kwgs['source_codec_header'] = os.path.join(kwgs['base_path'], kwgs['source_codec_header'])
    if kwgs['message_state'] == 1:
        print('Source path:', source_info)
    if not os.path.exists(source_info):
        raise RuntimeError("source_info must be an exist folder or file.")
    if not os.path.exists(source_codec_info):
        raise RuntimeError("source_codec_info must be an exist folder or file.")
    if not os.path.exists(channel_codec_info):
        raise RuntimeError("channel_codec_info must be an exist folder or file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    ...

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


def calcInfoRate(p0, rs=1):
    return rs * calc_entropy(np.float32([p0, 1-p0]))


def calcChannelDataRate(size_source: int, size_channel: int, rs=1):
    return size_channel / size_source * rs


def calcTheoryChannelDataRate(avlen: float, rs=1):
    return avlen / 8 * rs


def calcTheoryInfoRate(entropy, avlen: float=8., rs=1):
    return rs * entropy / avlen * 8


def write_output(out_file_name, in_file_name, info, x_size):
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        writer.writerow([in_file_name, "{:.6f}".format(info), x_size])


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for calcInfo.")
    parser.add_argument('--p0', type=float, help='Source probability.')
    parser.add_argument('-p', type=float, help='Error transmission probability.')
    parser.add_argument('--rs', type=float, default=1., help='Source data rate.')
    parser.add_argument('--HEADER', type=str, help='Source Codec header path.')
    parser.add_argument('--LEN', type=float, help='Channel Codec average code length (bit/byte).')
    parser.add_argument('OUTPUT', help='Output path.')
    parser.add_argument('SOURCE', nargs='?', help='Source Info path')
    parser.add_argument('SOURCE_CODEC', nargs='?', help='Source Codec Info path')
    parser.add_argument('CHANNEL_CODEC', nargs='?', help='Channel Codec Info path')
    parser.add_argument('-d', '--dir', help='Base directory path')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')

    args = parser.parse_args()

    return dict(
        p0=args.p0,
        p=args.p,
        rs=args.rs,
        source_codec_header=args.HEADER,
        LEN=args.LEN,
        output_path=args.OUTPUT,
        source_info=args.SOURCE,
        source_codec_info=args.SOURCE_CODEC,
        channel_codec_info=args.CHANNEL_CODEC,
        base_path=args.dir,
        message_state=1 if args.O else 2 if args.S else 0,
    )


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    main(**kwgs)
