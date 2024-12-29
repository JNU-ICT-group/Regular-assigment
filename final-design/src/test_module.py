from calcInfo import main
import os
import numpy as np
import unittest

class TestInformationContent(unittest.TestCase):

    def setUp(self):
        """设置测试环境"""
        self.test_file_path = 'test\\test_file{:02d}.bin'
        self.output_csv_path = 'test\\test_output.csv'

    def tearDown(self):
        """清理测试环境"""

    def test_TC01_empty_file(self):
        """TC01：创建一个空文件，预期信息量为 0"""
        if os.path.exists(self.output_csv_path):
            os.remove(self.output_csv_path)
        path = self.test_file_path.format(1)
        with open(path, 'wb') as f:
            f.write(b'')

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertEqual(entropy, 0.0)

    def test_TC02_single_char_file(self):
        """TC02：创建一个包含单个字符的文件，预期信息量为 0"""
        path = self.test_file_path.format(2)
        with open(path, 'wb') as f:
            f.write(b'A')

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertAlmostEqual(entropy, 0.0, places=6)

    def test_TC03_multiple_same_chars_file(self):
        """TC03：创建多个相同字符的文件，预期信息量为 0"""
        path = self.test_file_path.format(3)
        with open(path, 'wb') as f:
            f.write(b'AAAA')

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertAlmostEqual(entropy, 0.0, places=6)

    def test_TC04_different_chars_file(self):
        """TC04：创建一个包含不同字符的文件，检验性能（预期信息量大于 1）"""
        path = self.test_file_path.format(4)
        with open(path, 'wb') as f:
            f.write(b'ABCD')

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertGreater(entropy, 1.0)

    def test_TC05_full_byte_range_file(self):
        """TC05：创建包含完整的字节（0-255）的文件，每个字节出现一次，预期信息量应为 8"""
        path = self.test_file_path.format(5)
        full_byte_range = bytes(range(256))
        with open(path, 'wb') as f:
            f.write(full_byte_range)

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertAlmostEqual(entropy, 8.0, places=6)

    def test_TC06_whitespace_file(self):
        """TC06：创建只包含空格和换行的文件，预期信息量为 1"""
        path = self.test_file_path.format(6)
        with open(path, 'wb') as f:
            f.write(b' \n')

        entropy = main(path, self.output_csv_path, message_state=1)[0]
        self.assertAlmostEqual(entropy, 1.0, places=6)


if __name__ == '__main__':
    unittest.main()
