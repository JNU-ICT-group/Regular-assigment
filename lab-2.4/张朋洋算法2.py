import numpy as np
import csv

def byte_source(input_path, output_path, msg_len):
    """
    模拟256元离散无记忆信源，生成符合指定概率分布的长消息并输出到文件中。

    Parameters:
        input_path (str): 输入符号概率分布的CSV文件路径。
        output_path (str): 输出文件的路径，用于保存生成的符号序列。
        msg_len (int): 生成的消息长度（符号数量）。
    """

    # Step 1: 从CSV文件中读取符号概率分布
    symbol_prob = np.zeros(256)  # 初始化一个大小为256的数组来保存概率分布
    with open(input_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            symbol, prob = int(row[0]), float(row[1])
            symbol_prob[symbol] = prob
    
    # 检查概率分布是否符合要求（所有概率之和应为1）
    if not np.isclose(symbol_prob.sum(), 1.0):
        raise ValueError("输入的概率分布不符合要求，所有概率之和必须为1。")

    # Step 2: 计算累积概率分布 F(i)
    symbol_cumsum = symbol_prob.cumsum()

    # Step 3: 生成符合均匀分布的随机数，并通过累积概率分布查找对应符号
    symbol_random = np.random.uniform(size=msg_len)
    msg = np.searchsorted(symbol_cumsum, symbol_random)

    # Step 4: 将生成的符号序列保存到输出文件
    with open(output_path, 'w') as f:
        f.write(",".join(map(str, msg)))

# 示例使用
input_path = "input_prob.csv"  # 输入的CSV文件路径
output_path = "output_message.txt"  # 输出的符号序列文件路径
msg_len = 102400  # 生成的符号数量

# 调用函数生成符号序列
byte_source(input_path, output_path, msg_len)
