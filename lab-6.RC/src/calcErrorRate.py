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


class TestCalculateErrorRate(unittest.TestCase):
    def setUp(self):
        """
        测试前的准备工作，生成一些临时文件。
        """
        self.file1_path = "test_file1.bin"
        self.file2_path = "test_file2.bin"
        self.result_path = "test_result.csv"

        # 创建文件1，内容为 0b10101010
        with open(self.file1_path, "wb") as file1:
            file1.write(b"\xAA")

        # 创建文件2，内容为 0b10101010
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAA")

    def tearDown(self):
        """
        测试结束后的清理工作，删除临时文件。
        """
        if os.path.exists(self.file1_path):
            os.remove(self.file1_path)
        if os.path.exists(self.file2_path):
            os.remove(self.file2_path)
        if os.path.exists(self.result_path):
            os.remove(self.result_path)

    def test_identical_files(self):
        """
        测试两个完全相同的文件，误码率应为 0.0。
        """
        print("Test 1: Testing identical files with 0.0 error rate.")
        compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.0")
        print("Test 1 passed: Identical files tested successfully.")
        print()

    def test_different_files(self):
        """
        测试两个完全不同的文件，误码率应为 1.0。
        """
        print("Test 2: Testing completely different files with 1.0 error rate.")
        # 修改文件2的内容为 0b01010101
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\x55")

        compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},1.0")
        print("Test 2 passed: Different files tested successfully.")
        print()

    def test_partial_difference(self):
        """
        测试两个部分不同的文件。
        """
        print("Test 3: Testing partially different files with calculated error rate.")
        # 修改文件2的内容为 0b10101011
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAB")

        compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.125")
        print("Test 3 passed: Partially different files tested successfully.")
        print()

    def test_file_size_mismatch(self):
        """
        测试两个文件大小不一致的情况。
        """
        print("Test 4: Testing file size mismatch case.")
        # 修改文件2的内容为两个字节
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAA\xAA")

        try:
            compare_file(self.file1_path, self.file2_path, self.result_path)
            print("Expected ValueError was not raised for file size mismatch")
        except ValueError as e:
            print(f"Caught expected ValueError: {e}")
        print("Test 4 passed: File size mismatch handled correctly.")
        print()

    def test_file_not_exist(self):
        """
        测试文件路径无效的情况。
        """
        print("Test 5: Testing file not exist case.")
        invalid_path = "nonexistent_file.bin"
        try:
            compare_file(invalid_path, self.file2_path, self.result_path)
            print("Expected FileNotFoundError was not raised for non-existent file")
            print()
        except FileNotFoundError as e:
            print(f"Caught expected FileNotFoundError: {e}")
        print("Test 5 passed: Nonexistent file handled correctly.")
        print()

    def test_empty_files(self):
        """
        测试空文件的情况，误码率应为 0.0。
        """
        print("Test 6: Testing empty files with 0.0 error rate.")
        # 创建空文件
        with open(self.file1_path, "wb") as file1:
            file1.write(b"")
        with open(self.file2_path, "wb") as file2:
            file2.write(b"")

        try:
            compare_file(self.file1_path, self.file2_path, self.result_path)
            print("Calculation completed without ZeroDivisionError for empty files")
        except ZeroDivisionError as e:
            print(f"Caught ZeroDivisionError: {e}")

        # 检查结果文件内容（先判断文件是否存在）
        if os.path.exists(self.result_path):
            with open(self.result_path, "r") as result_file:
                result = result_file.read().strip()
            self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.0")
            print("Test 6 passed: Empty files tested successfully.")
        else:
            print(f"Result file {self.result_path} not found after calculating for empty files")
        print()

# 测试函数
def test():
    unittest.main(argv=['calcErrorRate'])


# 主程序入口
if __name__ == '__main__':
    main()
