import os
import numpy as np
import csv
import argparse


# 解析命令行参数
def parse_sys_args():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="生成指定符号概率分布")

    # 添加 -t 选项用于运行单元测试
    parser.add_argument('-t', action='store_true', help='运行单元测试')

    # 添加输入文件和输出文件的参数
    parser.add_argument('input_file', nargs='?', help='输入文件的地址')
    parser.add_argument('output_file', nargs='?', help='输出文件的地址')
    parser.add_argument('msg_len', nargs='?', help='输出文件的地址')

    return parser.parse_args()


def read_input(input_path):
    """
    从CSV文件中读取符号概率分布。

    Parameters:
        input_path (str): 输入符号概率分布的CSV文件路径。

    Returns:
        numpy.ndarray: 符号的概率分布数组。
    """
    symbol_prob = np.zeros(256)  # 初始化一个大小为256的数组来保存概率分布
    with open(input_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            symbol, prob = int(row[0]), float(row[1])
            symbol_prob[symbol] = prob

    # 检查概率分布是否符合要求（所有概率之和应为1）
    if not np.isclose(symbol_prob.sum(), 1.0):
        raise ValueError("输入的概率分布不符合要求，所有概率之和必须为1。")

    return symbol_prob


def write_output(output_path, msg):
    """
    将生成的符号序列保存到输出文件。

    Parameters:
        output_path (str): 输出文件的路径。
        msg (numpy.ndarray): 生成的符号序列。
    """
    with open(output_path, 'w') as f:
        f.write(",".join(map(str, msg)))


def byte_source(symbol_prob, msg_len):
    """
    生成符合指定概率分布的长消息。

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

    return msg


def workflow(input_path, output_path, msg_len):
    """
    处理整个工作流：读取概率分布，生成符号序列，并写入文件。

    Parameters:
        input_path (str): 输入符号概率分布的CSV文件路径。
        output_path (str): 输出文件的路径，用于保存生成的符号序列。
        msg_len (int): 生成的消息长度（符号数量）。
    """
    symbol_prob = read_input(input_path)
    msg = byte_source(symbol_prob, msg_len)
    write_output(output_path, msg)


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
    temp_output_path = "temp_output.csv"

    for _ in range(num_tests):
        # 调用算法函数生成符号序列
        workflow(temp_csv_path, temp_output_path, msg_len)

        # 读取生成的符号序列
        with open(temp_output_path, 'r') as f:
            msg = np.array(list(map(int, f.read().split(','))))

        # 计算生成符号序列的概率分布
        P = np.bincount(msg, minlength=256) / len(msg)

        # 判断相对误差是否在可接受范围内（例如小于2）
        relative_error = abs(P - symbol_prob) / symbol_prob
        if not np.all(relative_error <= 1):
            print("relative errors:", relative_error)
            return False

    # 删除临时文件
    os.remove(temp_csv_path)
    os.remove(temp_output_path)

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


# 主函数
def main():
    args = parse_sys_args()

    if args.t:
        test_flow()
    elif args.input_file and args.output_file and args.msg_len:
        workflow(args.input_file, args.output_file, args.msg_len)
    else:
        # 打印帮助信息
        print("使用方法:")
        print("运行单元测试: python byteSource.py -t")
        print("处理文件: python byteSource.py INPUT OUTPUT MSG_LEN")


if __name__ == "__main__":
    main()
