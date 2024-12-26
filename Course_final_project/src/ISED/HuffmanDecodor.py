import csv
import io
import os
import argparse

# Non-standard library
import numpy as np
from ..lib import dahuffman
from ..lib.dahuffman_no_EOF import HuffmanCodec

# 解码函数
def decode(in_file_name, out_file_name, byteorder = 'little'):
    # 字节序
    # 打开输入文件进行读取
    with open(in_file_name, 'rb') as in_file:
        in_file.seek(0, 2)
        if in_file.tell() == 0:
            open(out_file_name, 'wb').close()
            return 0, 0
        in_file.seek(0, 0)
        header_size = int.from_bytes(in_file.read(2), byteorder)  # 读取头部的大小
        header = io.BytesIO(in_file.read(header_size - 2))  # 读取头部数据（去掉前2字节）
        encoded = in_file.read()  # 读取编码后的数据

    # 解析码本信息
    codebook = {}
    symbol_count = header.read(1)[0]  # 读取符号计数
    source_len = int.from_bytes(header.read(4), byteorder)  # 读取源数据长度

    # 读取每个符号的编码信息并更新码本
    for k in range(symbol_count + 1):
        symbol = np.uint8(header.read(1)[0])  # 读取符号
        word_len = header.read(1)[0]  # 读取编码长度（单位：bit）
        word_bytes = int(np.ceil(word_len / 8))  # 计算编码字节长度
        word = int.from_bytes(header.read(word_bytes), byteorder)  # 读取编码字节并转换为整数
        codebook[symbol] = (word_len, word)  # 将符号和编码信息添加到码本中

    # 使用霍夫曼解码器进行解码
    codec = HuffmanCodec(codebook)
    decoded = np.asarray(codec.decode(encoded))[:source_len]  # 解码并截取源数据长度
    decoded.tofile(out_file_name)  # 将解码后的数据写入输出文件

    return (len(encoded), len(decoded))  # 返回编码数据的长度和解码后的数据长度
