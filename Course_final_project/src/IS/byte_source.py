import numpy as np

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