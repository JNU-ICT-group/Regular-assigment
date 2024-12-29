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
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to run (encode or decode)')

    parser.add_argument('INPUT1', type=str, nargs='?', help='path to input file 1')
    parser.add_argument('INPUT2', type=str, nargs='?', help='path to input file 2')
    parser.add_argument('RESULT', type=str, nargs='?', help='path to the result CSV file')

    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')

    # thory sub-command
    parser_calc = subparsers.add_parser('calc', help='calculate a thory case.')
    parser_calc.add_argument('LEN_CODE', type=int, help='Code Repeats.')
    parser_calc.add_argument('ERROR', type=float, help='Transmission error rate.')

    args = parser.parse_args()
    if args.test:
        return test()

    if args.command == 'calc':
        Pe = theoryCalcError(args.LEN_CODE, args.ERROR)
        print("Theory Error-Rate: %.8f" % Pe)
        return Pe

    INPUT1 = path_split(args.INPUT1)
    INPUT2 = path_split(args.INPUT2)

    for file1_path, file2_path in zip(INPUT1, INPUT2):
        print('Comparing source "%s" and decoded "%s" ...' % (os.path.basename(file1_path), os.path.basename(file2_path)))
        compare_file(file1_path, file2_path, args.RESULT)
        print('')


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


# 文件比较函数，比较两个文件的差异
def compare_file(file1_path, file2_path, result_path):
    """
    计算重复编码文件的误码率，并将结果保存到 CSV 文件。

    file1_path: str, 输入文件 1 的路径
    file2_path: str, 输入文件 2 的路径
    result_path: str, 结果保存的 CSV 文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        raise FileNotFoundError("文件路径错误，文件不存在")

    data1 = np.fromfile(file1_path, dtype='uint8')  # 读取第一个文件的数据
    data2 = np.fromfile(file2_path, dtype='uint8')  # 读取第二个文件的数据

    compare_size = min(data1.size, data2.size)  # 取较小的文件大小作为比较大小
    if data1.size != data2.size:  # 如果文件大小不同，输出警告
        print('[WARNING] These two files have different sizes (in bytes): %d vs %d' % (data1.size, data2.size))
        print('          Comparing the first %d bytes only.' % (compare_size))

    # 比较两个文件的数据，统计不同的字节数
    if compare_size == 0:
        print('[WARNING] These two files have least one Empty.')
        diff_total = 0
        error_rate = 0.0
    else:
        diff_total = np.unpackbits(data1[:compare_size] ^ data2[:compare_size]).sum()  # 统计不同字节的总数
        error_rate = diff_total / (compare_size * 8)

    # 保存结果到 CSV 文件
    with open(result_path, 'a', newline='') as result_file:
        writer = csv.writer(result_file)
        # 写入 CSV 内容
        writer.writerow([file1_path, file2_path, error_rate])

    print('Total %d bytes are different.' % (diff_total))

    return diff_total


def binomialCoef(n, k):
    a = 1
    for i in range(k+1, n+1): a *= i
    b = math.factorial(n - k)
    return a / b


def theoryCalcError(n, p):
    if p<0. or p>1.:
        raise ValueError("error_rate of BSC must between 0.&1.")
    if not isinstance(n, int) or n < 1 or (n % 2 == 0):
        raise ValueError("Repeats must positive prime number.")
    Pe = 0.
    for k in range((n+1)//2, n+1):
        bc = binomialCoef(n, k)
        # print(n, k, bc)
        Pe += bc * pow(p, k) * pow(1 - p, (n - k))
    return Pe


# 测试函数
def test():
    import calcErrorRateTest
    unittest.main(calcErrorRateTest, argv=['calcErrorRateTest'])


# 主程序入口
if __name__ == '__main__':
    main()
