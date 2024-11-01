import numpy as np
import csv

def calculate_cumulative_distribution(symbol_prob):
    """
    计算累积概率分布并生成符号序列。

    Parameters:
        symbol_prob (ndarray): 符号概率分布数组。

    Returns:
        symbol_cumsum (ndarray): 累积概率分布数组。
    """
    return symbol_prob.cumsum()

def generate_symbols(symbol_cumsum, msg_len):
    """
    生成符合给定累积概率分布的符号序列。

    Parameters:
        symbol_cumsum (ndarray): 累积概率分布数组。
        msg_len (int): 生成的消息长度（符号数量）。

    Returns:
        msg (ndarray): 生成的符号序列。
    """
    symbol_random = np.random.uniform(size=msg_len)
    return np.searchsorted(symbol_cumsum, symbol_random)

