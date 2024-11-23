import unittest
import os
import numpy as np
from byteSourceCoder import encode, decode, compare_file

class TestByteSourceCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 设置测试数据目录和文件路径
        cls.test_data_dir = '/test-data/'
        cls.pmf_file_name = cls.test_data_dir + 'pmf.byte.p0=0.8.csv'
        cls.source_file_name = cls.test_data_dir + 'source.p0=0.8.len=64KB.dat'
        cls.encoded_file_name = cls.test_data_dir + '_encoded.tmp'
        cls.decoded_file_name = cls.test_data_dir + '_decoded.tmp'

        # 确保测试数据目录存在
        if not os.path.exists(cls.test_data_dir):
            os.makedirs(cls.test_data_dir)

        # 生成测试源文件（模拟数据）
        np.random.seed(42)
        data = np.random.randint(0, 256, size=64 * 1024, dtype=np.uint8)
        data.tofile(cls.source_file_name)

        # 创建 PMF 文件（概率质量函数）
        pmf_data = [(i, 1 / 256.0) for i in range(256)]  # 使用均匀分布的概率
        with open(cls.pmf_file_name, 'w', newline='') as f:
            for symbol, probability in pmf_data:
                f.write(f"{symbol},{probability:.8f}\n")

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

    def test_encode(self):
        # 测试编码功能
        source_len, encoded_len = encode(self.pmf_file_name, self.source_file_name, self.encoded_file_name)
        self.assertGreater(source_len, 0, "源文件长度应大于 0")
        self.assertGreater(encoded_len, 0, "编码文件长度应大于 0")
        self.assertTrue(os.path.exists(self.encoded_file_name), "编码文件应已生成")

    def test_decode(self):
        # 测试解码功能
        encode(self.pmf_file_name, self.source_file_name, self.encoded_file_name)
        encoded_len, decoded_len = decode(self.encoded_file_name, self.decoded_file_name)
        self.assertGreater(decoded_len, 0, "解码文件长度应大于 0")
        self.assertTrue(os.path.exists(self.decoded_file_name), "解码文件应已生成")

    def test_compare_files(self):
        # 测试源文件和解码文件的比较
        encode(self.pmf_file_name, self.source_file_name, self.encoded_file_name)
        decode(self.encoded_file_name, self.decoded_file_name)
        diff_total = compare_file(self.source_file_name, self.decoded_file_name)
        self.assertEqual(diff_total, 0, "源文件和解码文件应完全相同")

if __name__ == '__main__':
    unittest.main()
