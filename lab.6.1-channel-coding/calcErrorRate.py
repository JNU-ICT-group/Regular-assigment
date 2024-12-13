import sys
import os
import csv
###张朋洋12.12###
def calculate_error_rate(file1_path, file2_path, result_path):
    """
    计算两个文件之间的误码率，并将结果保存到 CSV 文件。
    
    file1_path: str, 输入文件 1 的路径
    file2_path: str, 输入文件 2 的路径
    result_path: str, 结果保存的 CSV 文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("文件路径错误，文件不存在")
        return

    # 打开并读取文件
    with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
        # 读取二进制内容
        data1 = file1.read()
        data2 = file2.read()

    # 文件大小不一致，无法比较
    if len(data1) != len(data2):
        print(f"文件大小不一致：{file1_path} 和 {file2_path} 的大小分别为 {len(data1)} 和 {len(data2)}")
        return

    # 计算错误位数
    error_bits = 0
    total_bits = len(data1) * 8  # 总比特数

    # 比较两个文件的每个字节
    for byte1, byte2 in zip(data1, data2):
        # 使用异或（XOR）计算不相同的位
        diff_bits = byte1 ^ byte2
        # 计算不相同的比特数量，使用位计数方法
        error_bits += bin(diff_bits).count('1')

    # 计算误码率
    error_rate = error_bits / total_bits

    # 保存结果到 CSV 文件
    with open(result_path, 'w', newline='') as result_file:
        writer = csv.writer(result_file)
        # 写入 CSV 内容
        writer.writerow([file1_path, file2_path, error_rate])

    print(f"误码率计算完成，结果已保存到 {result_path}")


if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) != 4:
        print("用法: python calcErrorRate.py INPUT1 INPUT2 RESULT")
        sys.exit(1)
    
    # 从命令行参数获取文件路径
    input1_path = sys.argv[1]
    input2_path = sys.argv[2]
    result_path = sys.argv[3]
    
    # 调用计算误码率函数
    calculate_error_rate(input1_path, input2_path, result_path)
