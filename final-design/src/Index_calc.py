import os
import csv
import numpy as np
from pathlib import Path
import calcDMSInfo
import calcBSCInfo
import bytesourceCoder
import repetitionCoder

"""
zhangpengyang
2025.01.03
"""

##############################################################################
#   工具函数
# （几乎都是调用别的地方的函数，为了便于理解，我先copy过来）
##############################################################################

def read_file_as_bytes(in_file_name):
    """Read a file as bytes and return a uint8 array."""
    return np.fromfile(in_file_name, dtype='uint8')

def calc_probability(data) -> np.ndarray:
    """计算每个字节的近似概率"""
    file_size = len(data)
    byte_counts = np.histogram(data, bins=range(257))[0]
    probability = np.divide(byte_counts, file_size, dtype=np.float32)
    return probability

def write_export(out_file_name, x):
    with open(out_file_name, 'w', newline='', encoding='utf-8') as out_file:
        write = csv.writer(out_file, quoting=csv.QUOTE_NONE)
        write.writerows([int(i), '%.8f' % p] for i, p in enumerate(x) if p)

def calc_prob0(prob) -> float:
    bit_counts = np.uint8(bytearray(map(int.bit_count, range(256))))
    return 1. - (prob * bit_counts).sum() / 8

def calc_information(p: np.ndarray) -> np.ndarray:
    """计算每个字节的信息量（单位：比特）"""
    p = p.copy()
    np.clip(p, np.spacing(1), None, out=p)
    information = - np.log2(p, out=p)
    return information

def calc_entropy(p: np.ndarray) -> float:
    """计算信息熵，即平均每个字节的信息量"""
    entropy = (p * calc_information(p)).sum()
    return entropy

def calc_redundancy(p0: float) -> float:
    """计算二元DMS的冗余度"""
    return 1. - calc_entropy(np.float32([p0, 1-p0]))

def calc_entropy_256(prob_256: np.ndarray) -> float:
    """
    计算 256 元离散变量的熵(单位: bit/字节)。
    """
    p_copy = np.clip(prob_256, 1e-15, None)
    H = - np.sum(p_copy * np.log2(p_copy))
    return float(H)

def mutual_information(HX: float, HY: float, HXY: float) -> float:
    """
    互信息 I(X;Y) = H(X) + H(Y) - H(X,Y).
    这里若要按 bit/二元消息，需要在调用方把 HX, HY, HXY 调整到相同单位再传进来。
    """
    return HX + HY - HXY

def calc_compress_ratio(size0, size1) -> float:
    return size0 / size1

def calc_code_avlen(size0, size1) -> float:
    return 8 * size1 / size0

def calc_efficiency(ratio: float) -> float:
    return (1. - 1/ratio) * 100

def calc_huffman_encoded_entropy(encoded_file):
    """计算Huffman编码后文件的信息熵
    Args:
        encoded_file: 编码后的文件路径
    Returns:
        float: 信息熵(bits/byte)
    """
    # 读取编码后的文件，跳过header
    with open(encoded_file, 'rb') as f:
        header_size = int.from_bytes(f.read(2), 'little')
        f.seek(header_size)  # 跳过header
        encoded_data = np.fromfile(f, dtype='uint8')
    
    # 计算概率分布
    prob = calc_probability(encoded_data)
    
    # 计算信息熵
    entropy = calc_entropy(prob)
    
    return entropy

##############################################################################
# 2.1.2. 信源指标计算模块
##############################################################################

def calc_dms_info(source_file: str,
                  dms_info_csv: str,
                  export_256_csv: str = None):
    """
    输入:
      - source_file: 信源输出消息序列文件 (uint8字节序列)
    输出:
      - 字节概率分布文件（CSV格式），即256元DMS的概率分布统计 -> export_256_csv
      - 在 dms_info_csv 追加/写入一行:
            1数据比特概率分布（即二元DMS的概率分布统计） 
            2二元DMS的信息熵（信息比特/二元消息）
            3二元DMS的冗余度
            (计算公式详见文档，我这里注释就不再说了)
    """
    data = read_file_as_bytes(source_file)
    length_in_bytes = len(data)

    # 计算 256元概率分布
    prob_256 = calc_probability(data)
    # 导出 256 元分布 (可选)
    if export_256_csv:
        write_export(prob_256, export_256_csv)

    # 计算二元信息熵 (bit/二元消息)
    p0 = calc_prob0(prob_256)

    #二元DMS的冗余度
    H_b = calc_redundancy(p0)

    # 将结果写入 dms_info_csv
    need_header = not os.path.isfile(dms_info_csv)
    with open(dms_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:#(设计要求文档中没有要求这个小表头，就当作一个小小的优化，其实不用也行)
            writer.writerow(["source_file", "P(0)->P(255)", "H(bit/二元msg)", "redundancy", "length(bytes)"])
        row = [
            source_file,
            f"{p0:.6f}",
            f"{H_b:.6f}",
            f"{R:.6f}",
            f"{length_in_bytes}"
        ]
        writer.writerow(row)

##############################################################################
# 2.2.2. 信道指标计算模块
##############################################################################

def calc_channel_info(channel_in_file: str,
                      channel_out_file: str,
                      channel_info_csv: str):
    """
    输入:
      - channel_in_file: 信道输入消息序列
      - channel_out_file: 信道输出消息序列
    输出:
        包含以下指标数值的文件（CSV格式）
            1输入消息序列的信息熵（信息比特/二元消息）
            2输出消息序列的信息熵（信息比特/二元消息）
            3平均互信息量（信息比特/二元消息）
        （小表头：[in_file, out_file, H_in(bit/二元), H_out(bit/二元), I(bit/二元), length_in(bytes), length_out(bytes)]）
    """

    data_in = read_file_as_bytes(channel_in_file)
    data_out = read_file_as_bytes(channel_out_file)
    len_in = len(data_in)
    len_out = len(data_out)

#输入消息序列的信息熵(H(X))
    prob_in_256 = calc_probability(data_in)  # 计算256元分布
    H_in = calc_entropy_256(prob_in_256)     # 计算信道输入的信息熵(bit/字节)
    # 转换单位: 从bit/字节转为bit/二元消息
    H_in_bit = H_in / 8  # 每个字节8个二元消息,所以除以8

    p=0.01
#输出消息序列的信息熵
    if p == 0:
        #理想信道
        prob_out_256 = calc_probability(data_out)  # 计算256元分布 
        H_out = calc_entropy_256(prob_out_256)     # 计算信道输出的信息熵(bit/字节)
        # 转换单位: 从bit/字节转为bit/二元消息 
        H_out_bit = H_out / 8  # 每个字节8个二元消息,所以除以8
    else:
        #非理想信道
        #需要先确定先验概率分布

        
        #这个错误概率传递方法待定，所以这部分先注释掉


        # # 计算输入概率分布
        # prob_in_256 = calc_probability(data_in)
        
        # # 计算联合分布矩阵 P(X,Y)
        # joint_p_xy = calc_joint_distribution_matrix(prob_in_256, p)
        
        # # 计算输出边缘分布 P(Y)
        # prob_out_256 = calc_p_y(joint_p_xy)
        
        # # 计算输出熵 H(Y)
        # H_out = calc_entropy_256(prob_out_256)  # bit/字节
        
        # # 转换为bit/二元消息
        H_out_bit = H_out / 8


#平均互信息量（公式我就不写了）
    X = data_in
    Y = data_out
    H_XY = calcBSCInfo.calc_joint_H_xy(X, Y)
    I_XY = calcBSCInfo.H_X + calcBSCInfo.H_Y - H_XY


    # 在 channel_info_csv 追加输出
    need_header = not os.path.isfile(channel_info_csv)
    with open(channel_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([
                "channel_in_file", 
                "channel_out_file",
                "H_in(bit/二元)", 
                "H_out(bit/二元)", 
                "I(bit/二元)(approx)", 
                "length_in(bytes)", 
                "length_out(bytes)"
            ])
        row = [
            channel_in_file,
            channel_out_file,
            f"{H_in_bit:.6f}",
            f"{H_out_bit:.6f}",
            f"{I_XY:.6f}",
            f"{len_in}",
            f"{len_out}"
        ]
        writer.writerow(row)

##############################################################################
# 2.3.3. 信源编码指标计算模块
##############################################################################

def calc_source_codec_info(before_file: str,
                           after_file: str,
                           pmf_file_name,
                           source_codec_info_csv: str):
    """
    输入:
      - before_file: 编码前文件(原始)
      - after_file: 编码后文件
    输出:
    包含以下指标数值的文件（CSV格式）
        压缩比（编码前文件字节数/编码后文件字节数）=size0/(size1-header)
        平均码长（码字数据比特/信源字节）
        编码效率
        编码前的文件的信息熵（信息比特/字节）
        编码后的文件的信息熵（信息比特/字节）
            
      - 在 source_codec_info_csv 写一行:
         [
           before_file, after_file, compression_ratio,
           avg_codelen(bit/原字节), codec_efficiency,
           H_before(bit/字节), H_after(bit/字节),
           length_before, length_after
         ]
    """

    data_before = read_file_as_bytes(before_file)
    data_after  = read_file_as_bytes(after_file)

    len_b = len(data_before)
    len_a = len(data_after)

#压缩比（编码前文件字节数/编码后文件字节数）
    ratio = calc_compress_ratio(data_before, data_after)

#平均码长（码字数据比特/信源字节）
    avlen = calc_code_avlen(data_before, data_after)

#编码效率
    efficiency = calc_efficiency(ratio)

#编码前的文件的信息熵（信息比特/字节）
    calc_entropy(data_before)  # bit/字节
    # 去除0概率避免log2(0)
    p = p[p > 0]
    entropy3 = calc_entropy(p)

#编码后的文件的信息熵（信息比特/字节）
    after_file = bytesourceCoder.encode(pmf_file_name, in_file_name, out_file_name, byteorder = 'little')
    #huoffman编码后的文件的信息熵
    encoded_entropy = calc_huffman_encoded_entropy(after_file)


    # 写入结果 CSV
    need_header = not os.path.isfile(source_codec_info_csv)
    with open(source_codec_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([
                "before_file", "after_file",
                "compression_ratio",
                "avg_code_len(bit/origin_byte)",
                "codec_efficiency",
                "H_before(bit/byte)",
                "H_after(bit/byte)",
                "length_before(bytes)",
                "length_after(bytes)"
            ])
        row = [
            before_file,
            after_file,
            f"{ratio:.6f}",
            f"{avlen:.6f}",
            f"{efficiency:.6f}",
            f"{entropy3:.6f}",
            f"{encoded_entropy:.6f}",
            f"{len_b}",
            f"{len_a}"
        ]
        writer.writerow(row)

##############################################################################
# 2.4.3. 信道编解码指标计算模块
##############################################################################

def calc_channel_codec_info(before_file: str,
                            coded_file: str,
                            decoded_file: str,
                            channel_codec_info_csv: str):
    """
    输入:
      - before_file: 编码前的文件
      - coded_file: 编码后的文件
      - decoded_file: 解码后的文件
    输出:
    包含以下指标数值的文件（CSV格式）
        压缩比（编码前文件字节数/编码后文件字节数）
        误码率（汉明失真，错误数据比特/总数据比特）
        编码前的信源信息传输率（信息比特/字节）
        编码后的信源信息传输率（信息比特/字节）

      - 在 channel_codec_info_csv 写一行:
         [
           before_file, coded_file, decoded_file,
           compression_ratio, bit_error_rate,
           source_rate_before(bit/byte), source_rate_after(bit/byte),
           length_before, length_coded, length_decoded
         ]
    """
    data_before  = read_file_as_bytes(before_file)
    data_coded   = read_file_as_bytes(coded_file)
    data_decoded = read_file_as_bytes(decoded_file)

    len_b = len(data_before)
    len_c = len(data_coded)
    len_d = len(data_decoded)

#压缩比（编码前文件字节数/编码后文件字节数）
    compression_ratio = len(data_before) / len(data_coded) if len(data_coded) > 0 else 0

#误码率（汉明失真，错误数据比特/总数据比特）
    # 计算汉明误码率，使用较短的长度
    compare_size = min(len(data_before), len(data_decoded))
    diff_total = np.unpackbits(data_before[:compare_size] ^ data_decoded[:compare_size]).sum()
    bit_error_rate = diff_total / (compare_size * 8)

#编码前的信源信息传输率（信息比特/字节）
    # 计算编码前信源信息传输率（信息比特/字节）
    source_entropy = calc_entropy(calc_probability(data_before))     # 比特/字节
    source_rate_before = source_entropy                             # 定长

#编码后的信源信息传输率（信息比特/字节）
    # 计算编码后信源信息传输率（信息比特/字节）
    coded_entropy = calc_entropy(calc_probability(data_coded))      # 比特/字节
    source_rate_after = coded_entropy / len(data_coded) * len(data_before)  # 调整后的传输率


    # 写入 CSV
    need_header = not os.path.isfile(channel_codec_info_csv)
    with open(channel_codec_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([
                "before_file", "coded_file", "decoded_file",
                "compression_ratio",
                "bit_error_rate",
                "source_rate_before(bit/byte)",
                "source_rate_after(bit/byte)",
                "length_before", "length_coded", "length_decoded"
            ])
        row = [
            before_file,
            coded_file,
            decoded_file,
            f"{compression_ratio:.6f}",
            f"{bit_error_rate:.6f}",
            f"{source_rate_before:.6f}",
            f"{source_rate_after:.6f}",
            f"{len_b}",
            f"{len_c}",
            f"{len_d}"
        ]
        writer.writerow(row)

##############################################################################
#  main(): 调用这些函数
##############################################################################

def main():
    
    """
    在同一个脚本里调用这四大功能。
    自定义命令行参数或直接在这里写死路径来测试。
    """

    os.makedirs(data_dir, exist_ok=True)
    # 获取当前脚本路径
    current_path = Path(__file__).parent
    # 获取上级目录中的 data 目录
    data_dir = current_path.parent / 'data'
    # 确保目录存在
    data_dir.mkdir(exist_ok=True)

    # 假设有如下文件:
    source_file        = os.path.join(data_dir, "DMS.p0=0.1.dat")
    channel_in_file    = os.path.join(data_dir, "RC.en.p0=0.1.dat")
    channel_out_file   = os.path.join(data_dir, "BSC.p0=0.1.p=0.01.dat")
    source_codec_file  = os.path.join(data_dir, "HC.en.p0=0.1.dat")
    channel_decode_file= os.path.join(data_dir, "RC.de.p0=0.1.p=0.01.dat")

    # (1) 2.1.2. 信源指标: dms_info.csv
    dms_info_csv = os.path.join(data_dir, "DMS.info.csv")
    dms_256_csv  = os.path.join(data_dir, "DMS.256dist.csv")
    calc_dms_info(source_file, dms_info_csv, dms_256_csv)

    # (2) 2.2.2. 信道指标: BSC.info.csv
    channel_info_csv = os.path.join(data_dir, "BSC.info.csv")
    calc_channel_info(channel_in_file, channel_out_file, channel_info_csv)

    # (3) 2.3.3. 信源编码指标: HC.info.csv
    source_codec_info_csv = os.path.join(data_dir, "HC.info.csv")
    calc_source_codec_info(source_file, source_codec_file, source_codec_info_csv)

    # (4) 2.4.3. 信道编解码指标: RC.info.csv
    channel_codec_info_csv = os.path.join(data_dir, "RC.info.csv")
    calc_channel_codec_info(source_file, channel_in_file, channel_decode_file, channel_codec_info_csv)

    print("[INFO] All done. Check the CSV outputs in:", data_dir)

if __name__ == "__main__":
    main()
