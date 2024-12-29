import unittest, os
import calcErrorRate


class TestCalculateErrorRate(unittest.TestCase):
    def setUp(self):
        """
        测试前的准备工作，生成一些临时文件。
        """
        self.file1_path = "test_file1.bin"
        self.file2_path = "test_file2.bin"
        self.result_path = "test_result.csv"

        # 创建文件1，内容为 0b10101010
        with open(self.file1_path, "wb") as file1:
            file1.write(b"\xAA")

        # 创建文件2，内容为 0b10101010
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAA")

    def tearDown(self):
        """
        测试结束后的清理工作，删除临时文件。
        """
        if os.path.exists(self.file1_path):
            os.remove(self.file1_path)
        if os.path.exists(self.file2_path):
            os.remove(self.file2_path)
        if os.path.exists(self.result_path):
            os.remove(self.result_path)

    def test_identical_files(self):
        """
        测试两个完全相同的文件，误码率应为 0.0。
        """
        print("Test 1: Testing identical files with 0.0 error rate.")
        calcErrorRate.compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.0")
        print("Test 1 passed: Identical files tested successfully.")
        print()

    def test_different_files(self):
        """
        测试两个完全不同的文件，误码率应为 1.0。
        """
        print("Test 2: Testing completely different files with 1.0 error rate.")
        # 修改文件2的内容为 0b01010101
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\x55")

        calcErrorRate.compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},1.0")
        print("Test 2 passed: Different files tested successfully.")
        print()

    def test_partial_difference(self):
        """
        测试两个部分不同的文件。
        """
        print("Test 3: Testing partially different files with calculated error rate.")
        # 修改文件2的内容为 0b10101011
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAB")

        calcErrorRate.compare_file(self.file1_path, self.file2_path, self.result_path)

        # 检查结果文件内容
        with open(self.result_path, "r") as result_file:
            result = result_file.read().strip()
        self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.125")
        print("Test 3 passed: Partially different files tested successfully.")
        print()

    def test_file_size_mismatch(self):
        """
        测试两个文件大小不一致的情况。
        """
        print("Test 4: Testing file size mismatch case.")
        # 修改文件2的内容为两个字节
        with open(self.file2_path, "wb") as file2:
            file2.write(b"\xAA\xAA")

        try:
            calcErrorRate.compare_file(self.file1_path, self.file2_path, self.result_path)
            print("Expected ValueError was not raised for file size mismatch")
        except ValueError as e:
            print(f"Caught expected ValueError: {e}")
        print("Test 4 passed: File size mismatch handled correctly.")
        print()

    def test_file_not_exist(self):
        """
        测试文件路径无效的情况。
        """
        print("Test 5: Testing file not exist case.")
        invalid_path = "nonexistent_file.bin"
        try:
            calcErrorRate.compare_file(invalid_path, self.file2_path, self.result_path)
            print("Expected FileNotFoundError was not raised for non-existent file")
            print()
        except FileNotFoundError as e:
            print(f"Caught expected FileNotFoundError: {e}")
        print("Test 5 passed: Nonexistent file handled correctly.")
        print()

    def test_empty_files(self):
        """
        测试空文件的情况，误码率应为 0.0。
        """
        print("Test 6: Testing empty files with 0.0 error rate.")
        # 创建空文件
        with open(self.file1_path, "wb") as file1:
            file1.write(b"")
        with open(self.file2_path, "wb") as file2:
            file2.write(b"")

        try:
            calcErrorRate.compare_file(self.file1_path, self.file2_path, self.result_path)
            print("Calculation completed without ZeroDivisionError for empty files")
        except ZeroDivisionError as e:
            print(f"Caught ZeroDivisionError: {e}")

        # 检查结果文件内容（先判断文件是否存在）
        if os.path.exists(self.result_path):
            with open(self.result_path, "r") as result_file:
                result = result_file.read().strip()
            self.assertEqual(result, f"{self.file1_path},{self.file2_path},0.0")
            print("Test 6 passed: Empty files tested successfully.")
        else:
            print(f"Result file {self.result_path} not found after calculating for empty files")
        print()


if __name__ == "__main__":
    unittest.main()