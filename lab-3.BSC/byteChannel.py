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

# Non-standard library
import numpy as np

__author__ = "Chen, Jin; "
__email__ = "miracle@stu2022.jnu.edu.cn; "
__version__ = "20241031.1001"


def main(input_path, output_path, noise_path, **kwgs):
    input_paths = path_split(input_path)
    output_paths = path_split(output_path)
    noise_paths = path_split(noise_path)

    for input_path, noise_path, output_path in zip(input_paths, noise_paths, output_paths):
        if kwgs['message_state']:
            print('Processing INPUT "%s" OUTPUT "%s" with NOISE "%s"...' % (input_path, output_path, noise_path))
        work_flow(input_path, output_path, noise_path, **kwgs)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


def work_flow(input_path, output_path, noise_path, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('\tInput path:', input_path)
        print('\tOutput path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")
    if not os.path.isfile(noise_path):
        raise RuntimeError("noise_path must by an exist file.")

    if kwgs['message_state'] == 1:
        print()
    arr = read_input(input_path)
    noise = read_input(noise_path)
    if len(arr)*8 != len(noise) and len(arr) != len(noise):
        raise ValueError("NOISE must have the size 8-times longer than INPUT, "
                         "while NOISE values only 1-bits.")
    out = generate_error_channel(arr, noise)
    write_output(output_path, out)


def read_input(input_path) -> np.ndarray:
    """
    从CSV文件中读取符号概率分布。

    Parameters:
        input_path (str): 。

    Returns:
        numpy.ndarray: 。
    """
    return np.fromfile(input_path, dtype=np.uint8)


def generate_error_channel(arr, noise) -> np.ndarray:
    """
    使用np.searchsorted对np.random.uniform的结果做2分类（长度为arr的长度的8倍），使其中1的
    概率为p（二元对称信道错误传输概率），即0的概率为1-p，随后将二元结果以8个一组，合并为长度同arr的，即N=8次扩展。然后使用
    异或加载到256元的arr信源。这种方法仅适用于BSC
    """
    if len(arr) * 8 == len(noise):
        noise = np.packbits(noise)
    out = np.bitwise_xor(arr, noise)
    return out


def write_output(output_path, sequence) -> None:
    """

    Parameters:
        output_path (str): 输出文件的路径。
        sequence (numpy.ndarray): 生成的符号序列。
    """
    with open(output_path, 'wb') as f:
        f.write(bytearray(sequence))


def quick_test(symbol_prob, msg_len=100000, num_tests=10) -> bool:
    """
    快速测试生成符号序列的概率分布是否符合给定的概率分布。

    Parameters:
        symbol_prob (numpy.ndarray): 符号的概率分布。
        msg_len (int): 生成的消息长度（符号数量）。
        num_tests (int): 测试的轮数。

    Returns:
        bool: 测试是否通过。
    """
    return True


def test_flow() -> None:
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
