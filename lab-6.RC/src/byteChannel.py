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
        if kwgs.get('message_state'):
            print('Processing INPUT "%s" OUTPUT "%s" with NOISE "%s"...' % (input_path, output_path, noise_path))
        work_flow(input_path, output_path, noise_path, **kwgs)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


def work_flow(input_path, output_path, noise_path, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs.get('message_state') == 1:
        print('\tInput path:', input_path)
        print('\tOutput path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")
    if not os.path.isfile(noise_path):
        raise RuntimeError("noise_path must by an exist file.")

    if kwgs.get('message_state') == 1:
        print()
    arr = read_input(input_path)
    noise = read_input(noise_path)
    if len(arr)*8 != len(noise) and len(arr) != len(noise):
        raise ValueError("NOISE(%d) must have the size 8-times longer than INPUT(%d), "
                         "while NOISE values only 1-bits." % (len(noise), len(arr)))
    out = generate_error_channel(arr, noise)
    write_output(output_path, out)


def read_input(input_path) -> np.ndarray:
    """
    从CSV文件中读取信源数据。

    Parameters:
        input_path (str): 文件路径。

    Returns:
        numpy.ndarray: 256元信源数据。
    """
    return np.fromfile(input_path, dtype=np.uint8)


def generate_error_channel(arr, noise) -> np.ndarray:
    """
    使用np.searchsorted对np.random.uniform的结果做分类，使其中1的概率为p（二元对称信道错误传输概率），
    即0的概率为1-p，为了方便使用byteSource产生随机序列，将二元概率空间以8个bit一组，合并为1byte长度，即N=8次扩展。
    然后使用异或将NOISE加载到256元的信源X上。这种方法仅适用于BSC

    Parameters:
        arr (numpy.ndarray): 信源X。
        noise (numpy.ndarray): 信道的噪声。

    Returns:
        numpy.ndarray: 信道输出的信源Y。
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
    sequence.tofile(output_path)


def quick_test(input_path, output_path, noise_path) -> bool:
    """
    快速测试生成符号序列的概率分布是否符合给定的概率分布。

    Returns:
        bool: 测试是否通过。
    """

    work_flow(input_path, output_path, noise_path)
    input_data = read_input(input_path)
    noise_data = read_input(noise_path)
    output_data = read_input(output_path)
    # 逐位比较并统计不同位的数量
    test_differences = np.bitwise_xor(input_data, output_data)
    real_differences = noise_data
    test_error_count = np.unpackbits(test_differences).sum(dtype=np.uint32)
    real_error_count = np.unpackbits(real_differences).sum(dtype=np.uint32)

    # 计算错误率
    total_bits = len(output_data) * 8  # 每个 uint8 有 8 位
    test_error_rate = test_error_count / total_bits
    real_error_rate = real_error_count / total_bits
    if test_error_rate == real_error_rate:
        print("错误传输概率：", test_error_rate)
    else:
        print("错误传输概率：%f 实测：%f，测试不通过" % (real_error_rate,  test_error_rate))
        return False
    return True


def test_flow(msg_len=100000) -> None:
    """

    Parameters:
        msg_len (int): 生成的消息长度（符号数量）。

    """
    import uuid

    # 生成特殊情况文件三种如下
    def generate_all_zeros(length):
        """
        生成一个全为0的数组，并保存为二进制文件。

        参数:
            length (int): 数组的长度。

        返回:
            str: 保存的二进制文件的完整路径。
        """
        data = np.zeros(length, dtype='uint8')
        return save_to_file(data)

    def generate_half_zeros_half_ones(length):
        """
        生成一个一半为0一半为1的数组，并保存为二进制文件。

        参数:
            length (int): 数组的长度。

        返回:
            str: 保存的二进制文件的完整路径。
        """
        data = np.zeros(length, dtype='uint8')
        mid_point = length // 2
        data[mid_point:] = 0xFF
        return save_to_file(data)

    def generate_alternating_zeros_ones(length):
        """
        生成一个交替为0和1的数组，并保存为二进制文件。

        参数:
            length (int): 数组的长度。

        返回:
            str: 保存的二进制文件的完整路径。
        """
        data = np.full(length, 0b0101_0101, dtype='uint8')
        return save_to_file(data)

    def save_to_file(data):
        """
        将数组数据保存为一个随机生成的二进制文件，并返回文件路径。

        参数:
            data (numpy.ndarray): 要保存的数组数据。

        返回:
            str: 保存的二进制文件的完整路径。
        """
        # 使用 uuid 生成一个唯一的文件名
        random_filename = "{}.bin".format(uuid.uuid4())
        # 获取当前工作目录并构建完整路径
        file_path = os.path.join(os.getcwd(), random_filename)
        # 将数组数据保存为二进制文件
        write_output(file_path, data)
        # 返回文件路径
        return file_path

    def delete_temp_file(file_path):
        """
        删除临时文件
        :param file_path: 临时文件路径
        """
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"文件不存在: {file_path}")

    # 文件名称列表
    file_names = ["全0文件", "半0半1文件", "01交替文件"]

    files = [
        generate_all_zeros(msg_len),
        generate_half_zeros_half_ones(msg_len),
        generate_alternating_zeros_ones(msg_len)
    ]
    all_tests_passed = True

    for i, file1 in enumerate(files):
        for j, file2 in enumerate(files):
            print(f"Processing files:H(X) {file_names[i]} and H(N){file_names[j]}")
            output_file = f'outfile{i}{j}.dat'
            all_tests_passed &= quick_test(file1, output_file, file2)
            delete_temp_file(output_file)

    # 删除所有输出文件
    for file in files:
        delete_temp_file(file)
    # 检查是否所有测试都通过
    if all_tests_passed:
        print("All passed.")


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
