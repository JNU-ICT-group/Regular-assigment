import unittest
import os
import csv
import numpy as np
from byteSourceCoder import encode, decode, compare_file

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
        cls.test_data_dir = 'test-data'
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
        # np.random.seed(42)
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
        pass

    def test_unmapped_distribution(self):
        # 生成测试源文件（模拟数据）
        # np.random.seed(42)
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
