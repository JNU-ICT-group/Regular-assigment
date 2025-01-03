import byteSource
import calcDMSInfo
import os, csv
import numpy as np



def quick_test(symbol_prob, p0, hx, redund, msg_len=100000, num_tests=2):
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
    temp_info_path = "temp_info_stat.csv"
    # 生成临时输出文件路径
    temp_output_path = "temp_output.bin"
    temp_prob_path = "temp_prob_stat.csv"
    # 删除临时文件
    if os.path.exists(temp_info_path):
        os.remove(temp_info_path)

    for _ in range(num_tests):
        # 调用算法函数生成符号序列
        byteSource.work_flow(symbol_prob, temp_output_path, msg_len, message_state=0)

        arr, x_size = calcDMSInfo.read_input(temp_output_path)
        assert msg_len == x_size, 'Except to %d but %s' % (msg_len,x_size)
        for i,p in enumerate(symbol_prob):
            P = (arr == i).sum(dtype=np.uint32) / x_size
            if abs(P - p) > 1e-2:
                print("Error probability: except %.6f, but %.6f at symbol %d" % (p, P, i))
                return False

        # 指标计算测试
        calcDMSInfo.main(temp_output_path, temp_info_path, export_p=temp_prob_path, message_state=0)
        with open(temp_prob_path) as f:
            p = np.zeros_like(symbol_prob)
            for row in csv.reader(f):
                p[int(row[0])] = float(row[1])
        relative_error = np.abs(symbol_prob - p)
        if not (relative_error <= 0.02).all():
            print("relative errors:", relative_error)
            return False
        with open(temp_info_path) as f:
            for (X,P0,HX,redundancy,msg_length) in csv.reader(f):
                pass
            assert X == temp_output_path, 'Except to %s but %s' % (temp_output_path,X)
            assert abs(p0 - float(P0)) < 1e-2, 'Except to %.4f but %s' % (p0,P0)
            assert abs(hx - float(HX)) < 1e-2, 'Except to %.4f but %s' % (hx,HX)
            assert abs(redund - float(redundancy)) < 1e-2, 'Except to %.3f but %s' % (redund,redundancy)
            assert msg_len == int(msg_length), 'Except to %d but %s' % (msg_len,msg_length)


    # 删除临时文件
    os.remove(temp_output_path)
    os.remove(temp_prob_path)
    os.remove(temp_info_path)
    return True


def test_flow():
    all_tests_passed = True

    # 只有一个符号概率为1，其余为0
    single_symbol_dist = np.zeros(256)
    single_symbol_dist[0] = single_symbol_dist[-1] = 0.5
    print("Testing single symbol distribution:")
    if quick_test(single_symbol_dist, 0.5, 1., 0.):
        print("Single symbol distribution test passed.")
    else:
        all_tests_passed = False
        print("Single symbol distribution test passed (nan).")

    # 均匀分布
    uniform_dist = np.full(256, 1 / 256)
    print("Testing uniform distribution:")
    if quick_test(uniform_dist, 0.5, 1., 0.):
        print("Uniform distribution test passed.")
    else:
        all_tests_passed = False
        print("Uniform distribution test failed.")

    # 不同长度的消息
    print("Testing different message lengths:")
    for length in [10000, 100000]:
        print(f"Testing length {length}:")
        if quick_test(uniform_dist, 0.5,1,0, msg_len=length):
            print(f"Length {length} test passed.")
        else:
            all_tests_passed = False
            print(f"Length {length} test failed.")

    # 不同随机种子的影响
    print("Testing different random seeds:")
    for seed in [1, 2, 3]:
        np.random.seed(seed)
        print(f"Testing seed {seed}:")
        if quick_test(uniform_dist, 0.5,1,0):
            print(f"Seed {seed} test passed.")
        else:
            all_tests_passed = False
            print(f"Seed {seed} test failed.")

    # 检查是否所有测试都通过
    if all_tests_passed:
        print("all pass")


if __name__ == '__main__':
    test_flow()
