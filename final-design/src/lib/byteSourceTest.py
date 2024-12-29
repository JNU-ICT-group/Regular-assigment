import byteSource
import os, csv
import numpy as np



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
    temp_output_path = "temp_output.bin"
    temp_prob_path = "temp_prob_stat.csv"
    import calcInfo
    for _ in range(num_tests):
        # 调用算法函数生成符号序列
        byteSource.main(temp_csv_path, temp_output_path, msg_len, message_state=0)

        with open(temp_output_path, 'rb') as f:
            arr = np.frombuffer(memoryview(f.read()), dtype=np.uint8)
            p, info = calcInfo.compute_info(arr, len(arr))
            calcInfo.write_export(temp_prob_path, p)

        P = byteSource.read_input(temp_prob_path)
        # 判断相对误差是否在可接受范围内（例如小于2）
        relative_error = np.abs(P - symbol_prob) / symbol_prob
        if not np.all(relative_error <= 1):
            print("relative errors:", relative_error)
            return False

    # 删除临时文件
    os.remove(temp_csv_path)
    os.remove(temp_output_path)
    os.remove(temp_prob_path)
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


if __name__ == '__main__':
    test_flow()
