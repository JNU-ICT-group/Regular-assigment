import os
import byteChannel
import numpy as np
import uuid
import csv

# 计算信息熵、冗余度等的功能模块
bit_counts = np.uint8(bytearray(map(int.bit_count, range(256))))


def calcDMSInfo(input_path, output_path, **kwgs) -> [float]:
    """计算二元离散无记忆信源（DMS）的指标"""

    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)

    arr, x_size = read_input(input_path)
    p, info = compute_info(arr, x_size)

    write_output(output_path, input_path, info, x_size)
    return p, info


def quick_test(input_path, output_path, noise_path) -> bool:
    """
    快速测试生成符号序列的概率分布是否符合给定的概率分布。
    """

    byteChannel.work_flow(input_path, output_path, noise_path)
    input_data = byteChannel.read_input(input_path)
    noise_data = byteChannel.read_input(noise_path)
    output_data = byteChannel.read_input(output_path)

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
        print("错误传输概率：%f 实测：%f，测试不通过" % (real_error_rate, test_error_rate))
        return False
    return True


def test_flow(msg_len=100000) -> None:
    """生成测试消息并运行概率分布计算与错误测试"""

    # 生成特殊情况文件三种如下
    def generate_all_zeros(length):
        """
        生成一个全为0的数组，并保存为二进制文件。
        """
        data = np.zeros(length, dtype='uint8')
        return save_to_file(data)

    def generate_half_zeros_half_ones(length):
        """
        生成一个一半为0一半为1的数组，并保存为二进制文件。
        """
        data = np.zeros(length, dtype='uint8')
        mid_point = length // 2
        data[mid_point:] = 0xFF
        return save_to_file(data)

    def generate_alternating_zeros_ones(length):
        """
        生成一个交替为0和1的数组，并保存为二进制文件。
        """
        data = np.full(length, 0b0101_0101, dtype='uint8')
        return save_to_file(data)

    def save_to_file(data):
        """
        将数组数据保存为一个随机生成的二进制文件，并返回文件路径。
        """
        random_filename = "{}.bin".format(uuid.uuid4())
        file_path = os.path.join(os.getcwd(), random_filename)
        byteChannel.write_output(file_path, data)
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

            # 运行 DMS 信息计算模块
            dms_output_file = f'dms_output{i}{j}.csv'
            calcDMSInfo(file1, dms_output_file)

    # 删除所有输出文件
    for file in files:
        delete_temp_file(file)
    # 检查是否所有测试都通过
    if all_tests_passed:
        print("All tests passed.")


def read_input(in_file_name) -> (np.ndarray, int):
    """使用numpy的fromfile函数读取文件"""
    arr = np.fromfile(in_file_name, dtype=np.uint8)
    return arr, len(arr)


def compute_info(arr, x_size) -> (np.ndarray, (float, float, float)):
    """计算信息熵、冗余度"""
    if x_size == 0:
        return (np.zeros(256, dtype=np.float32), (0.0, 0.0, 0.0))  # 避免空文件导致的问题

    # 计算每个字节的近似概率
    probability = calc_probability(arr[:x_size])
    # 计算信息熵
    prob0 = calc_prob0(probability)
    entropy = calc_entropy(probability) / 8
    redundancy = calc_redundancy(prob0)

    return probability, (prob0, entropy, redundancy)


def calc_probability(data) -> np.ndarray:
    """计算每个字节的近似概率"""
    file_size = len(data)
    byte_counts = np.histogram(data, bins=range(257))[0]
    probability = np.divide(byte_counts, file_size, dtype=np.float32)
    return probability


def calc_entropy(p: np.ndarray) -> float:
    """计算信息熵，即平均每个字节的信息量"""
    entropy = (p * calc_information(p)).sum()
    return entropy


def calc_information(p: np.ndarray) -> np.ndarray:
    """计算每个字节的信息量（单位：比特）"""
    p = p.copy()
    np.clip(p, np.spacing(1), None, out=p)
    information = - np.log2(p, out=p)
    return information


def calc_prob0(prob) -> float:
    return 1. - (prob * bit_counts).sum() / 8


def calc_redundancy(p0: float) -> float:
    return 1. - calc_entropy(np.float32([p0, 1 - p0]))


def write_output(out_file_name, in_file_name, info, x_size):
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
        out_file.write('"X(source)","P(0)","H(X)","redundancy","msg length"\n')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        row = [in_file_name]
        for v in info:
            row.append("{:.6f}".format(v))
        row.append(x_size)
        writer.writerow(row)


if __name__ == '__main__':
    test_flow()
