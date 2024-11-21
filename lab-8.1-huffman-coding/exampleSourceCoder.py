""" A basic source coder.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |header_size  : uint16, number of bytes for header
        |symbol_count : uint8, (number of symbols in codebook)-1
  ______|source_len   : uint32, number of symbols in source
  Code-1|symbol       : uint8, symbol
        |word_len     : uint8, number of bits for codeword
  ______|word         : ceil(word_len/8)*uint8, codeword
    ....|...
  ______|
  Code-n|symbol
        |word_len
________|word
Payload |encoded-data : many unit8

Note: This program is intended for use in course, Principle of Information and Coding Theory.

"""

import csv
import io

# Non-standard library
import numpy as np
from dahuffman_no_EOF import HuffmanCodec   #导入霍夫曼编码库

__author__ = "Guo, Jiangling"
__email__ = "tguojiangling@jnu.edu.cn"
__version__ = "20201111.1702"

#编码函数
def encode(pmf_file_name, in_file_name, out_file_name):
    #读取概率质量函数文件，构建符号的概率字典
    with open(pmf_file_name, newline='') as csv_file:
        #读取符号和概率，形成字典
        pmf = dict([(np.uint8(row[0]), float(row[1])) for row in csv.reader(csv_file)])
    codec = HuffmanCodec.from_frequencies(pmf)  # 使用给定的频率表构建霍夫曼编码器

    # 从输入文件读取源数据
    source = np.fromfile(in_file_name, dtype='uint8')   ## 读取输入文件，数据格式为uint8
    encoded = codec.encode(source)  # 使用霍夫曼编码器对源数据进行编码

    # 获取霍夫曼编码器的码本
    codebook = codec.get_code_table()
    byteorder = 'little'    # 设置字节序（小端字节序）
    # 构建文件头部：头部包含码本信息
    header = bytearray(2)   # 头部初始化（2字节）
    header.append(len(codebook)-1)  # 符号计数（符号个数减去1）
    header.extend(len(source).to_bytes(4, byteorder))   # 源数据长度（4字节表示）
    
    # 遍历码本，添加每个符号对应的编码信息到头部
    for symbol, (word_len, word) in codebook.items():
        (word_len, word) = codebook[symbol]
        word_bytes = int(np.ceil(word_len / 8)) # 计算编码的字节长度
        header.append(symbol)   # 添加符号
        header.append(word_len) # 添加编码长度（单位：bit）
        header.extend(word.to_bytes(word_bytes, byteorder)) # 添加编码字节
    header[0:2] = len(header).to_bytes(2, byteorder)    # 更新头部的大小信息（前2字节为头部长度）

    # 打开输出文件并写入头部和编码后的数据
    with open(out_file_name, 'wb') as out_file:
        out_file.write(header)  # 写入头部
        out_file.write(encoded) # 写入编码数据
    
    return (len(source), len(encoded))   # 返回源数据的长度和编码后的数据长度
#解码函数
def decode(in_file_name, out_file_name):

    byteorder = 'little'    # 字节序
    # 打开输入文件进行读取
    with open(in_file_name, 'rb') as in_file:
        header_size = int.from_bytes(in_file.read(2), byteorder)    # 读取头部的大小
        header = io.BytesIO(in_file.read(header_size-2))    # 读取头部数据（去掉前2字节）
        encoded = in_file.read()    # 读取编码后的数据
    
    # 解析码本信息
    codebook = {}
    symbol_count = header.read(1)[0]    # 读取符号计数
    source_len = int.from_bytes(header.read(4), byteorder)  # 读取源数据长度
    
    # 读取每个符号的编码信息并更新码本
    for k in range(symbol_count+1):
        symbol = np.uint8(header.read(1)[0])    # 读取符号
        word_len = header.read(1)[0]    # 读取编码长度（单位：bit）
        word_bytes = int(np.ceil(word_len / 8)) # 计算编码字节长度
        word = int.from_bytes(header.read(word_bytes), byteorder)   # 读取编码字节并转换为整数
        codebook[symbol] = (word_len, word) # 将符号和编码信息添加到码本中
    
    # 使用霍夫曼解码器进行解码
    codec = HuffmanCodec(codebook)
    decoded = np.asarray(codec.decode(encoded))[:source_len]    # 解码并截取源数据长度
    decoded.tofile(out_file_name)   # 将解码后的数据写入输出文件

    return (len(encoded), len(decoded)) # 返回编码数据的长度和解码后的数据长度

# 文件比较函数，比较两个文件的差异
def compare_file(file_name_1, file_name_2):
    """Compare two files and count number of different bytes."""
    data1 = np.fromfile(file_name_1, dtype='uint8') # 读取第一个文件的数据
    data2 = np.fromfile(file_name_2, dtype='uint8') # 读取第二个文件的数据

    compare_size = min(data1.size, data2.size)  # 取较小的文件大小作为比较大小
    if data1.size != data2.size:    # 如果文件大小不同，输出警告
        print('[WARNING] These two files have different sizes (in bytes): %d vs %d' % (data1.size, data2.size))
        print('          Comparing the first %d bytes only.' % (compare_size))

    # 比较两个文件的数据，统计不同的字节数
    diff_total = np.sum(data1[:compare_size] != data2[:compare_size])   # 统计不同字节的总数
    print('Total %d bytes are different.' % (diff_total))

    return diff_total

# 测试函数
def test():
    test_data_dir = 'test-data/'    # 测试数据目录
    pmf_file_name = test_data_dir + 'pmf.byte.p0=0.8.csv'   # 概率质量函数文件
    source_file_name = test_data_dir + 'source.p0=0.8.len=64KB.dat' # 源文件
    encoded_file_name = test_data_dir + '_encoded.tmp'  # 编码后文件
    decoded_file_name = test_data_dir + '_decoded.tmp'  # 解码后文件

    print('Encoding...')
    (source_len, encoded_len) = encode(pmf_file_name, source_file_name, encoded_file_name)
    print(' source len:', source_len)   # 打印源数据长度
    print('encoded len:', encoded_len)  # 打印编码后的数据长度
    print('     ratio :', source_len/encoded_len)   # 打印压缩比
    print('')

    print('Decoding...')
    (encoded_len, decoded_len) = decode(encoded_file_name, decoded_file_name)   # 执行解码
    print('encoded len:', encoded_len)  # 打印编码数据长度
    print('decoded len:', decoded_len)  # 打印解码数据长度
    print('')

    print('Comparing source and decoded...')
    compare_file(source_file_name, decoded_file_name)   # 比较源文件和解码后的文件
    print('')

#主程序入口
if __name__ == '__main__':
    test()  # 执行测试
