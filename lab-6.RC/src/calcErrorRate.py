""" A basic program calculate the error rate of repetition coding file.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |LEN  : uint8, code length n, must be odd number and 2 < n < 10
        |source length : uint32, number of symbols in source divided by 8
Payload |codeword sequence : many unit8

Note: This program is intended for use in course, Principle of Information and Coding Theory.

"""

import csv
import os
import argparse

# Non-standard library
import numpy as np

__author__ = "Zhang, Pengyang; Chen, Jin; "
__email__ = "miracle@stu2022.jnu.edu.cn"
__version__ = "20241212.2220"


def main():
    parser = argparse.ArgumentParser(description="Lossless source coder for encoding and decoding.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to run (encode or decode)')

    # Compare sub-command
    parser_compare = subparsers.add_parser('compare', help='Compare source file and decoded file')
    parser_compare.add_argument('INPUT1', type=str, help='path to input file 1')
    parser_compare.add_argument('INPUT2', type=str, help='path to input file 2')
    parser_compare.add_argument('RESULT', type=str, help='path to the result CSV file')

    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')

    args = parser.parse_args()

    # Execute based on sub-command
    if args.command == 'compare':
        print('Comparing source "%s" and decoded "%s" ...' % (os.path.basename(args.SOURCE), os.path.basename(args.OUTPUT)))
        compare_file(args.SOURCE, args.OUTPUT, args.RESULT)
        print('')

    elif args.test:
        test()
    else:
        parser.print_help()


# 文件比较函数，比较两个文件的差异
def compare_file(file_name_1, file_name_2, file_output):
    """Compare two files and count number of different bytes."""
    data1 = np.fromfile(file_name_1, dtype='uint8')  # 读取第一个文件的数据
    data2 = np.fromfile(file_name_2, dtype='uint8')  # 读取第二个文件的数据

    compare_size = min(data1.size, data2.size)  # 取较小的文件大小作为比较大小
    if data1.size != data2.size:  # 如果文件大小不同，输出警告
        print('[WARNING] These two files have different sizes (in bytes): %d vs %d' % (data1.size, data2.size))
        print('          Comparing the first %d bytes only.' % (compare_size))

    # 比较两个文件的数据，统计不同的字节数
    diff_total = np.sum(data1[:compare_size] != data2[:compare_size])  # 统计不同字节的总数
    print('Total %d bytes are different.' % (diff_total))

    return diff_total


# 测试函数
def test():
    import unittest
    ...


# 主程序入口
if __name__ == '__main__':
    main()
