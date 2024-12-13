""" A basic program calculate the error rate of repetition coding file.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |LEN  : uint8, code length n, must be odd number and 2 < n < 10
        |source length : uint32, number of symbols in source divided by 8
Payload |codeword sequence : many uint
End |pad : some bits as 0

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

    parser.add_argument('INPUT1', type=str, help='path to input file 1')
    parser.add_argument('INPUT2', type=str, help='path to input file 2')
    parser.add_argument('RESULT', type=str, help='path to the result CSV file')

    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')

    args = parser.parse_args()
    INPUT1 = path_split(args.INPUT1)
    INPUT2 = path_split(args.INPUT2)

    for file1_path, file2_path in zip(INPUT1, INPUT2):
        print('Comparing source "%s" and decoded "%s" ...' % (os.path.basename(file1_path), os.path.basename(file2_path)))
        compare_file(file1_path, file2_path, args.RESULT)
        print('')

    if args.test:
        test()


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
        print("文件路径错误，文件不存在")
        return

    data1 = np.fromfile(file1_path, dtype='uint8')  # 读取第一个文件的数据
    data2 = np.fromfile(file2_path, dtype='uint8')  # 读取第二个文件的数据

    compare_size = min(data1.size, data2.size)  # 取较小的文件大小作为比较大小
    if data1.size != data2.size:  # 如果文件大小不同，输出警告
        print('[WARNING] These two files have different sizes (in bytes): %d vs %d' % (data1.size, data2.size))
        print('          Comparing the first %d bytes only.' % (compare_size))

    # 比较两个文件的数据，统计不同的字节数
    diff_total = np.sum(data1[:compare_size] != data2[:compare_size])  # 统计不同字节的总数
    error_rate = diff_total / compare_size

    # 保存结果到 CSV 文件
    with open(result_path, 'a', newline='') as result_file:
        writer = csv.writer(result_file)
        # 写入 CSV 内容
        writer.writerow([file1_path, file2_path, error_rate])

    print('Total %d bytes are different.' % (diff_total))

    return diff_total


# 测试函数
def test():
    import unittest
    ...


# 主程序入口
if __name__ == '__main__':
    main()
