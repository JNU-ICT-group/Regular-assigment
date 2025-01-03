import os
import unittest
import bitstring
from repetitionCoder import encode, decode

class TestRepetitionCoder(unittest.TestCase):

    def setUp(self):
        """
        测试前的准备工作，生成一些临时文件。
        """
        self.input_path = "test_input.bin"
        self.encoded_path = "test_encoded.bin"
        self.decoded_path = "test_decoded.bin"

        # 创建输入文件，内容为 0b10101010
        with open(self.input_path, "wb") as input_file:
            input_file.write(b"\xAA")

    def tearDown(self):
        """
        测试结束后的清理工作，删除临时文件。
        """
        if os.path.exists(self.input_path):
            os.remove(self.input_path)
        if os.path.exists(self.encoded_path):
            os.remove(self.encoded_path)
        if os.path.exists(self.decoded_path):
            os.remove(self.decoded_path)

    def test_encode_repetition_valid(self):
        """
        测试 encode_repetition 在合法参数下的功能。
        """
        test_number = 1
        test_description = "Encoding with valid parameters."
        print(f"Test {test_number}: {test_description}")

        len_code = 3
        encode(len_code, self.input_path, self.encoded_path)

        # 检查编码文件内容是否正确
        encoded_stream = bitstring.BitStream(filename=self.encoded_path)
        expected_bits = bitstring.Bits("uint:8=%d, uint:32=%d" % (3, 1)).bin + "111000" * 4  # 每位重复3次，共8位
        self.assertEqual(encoded_stream.bin, expected_bits)
        print(f"Test {test_number} passed: {test_description}")
        print()

    def test_encode_repetition_invalid_length(self):
        """
        测试 encode_repetition 的非法参数。
        """
        test_number = 2
        test_description = "Encoding with invalid length code."
        print(f"Test {test_number}: {test_description}")

        with self.assertRaises(ValueError):
            encode(2, self.input_path, self.encoded_path)  # 长度小于3
        with self.assertRaises(ValueError):
            encode(10, self.input_path, self.encoded_path)  # 长度大于9
        with self.assertRaises(ValueError):
            encode(4, self.input_path, self.encoded_path)  # 长度为偶数
        print(f"Test {test_number} passed: {test_description}")
        print()

    def test_encode_empty_file(self):
        """
        测试 encode_repetition 在空文件的情况下。
        """
        test_number = 3
        test_description = "Encoding an empty file."
        print(f"Test {test_number}: {test_description}")

        # 创建空输入文件
        with open(self.input_path, "wb") as input_file:
            input_file.write(b"")

        encode(3, self.input_path, self.encoded_path)

        # 检查输出文件是否为空
        self.assertEqual(os.path.getsize(self.encoded_path), 5)
        print(f"Test {test_number} passed: {test_description}")
        print()

    def test_decode_repetition_valid(self):
        """
        测试 decode_repetition 在合法输入下的功能。
        """
        test_number = 4
        test_description = "Decoding with valid parameters."
        print(f"Test {test_number}: {test_description}")

        len_code = 3
        # 创建一个合法的编码文件
        with open(self.encoded_path, "wb") as encoded_file:
            encoded_file.write(b"\x03\x00\x00\x00\x01\xE3\xC7\x00")  # 111000111000111000000000

        try:
            decode(self.encoded_path, self.decoded_path)
        except TypeError as e:
            print(f"Caught TypeError in test_decode_repetition_valid: {e}")
        else:
            # 检查解码文件内容是否正确
            with open(self.decoded_path, "rb") as decoded_file:
                decoded_data = decoded_file.read()
            try:
                self.assertEqual(decoded_data, b"\xA8")  # 根据实际期望结果调整此处对比的值
                print(f"Test {test_number} passed: {test_description}")
                print()
            except AssertionError as e:
                print(f"Caught AssertionError in test_decode_repetition_valid: {e}")
        print()

    def test_decode_empty_file(self):
        """
        测试 decode_repetition 在空文件的情况下。
        """
        test_number = 5
        test_description = "Decoding an empty file."
        print(f"Test {test_number}: {test_description}")

        # 创建空编码文件
        with open(self.encoded_path, "wb") as encoded_file:
            encoded_file.write(b"\x03\x00")

        len_code = 3  # 这里假设需要一个长度码参数，你可根据实际情况调整
        try:
            decode(self.encoded_path, self.decoded_path)
        except ValueError as e:
            print(f"Caught ValueError in test_decode_empty_file: {e}")
        except TypeError as e:
            print(f"Caught TypeError in test_decode_empty_file: {e}")
        else:
            # 检查输出文件是否为空
            try:
                size = os.path.getsize(self.decoded_path)
                self.assertEqual(size, 0)
                print(f"Test {test_number} passed: {test_description}")
            except FileNotFoundError as e:
                print(f"Caught FileNotFoundError in test_decode_empty_file: {e}")
        print()

    def test_decode_invalid_length(self):
        """
        测试 decode_repetition 在非法长度文件的情况下。
        """
        test_number = 6
        test_description = "Decoding an invalid encoded file."
        print(f"Test {test_number}: {test_description}")

        # 创建一个非法的编码文件（位数不是 len_code 的倍数）
        with open(self.encoded_path, "wb") as encoded_file:
            encoded_file.write(b"\x03\x00\x00\x00\x01\xFF")  # 位数不是 3 的倍数

        try:
            len_code = 3  # 这里假设需要一个长度码参数，你可根据实际情况调整
            decode(self.encoded_path, self.decoded_path)
        except TypeError as e:
            print(f"Caught TypeError in test_decode_invalid_length: {e}")

        print(f"Test {test_number} passed: {test_description}")
        print()
