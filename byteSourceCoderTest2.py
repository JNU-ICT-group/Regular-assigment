import unittest
import os
import csv
import numpy as np
from byteSourceCoder import encode, decode, compare_file


# 模拟信源编码指标计算模块
def calc_compression_metrics(input_path, encoded_path, output_path, **kwgs):
    """
    计算编码过程的相关指标：压缩比、平均码长、编码效率以及信息熵。
    """
    source, x_size = read_input(input_path)
    encoded, y_size = read_input(encoded_path)
    p_source = calc_probability(source)
    p_encoded = calc_probability(encoded)

    entropy_source = calc_entropy(p_source) / 8
    entropy_encoded = calc_entropy(p_encoded) / 8
    ratio = calc_compress_ratio(x_size, y_size)
    avg_len = calc_code_avlen(x_size, y_size)
    efficiency = calc_efficiency(ratio)

    info = [ratio, avg_len, efficiency, entropy_source, entropy_encoded]
    write_compression_metrics(output_path, input_path, encoded_path, info)


def read_input(in_file_name) -> (np.ndarray, int):
    """读取文件数据并返回数组及文件大小"""
    arr = np.fromfile(in_file_name, dtype=np.uint8)
    return arr, len(arr)


def calc_probability(data) -> np.ndarray:
    """计算每个字节的概率分布"""
    file_size = len(data)
    byte_counts = np.histogram(data, bins=range(257))[0]
    probability = np.divide(byte_counts, file_size, dtype=np.float32)
    return probability


def calc_entropy(p: np.ndarray) -> float:
    """计算信息熵"""
    p = p.copy()
    np.clip(p, np.spacing(1), None, out=p)
    information = - np.log2(p, out=p)
    entropy = (p * information).sum()
    return entropy


def calc_compress_ratio(size0, size1) -> float:
    """计算压缩比"""
    return size1 / size0


def calc_code_avlen(size0, size1) -> float:
    """计算平均码长"""
    return 8 * size1 / size0


def calc_efficiency(ratio: float) -> float:
    """计算编码效率"""
    return (1. - ratio) * 100


def write_compression_metrics(out_file_name, in_file_name, encode_file_name, info):
    """写入编码指标数据到CSV文件"""
    if not os.path.isfile(out_file_name):
        out_file = open(out_file_name, 'w', newline='', encoding='utf-8')
        out_file.write('"X(source)","Y(encoded)","compression ratio","L(avg code len)bit/byte","η(efficiency)%","H(X)","H(Y)"\n')
    else:
        out_file = open(out_file_name, 'a', newline='', encoding='utf-8')
    with out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        row = [in_file_name, encode_file_name]
        for v in info:
            row.append("{:.6f}".format(v))
        writer.writerow(row)


# 测试模块
def test_once(pmf_file_name, source_file_name, encoded_file_name, decoded_file_name):
    print('Encoding...')
    (source_len, encoded_len) = encode(pmf_file_name, source_file_name, encoded_file_name)
    print(' source len:', source_len)  # 打印源数据长度
    print('encoded len:', encoded_len)  # 打印编码后的数据长度
    print('     ratio :', (source_len / encoded_len if encoded_len else np.nan))  # 打印压缩比
    print('')

    print('Decoding...')
    (encoded_len, decoded_len) = decode(encoded_file_name, decoded_file_name)  # 执行解码
    print('encoded len:', encoded_len)  # 打印编码数据长度
    print('decoded len:', decoded_len)  # 打印解码数据长度
    print('')

    print('Comparing source and decoded...')
    diff_total = compare_file(source_file_name, decoded_file_name)  # 比较源文件和解码后的文件
    print('')
    return diff_total


class TestByteSourceCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 设置测试数据目录和文件路径
        cls.test_data_dir = 'test-data1'
        cls.pmf_file_name = os.path.join(cls.test_data_dir, 'pmf.csv')
        cls.source_file_name = os.path.join(cls.test_data_dir, 'source.dat')
        cls.encoded_file_name = os.path.join(cls.test_data_dir, '_encoded.tmp')
        cls.decoded_file_name = os.path.join(cls.test_data_dir, '_decoded.tmp')

        # 确保测试数据目录存在
        if not os.path.exists(cls.test_data_dir):
            os.makedirs(cls.test_data_dir)

    @classmethod
    def tearDownClass(cls):
        # 删除临时文件
        if os.path.exists(cls.encoded_file_name):
            os.remove(cls.encoded_file_name)
        if os.path.exists(cls.decoded_file_name):
            os.remove(cls.decoded_file_name)
        if os.path.exists(cls.pmf_file_name):
            os.remove(cls.pmf_file_name)
        if os.path.exists(cls.source_file_name):
            os.remove(cls.source_file_name)

    def test_uniform_distribution(self):
        # 生成测试源文件（模拟数据）
        data = np.random.randint(0, 256, size=64 * 1024, dtype=np.uint8)
        data.tofile(self.source_file_name)

        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, round(1 / 256.0, 6)) for i in range(256)]  # 使用均匀分布的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        self.assertEqual(diff_total, 0, "源文件和解码文件应完全相同")

    def test_empty_file(self):
        open(self.source_file_name, 'wb').close()
        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, 0.0) for i in range(256)]  # 使用均匀分布的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        self.assertEqual(diff_total, 0, "源文件和解码文件应完全相同")

    def test_unmapped_distribution(self):
        # 生成测试源文件（模拟数据）
        data = np.random.randint(0, 256, size=64 * 1024, dtype=np.uint8)
        data.tofile(self.source_file_name)

        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, round(i / 256.0, 6)) for i in range(256)]  # 使用分布不匹配的概率
        with open(self.pmf_file_name, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONE)
            writer.writerows(pmf_data)
        # 测试源文件和解码文件的比较
        diff_total = test_once(self.pmf_file_name, self.source_file_name, self.encoded_file_name, self.decoded_file_name)
        self.assertEqual(diff_total, 0, "源文件和解码文件应完全相同")


if __name__ == '__main__':
    unittest.main()
