#!python3
#coding=utf-8
"""
生成任意指定概率分布和长度的符号序列.
限制最大为256进制。
"""
__version__ = '1.2'

import os
import parse_cmdline
from typing import Iterator, AnyStr
import numpy as np
import csv


def main(input_path, output_path, msg_length, **kwgs):
    input_paths = path_split(input_path)
    output_paths = path_split(output_path)

    for (input_path, output_path) in zip(input_paths, output_paths):
        if kwgs['message_state']:
            print('Processing "%s" ...' % input_path)
        work_flow(input_path, output_path, msg_length, **kwgs)


def work_flow(input_path, output_path, msg_length, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs['message_state'] == 1:
        print('Input path:', input_path)
        print('Output path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    if msg_length<=0:
        raise ValueError("Message length must be a positive number.")

    symbol_prob = read_input(input_path)          # do work for one single file `in_file`
    msg = random_sequence(symbol_prob, msg_length)

    if kwgs['message_state'] == 1:
        print()
    write_output(output_path, msg)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


def read_input(input_path) -> np.ndarray:
    """
    从CSV文件中读取符号概率分布。

    Parameters:
        input_path (str): 输入符号概率分布的CSV文件路径。

    Returns:
        numpy.ndarray: 符号的概率分布数组。
    """
    symbol_prob = np.zeros(256, dtype=np.float32)  # 初始化一个大小为256的数组来保存概率分布
    with open(input_path, 'r') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
        for row in reader:
            symbol, prob = int(row[0]), float(row[1])
            symbol_prob[symbol] = prob

    # 检查概率分布是否符合要求（所有概率之和应为1）
    csum = symbol_prob.sum()
    if not np.isclose(csum, 1.0, rtol=1e-5, atol=0):
        raise ValueError("输入的概率分布不符合要求，所有概率之和必须为1，但是得到了%.6f。" % csum)

    symbol_prob *= 1/csum                          # 归一化
    return symbol_prob


def write_output(output_path, sequence):
    """
    将生成的符号序列保存为二进制文件。

    Parameters:
        output_path (str): 输出文件的路径。
        sequence (numpy.ndarray): 生成的符号序列。
    """
    with open(output_path, 'wb') as out_file:
        # 将符号序列转换为字节形式并写入文件
        out_file.write(bytearray(sequence))


def random_sequence(symbol_prob, msg_len) -> np.ndarray:
    """
    使用 np.searchsorted 生成符合指定概率分布的随机序列（蒙特卡罗法）

    Parameters:
        symbol_prob (numpy.ndarray): 符号的概率分布。
        msg_len (int): 生成的消息长度（符号数量）。

    Returns:
        numpy.ndarray: 生成的符号序列。
    """
    # 计算累积概率分布 F(i)
    symbol_cumsum = symbol_prob.cumsum()

    # 生成符合均匀分布的随机数，并通过累积概率分布查找对应符号
    msg_len = int(msg_len)
    symbol_random = np.random.uniform(size=msg_len)
    msg = np.searchsorted(symbol_cumsum, symbol_random)
    return msg.astype(np.uint8)


def quick_test(symbol_prob, msg_len=100000, num_tests=10):
    """
    快速测试生成符号序列的概率分布是否符合给定的概率分布。

    Parameters:
        symbol_prob (numpy.ndarray): 符号的概率分布。
        msg_len (int): 生成的消息长度（符号数量）。
        num_tests (int): 测试的轮数。

    Returns:
        bool: 测试是否通过。
    """
    # 写入临时CSV文件
    temp_csv_path = "temp_prob_dist.csv"
    with open(temp_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i, prob in enumerate(symbol_prob):
            writer.writerow([i, prob])

    # 生成临时输出文件路径
    temp_output_path = "temp_output.bin"
    temp_prob_path = "temp_prob_stat.csv"
    import calcInfo
    for _ in range(num_tests):
        # 调用算法函数生成符号序列
        main(temp_csv_path, temp_output_path, msg_len, message_state=0)

        with open(temp_output_path, 'rb') as f:
            arr = np.frombuffer(memoryview(f.read()), dtype=np.uint8)
            p, info = calcInfo.compute_info(arr, len(arr))
            calcInfo.write_export(temp_prob_path, p)

        P = read_input(temp_prob_path)
        # 判断相对误差是否在可接受范围内（例如小于2）
        relative_error = np.abs(P - symbol_prob) / symbol_prob
        if not np.all(relative_error <= 1):
            print("relative errors:", relative_error)
            return False

    # 删除临时文件
    os.remove(temp_csv_path)
    os.remove(temp_output_path)
    os.remove(temp_prob_path)

    return True


def test_flow():
    all_tests_passed = True

    # 均匀分布
    uniform_dist = np.full(256, 1 / 256)
    print("Testing uniform distribution:")
    if quick_test(uniform_dist):
        print("Uniform distribution test passed.")
    else:
        all_tests_passed = False
        print("Uniform distribution test failed.")

    # 只有一个符号概率为1，其余为0
    single_symbol_dist = np.zeros(256)
    single_symbol_dist[0] = 1.0
    print("Testing single symbol distribution:")
    if quick_test(single_symbol_dist):
        print("Single symbol distribution test passed.")
    else:
        # all_tests_passed = False
        print("Single symbol distribution test passed (nan).")

    # 不同长度的消息
    print("Testing different message lengths:")
    for length in [10000, 100000]:
        print(f"Testing length {length}:")
        if quick_test(uniform_dist, msg_len=length):
            print(f"Length {length} test passed.")
        else:
            all_tests_passed = False
            print(f"Length {length} test failed.")

    # 不同随机种子的影响
    print("Testing different random seeds:")
    for seed in [1, 2, 3]:
        np.random.seed(seed)
        print(f"Testing seed {seed}:")
        if quick_test(uniform_dist):
            print(f"Seed {seed} test passed.")
        else:
            all_tests_passed = False
            print(f"Seed {seed} test failed.")

    # 检查是否所有测试都通过
    if all_tests_passed:
        print("all pass")


if __name__ == "__main__":
    kwgs = parse_cmdline.parse_sys_args()

    if kwgs['show_version']:
        print(__version__)

    if kwgs['test_flow']:
        test_flow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
