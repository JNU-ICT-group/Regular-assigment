""" Generate a channel with specified error transmission probability of a BSC.

This program is intended for used in course, Principle of Information and Coding Theory.
Usage details can be displayed by passing command line argument `--help`.

Note: All information contents calculated are bit-wise, i.e. in (information-)bit per (binary-)bit.
"""

# Standard library
import os.path
import argparse
import time
import csv
from pathlib import Path
import struct
# Non-standard library
import numpy as np

__author__ = "Guo, Jiangling; "
__email__ = "miracle@stu2022.jnu.edu.cn; "
__version__ = "20241104.1635"


def main(input_path, noise_path, output_path, **kwgs):
    input_paths = path_split(input_path)
    output_paths = path_split(output_path)
    noises = path_split(noise_path)

    if len(input_paths) * len(noises) != len(output_paths):
        raise ValueError("INPUT(%d),OUTPUT(%d),NOISE(%d) must have the size like "
                         "INPUT.length*NOISE.length = OUTPUT.length." %
                         (len(input_paths), len(output_paths), len(noises)))

    output_paths = iter(output_paths)
    for input_path in input_paths:
        if kwgs['message_state']:
            print('Processing INPUT "%s" ...' % input_path)
        for noise in noises:
            output_path = next(output_paths)
            if kwgs['message_state']:
                print('\tProcessing OUTPUT "%s" with noise=%.4f...' % (output_path, noise))
            work_flow(input_path, noise, output_path, **kwgs)


def path_split(path):
    return tuple(filter(None, map(str.strip, ''.join(filter(lambda c: "'" != c != '"', path)).split(';'))))


def work_flow(input_path, noise_path, output_path, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('Input path:', input_path)
        print('Noise path:', noise_path)
        print('Output path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist folder or file.")
    if os.path.exists(noise_path) and not os.path.isfile(noise_path):
        raise RuntimeError("noise_path must be a file, not a folder.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    input_data = read_input(input_path)
    noise_data = read_input(noise_path)

    if kwgs['message_state'] == 1:
        print()

    write_output(output_path, byte_channel(input_data, noise_data))


def read_input(input_path):
    # 使用 NumPy 直接读取文件并转换为 uint8 数组
    uint8_array = np.fromfile(input_path, dtype=np.uint8)
    return uint8_array


def byte_channel(input_data, noise_data):
    """
    模拟二元对称信道 (BSC)，将噪声作用在输入消息上。

    Parameters:
        input_data (str): 输入消息文件的路径。
        noise_data (str): 噪声文件的路径。
    """
    # 检查输入和噪声文件大小是否一致
    if len(input_data) != len(noise_data):
        raise ValueError("输入文件和噪声文件的大小必须相同。")
    output_data = np.bitwise_xor(input_data, noise_data)
    print(len(output_data))
    return output_data


def write_output(output_path, output_data):
    # 将结果写入输出文件
    with open(output_path, 'wb') as out_file:
        out_file.write(bytearray(output_data))
    print(f"输出文件已保存到 {output_path}")


def calculate_error_rate_test(input_file, output_file):
    with open(input_file, 'rb') as f_in, open(output_file, 'rb') as f_out:
        input_data = f_in.read()
        output_data = f_out.read()

    # 确保两个文件长度一致
    assert len(input_data) == len(output_data), "Input and output files must have the same length"

    # 计算比特错误数量
    error_count = sum(1 for in_bit, out_bit in zip(input_data, output_data) if in_bit != out_bit)
    total_bits = len(input_data) * 8  # 每个字节8个比特

    error_rate = error_count / total_bits
    return error_rate


def test_error_probability_test(input_file, output_file):
    error_rate = calculate_error_rate_test(input_file, output_file)
    print(f"Measured error rate: {error_rate}")

    # 验证错误率是否接近预期值（允许小范围误差，例如0.02）
    assert np.isclose(error_rate, 0.25, atol=0.02), \
        f"Error rate mismatch: expected {0.25}, got {error_rate}"


def test_flow() -> None:
    test_error_probability_test("test.dat`", "testout.dat")

    all_tests_passed = True

    # 检查是否所有测试都通过
    if all_tests_passed:
        print("all pass")


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for byteChannel.")
    parser.add_argument('INPUT', nargs='?', help='Input file path')
    parser.add_argument('NOISE', nargs='?', help='Error transmission probability of BSC.')
    parser.add_argument('OUTPUT', nargs='?', help='Output file path')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    args = parser.parse_args()
    return dict(
        input_path=args.INPUT,
        noise_path=args.NOISE,
        output_path=args.OUTPUT,
        base_path=args.dir,
        message_state=1 if args.O else 2 if args.S else 0,
        test_flow=args.test,
        show_version=args.version,
    )


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['show_version']:
        print(__version__)

    if kwgs['test_flow']:
        test_flow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
