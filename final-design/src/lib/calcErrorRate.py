### calcErrorRate.py ###
""" A basic program calculate the error rate of repetition coding file.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |LEN  : uint8, code length n, must be odd number and 2 < n < 10
        |source length : uint32, number of symbols in source divided by 8
Payload |codeword sequence : many uint
End |pad : some bits as 0

Note: This program is intended for use in course, Principle of Information and Coding Theory.
2.4.	信道编解码指标计算
模块输入
	编码前的文件
	编码后的文件
	解码后的文件
模块输出
	包含以下指标数值的文件（CSV格式）
    	压缩比（编码前文件字节数/编码后文件字节数）
    	误码率（汉明失真，错误数据比特/总数据比特）
    	编码前的信源信息传输率（信息比特/字节）
    	编码后的信源信息传输率（信息比特/字节）

"""

import csv
import os
import argparse
import unittest
import math

# Non-standard library
import numpy as np


__author__ = "Zhang, Pengyang; Chen, Jin; "
__email__ = "miracle@stu2022.jnu.edu.cn"
__version__ = "20241212.2220"


def main():
    parser = argparse.ArgumentParser(description="Lossless source coder for encoding and decoding.")

    parser.add_argument('SOURCE', type=str, help='path to input file 1 (before encoding)')
    parser.add_argument('ENCODE', type=str, help='path to input file 2 (after encoding)')
    parser.add_argument('DECODE', type=str, help='path to input file 3 (after decoding)')
    parser.add_argument('RESULT', type=str, nargs='?', help='path to the result CSV file')

    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show message')

    args = parser.parse_args()
    if args.test:
        return test()

    SOURCE = path_split(args.SOURCE)
    ENCODE = path_split(args.ENCODE)
    DECODE = path_split(args.DECODE)

    for source_path, encode_path, decode_path in zip(SOURCE, ENCODE, DECODE):
        if args.verbose:
            print(f'Comparing source "{os.path.basename(source_path)}", encoded "{os.path.basename(encode_path)}", and decoded "{os.path.basename(decode_path)}" ...')
        compare_files(source_path, encode_path, decode_path, args.RESULT, args.verbose)
        if args.verbose:
            print('')


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


def compare_files(source_path, encode_path, decode_path, result_path, verbose=False):
    """
    计算误码率，压缩比和信源信息传输率，并将结果保存到 CSV 文件。

    source_path: 原始文件路径
    encode_path: 编码文件路径
    decode_path: 解码文件路径
    result_path: 结果保存的 CSV 文件路径
    """

    # 检查文件是否存在
    if not os.path.exists(source_path) or not os.path.exists(encode_path) or not os.path.exists(decode_path):
        raise FileNotFoundError("文件路径错误，文件不存在")

    source = np.fromfile(source_path, dtype='uint8')  # 读取原始文件数据
    encoded = np.fromfile(encode_path, dtype='uint8')  # 读取编码后的文件数据
    decoded = np.fromfile(decode_path, dtype='uint8')  # 读取解码后的文件数据

    compare_size = min(len(source), len(decoded))  # 取较小的文件大小作为比较大小

    if len(source) != len(decoded):
        print(f'[WARNING] These files have different sizes: {len(source)} (original), {len(decoded)} (decoded)')
        print(f'Comparing the first {compare_size} bytes only.')

    # 计算汉明误码率
    diff_total = np.unpackbits(source[:compare_size] ^ decoded[:compare_size]).sum()  # 统计不同的比特数
    error_rate = diff_total / (compare_size * 8)

    # 计算压缩比（编码前字节数 / 编码后字节数）
    compression_ratio = len(source) / len(encoded) if len(encoded) > 0 else 0

    # 计算编码前信源信息传输率（信息比特/字节）
    source_entropy = calc_entropy(calc_probability(source))     # 比特/字节
    source_rate = source_entropy / 8 * 8                        # 定长

    # 计算编码后信源信息传输率（信息比特/字节）
    encoded_entropy = calc_entropy(calc_probability(encoded))   # 比特/字节
    encoded_rate = encoded_entropy / len(encoded) * len(source) # 重复编码

    if not os.path.isfile(result_path):
        with open(result_path, 'a', newline='') as result_file:
            result_file.write('"X(source)","Y(encoded)","Z(decoded)","compression ratio","error rate","R(X)bit/byte","R(Y)bit/byte"\n')
    # 保存结果到 CSV 文件
    with open(result_path, 'a', newline='') as result_file:
        writer = csv.writer(result_file, quoting=csv.QUOTE_ALL)
        # 写入 CSV 内容
        writer.writerow([source_path, encode_path, decode_path, compression_ratio, error_rate, source_rate, encoded_rate])

    if verbose:
        print(f'Total {diff_total} bits are different.')
        print(f'Compression Ratio: {compression_ratio:.4f}')
        print(f'Error Rate: {error_rate:.8f}')
        print(f'Source Transmission Rate (before encoding): {source_entropy:.6f} bits/byte')
        print(f'Encoded Transmission Rate (after encoding): {encoded_entropy:.6f} bits/byte')


def calc_probability(data):
    """计算每个字节的概率分布"""
    file_size = len(data)
    byte_counts = np.histogram(data, bins=range(256))[0]
    probability = byte_counts / file_size
    return probability


def calc_information(p):
    """计算每个字节的信息量（单位：比特）"""
    p = p.copy()
    np.clip(p, np.spacing(1), None, out=p)
    information = - np.log2(p, out=p)
    return information


def calc_entropy(p):
    """计算信息熵"""
    entropy = (p * calc_information(p)).sum()
    return entropy


def binomialCoef(n, k):
    a = 1
    for i in range(k + 1, n + 1):
        a *= i
    b = math.factorial(n - k)
    return a / b


def theoryCalcError(n, p):
    """计算理论误码率"""
    if p < 0. or p > 1.:
        raise ValueError("Error rate of BSC must be between 0 & 1.")
    if not isinstance(n, int) or n < 1 or (n % 2 == 0):
        raise ValueError("Repeats must be a positive odd number.")
    Pe = 0.
    for k in range((n + 1) // 2, n + 1):
        bc = binomialCoef(n, k)
        Pe += bc * pow(p, k) * pow(1 - p, (n - k))
    return Pe


# 测试函数
def test():
    import calcErrorRateTest
    unittest.main(calcErrorRateTest, argv=['calcErrorRateTest'])


if __name__ == '__main__':
    main()
