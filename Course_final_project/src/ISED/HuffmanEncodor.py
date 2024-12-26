import csv
import io
import os
import argparse

# Non-standard library
import numpy as np
from ..lib import dahuffman
from ..lib.dahuffman_no_EOF import HuffmanCodec

# 编码函数
def encode(pmf_file_name, in_file_name, out_file_name, byteorder = 'little'):
    # 从输入文件读取源数据
    source = np.fromfile(in_file_name, dtype='uint8')  ## 读取输入文件，数据格式为uint8
    if len(source) == 0:
        open(out_file_name, 'wb').close()
        return 0, 0
    # 读取概率质量函数文件，构建符号的概率字典
    with open(pmf_file_name, newline='') as csv_file:
        # 读取符号和概率，形成字典
        pmf = {np.uint8(row[0]): float(row[1]) for row in csv.reader(csv_file)}
    # if not np.isclose(sum(pmf.values()), 0, 1e-5):
    #     raise ValueError("PMF must have summary close to 1, but got %.8f." % sum(pmf.values()))
    codec = HuffmanCodec.from_frequencies(pmf)  # 使用给定的频率表构建霍夫曼编码器

    encoded = codec.encode(source)  # 使用霍夫曼编码器对源数据进行编码

    # 获取霍夫曼编码器的码本
    codebook = codec.get_code_table()
    # 设置字节序（小端字节序）
    # 构建文件头部：头部包含码本信息
    header = bytearray(2)  # 头部初始化（2字节）
    header.append(len(codebook) - 1)  # 符号计数（符号个数减去1）
    header.extend(len(source).to_bytes(4, byteorder))  # 源数据长度（4字节表示）

    # 遍历码本，添加每个符号对应的编码信息到头部
    for symbol, (word_len, word) in codebook.items():
        word_bytes = int(np.ceil(word_len / 8))  # 计算编码的字节长度
        header.append(symbol)  # 添加符号
        header.append(word_len)  # 添加编码长度（单位：bit）
        header.extend(word.to_bytes(word_bytes, byteorder))  # 添加编码字节
    header[0:2] = len(header).to_bytes(2, byteorder)  # 更新头部的大小信息（前2字节为头部长度）

    # 打开输出文件并写入头部和编码后的数据
    with open(out_file_name, 'wb') as out_file:
        out_file.write(header)  # 写入头部
        out_file.write(encoded)  # 写入编码数据

    return (len(source), len(encoded))  # 返回源数据的长度和编码后的数据长度