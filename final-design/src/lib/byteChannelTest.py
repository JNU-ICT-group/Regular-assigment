import os
import byteChannel
import numpy as np


def quick_test(input_path, output_path, noise_path) -> bool:
    """
    快速测试生成符号序列的概率分布是否符合给定的概率分布。

    Returns:
        bool: 测试是否通过。
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
        byteChannel.write_output(file_path, data)
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


if __name__ == '__main__':
    test_flow()