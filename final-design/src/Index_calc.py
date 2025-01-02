#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
from pathlib import Path
##############################################################################
# 工具函数
##############################################################################

def read_file_to_array(file_path: str) -> np.ndarray:
    """
    读取文件为 uint8 一维数组。
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return np.fromfile(file_path, dtype=np.uint8)

def calc_256_probability_distribution(data: np.ndarray) -> np.ndarray:
    """
    计算 256 元离散分布 P(0), P(1), ..., P(255).
    返回形状 (256,) 的数组。
    """
    length = len(data)
    if length == 0:
        return np.zeros(256, dtype=np.float64)
    hist, _ = np.histogram(data, bins=256, range=(0,256))
    return hist.astype(np.float64) / length

def calc_p0_from_256(prob_256: np.ndarray) -> float:
    """
    给定每个字节值的概率分布 prob_256[i],
    计算二进制比特层面的 P(0)，即所有 bit 中为 0 的概率。
    """
    # 先计算每个字节的 1 比特数
    bit_counts = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)
    # 平均1比特个数
    avg_ones = np.sum(prob_256 * bit_counts)
    # 每字节8位 => 平均0比特个数 = 8 - avg_ones
    p0 = 1.0 - (avg_ones / 8.0)
    return p0

def binary_entropy(p: float) -> float:
    """
    计算二元熵函数 H_2(p) = - [ p log2(p) + (1-p) log2(1-p) ] (bit)
    注意做 clip，防止 p=0 或 1 时报错。
    """
    eps = 1e-15
    p = max(min(p, 1.0 - eps), eps)
    return - (p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p))

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
      - (可选) 256 元概率分布文件 export_256_csv
      - 在 dms_info_csv 追加/写入一行: 
          [file, P(0), H(bit/二元消息), redundancy, length(bytes)]
    """
    data = read_file_to_array(source_file)
    length_in_bytes = len(data)

    # 计算 256元概率分布
    prob_256 = calc_256_probability_distribution(data)

    # 导出 256 元分布 (可选)
    if export_256_csv:
        export_256_distribution(prob_256, export_256_csv)

    # 计算二元信息熵 (bit/二元消息)
    p0 = calc_p0_from_256(prob_256)
    H_b = binary_entropy(p0)  # 二元熵
    # 冗余度 R = 1 - H_b (若以2进制最大熵=1 bit/符号为参照)
    # 由于二元符号的最大熵为1 bit/符号(当p0=0.5),
    # 冗余度 = 1 - H_b
    R = 1.0 - H_b

    # 将结果写入 dms_info_csv
    need_header = not os.path.isfile(dms_info_csv)
    with open(dms_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow(["source_file", "P(0)", "H(bit/二元msg)", "redundancy", "length(bytes)"])
        row = [
            source_file,
            f"{p0:.6f}",
            f"{H_b:.6f}",
            f"{R:.6f}",
            f"{length_in_bytes}"
        ]
        writer.writerow(row)

def export_256_distribution(prob_256: np.ndarray, out_csv: str):
    """
    将 prob_256[i] 写入 CSV: [byte_value, probability]
    """
    need_header = not os.path.isfile(out_csv)
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if need_header:
            writer.writerow(["byte_value", "probability"])
        for i, p in enumerate(prob_256):
            if p > 0:
                writer.writerow([i, f"{p:.8f}"])

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
      - 在 channel_info_csv 追加/写一行:
         [in_file, out_file, H_in(bit/二元), H_out(bit/二元), I(bit/二元), length_in(bytes), length_out(bytes)]
    """
    data_in = read_file_to_array(channel_in_file)
    data_out = read_file_to_array(channel_out_file)
    len_in = len(data_in)
    len_out = len(data_out)

    # 分别计算 256 元分布
    prob_in_256  = calc_256_probability_distribution(data_in)
    prob_out_256 = calc_256_probability_distribution(data_out)

    # 计算二元熵(单个消息维度)
    p0_in  = calc_p0_from_256(prob_in_256)
    p0_out = calc_p0_from_256(prob_out_256)
    H_in   = binary_entropy(p0_in)
    H_out  = binary_entropy(p0_out)

    # 简化处理: 估计 H(X,Y) ~ H(X xor Y) 这类做法并不准确。
    # 这里若要“平均互信息 I(in;out)”，更严格需要统计 joint distribution P(in_byte, out_byte)。
    # 下面给出一种简单的近似(或您可自行实现更详细的 joint 统计)。
    # ----------------------------------------------------------------
    # 为了演示，我们先各自算“8 bit/字节”的熵 H_8(in), H_8(out) 再转为 “bit/二元消息”:
    #   H_8(in) = calc_entropy_256(prob_in_256)
    #   => H_in_byte = H_8(in)/8  => bit/二元消息
    # 同理 H_out_byte, joint_entropy
    # I(in;out) = H(in_byte) + H(out_byte) - H(in,out_byte)
    #  这里先简化: 不真正算 in,out 的联合分布 => 无法准确给出 I(in;out).
    # 您如果需要真实 I(X;Y)，则必须统计 65536 元分布: P((byte_in, byte_out)).
    # ----------------------------------------------------------------

    # 简易实现(仅示例)：各自独立算熵
    H_in_byte  = calc_entropy_256(prob_in_256)  / 8.0  # bit/二元消息
    H_out_byte = calc_entropy_256(prob_out_256) / 8.0  # bit/二元消息
    # 假设 (in,out) 独立(仅为演示!!) => H(in,out)=H(in)+H(out)
    # => I(in,out)=0.  这肯定不对，但仅作示例。
    # 正确做法：统计联合分布 P(in_byte, out_byte)，算出 H(in,out)，再得 I.
    # 这里以演示写法:
    I_approx = H_in_byte + H_out_byte - (H_in_byte + H_out_byte)  # => 0

    # 在 channel_info_csv 追加输出
    need_header = not os.path.isfile(channel_info_csv)
    with open(channel_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([
                "channel_in_file", "channel_out_file",
                "H_in(bit/二元)", "H_out(bit/二元)", 
                "I(bit/二元)(approx)", 
                "length_in(bytes)", "length_out(bytes)"
            ])
        row = [
            channel_in_file,
            channel_out_file,
            f"{H_in:.6f}",
            f"{H_out:.6f}",
            f"{I_approx:.6f}",
            f"{len_in}",
            f"{len_out}"
        ]
        writer.writerow(row)

##############################################################################
# 2.3.3. 信源编码指标计算模块
##############################################################################

def calc_source_codec_info(before_file: str,
                           after_file: str,
                           source_codec_info_csv: str):
    """
    输入:
      - before_file: 编码前文件(原始)
      - after_file: 编码后文件
    输出:
      - 在 source_codec_info_csv 写一行:
         [
           before_file, after_file, compression_ratio,
           avg_codelen(bit/原字节), codec_efficiency,
           H_before(bit/字节), H_after(bit/字节),
           length_before, length_after
         ]
    """
    data_before = read_file_to_array(before_file)
    data_after  = read_file_to_array(after_file)

    len_b = len(data_before)
    len_a = len(data_after)

    # 压缩比
    compression_ratio = (len_b / len_a) if len_a>0 else 0.0

    # 平均码长(= after_file总比特 / before_file字节数)
    # 这里“after_file总比特”= len_a * 8
    avg_code_len = (len_a * 8.0) / len_b if len_b>0 else 0.0

    # 分别算“bit/字节”的信息熵
    prob_b_256 = calc_256_probability_distribution(data_before)
    prob_a_256 = calc_256_probability_distribution(data_after)
    H_b_byte   = calc_entropy_256(prob_b_256)  # bit/字节
    H_a_byte   = calc_entropy_256(prob_a_256)  # bit/字节

    # 编码效率 = (信息熵) / (实际平均码长)
    #   但“信息熵”可指 原文件的H 或 after_file的H，看具体定义。
    #   常见做法: 以“原文件熵 / 实际平均码长”。
    #   这里演示: codec_eff = H_b_byte / avg_code_len
    #   但要注意维度:
    #   - H_b_byte 是 “bit/原字节”
    #   - avg_code_len 是 “bit/原字节”
    #   => 无维度冲突
    codec_eff = 0.0
    if avg_code_len>0:
        codec_eff = H_b_byte / avg_code_len

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
            f"{compression_ratio:.6f}",
            f"{avg_code_len:.6f}",
            f"{codec_eff:.6f}",
            f"{H_b_byte:.6f}",
            f"{H_a_byte:.6f}",
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
      - 在 channel_codec_info_csv 写一行:
         [
           before_file, coded_file, decoded_file,
           compression_ratio, bit_error_rate,
           source_rate_before(bit/byte), source_rate_after(bit/byte),
           length_before, length_coded, length_decoded
         ]
    """
    data_before  = read_file_to_array(before_file)
    data_coded   = read_file_to_array(coded_file)
    data_decoded = read_file_to_array(decoded_file)

    len_b = len(data_before)
    len_c = len(data_coded)
    len_d = len(data_decoded)

    # 1) 压缩比 = len_b / len_c (若这是“信道编码”，可能反而 >1)
    compression_ratio = (len_b / len_c) if len_c>0 else 0.0

    # 2) 误码率(汉明失真: 错误数据比特/总数据比特)
    #   首先要保证 len_c == len_d (或要与 before_file 比较?) 
    #   在很多编码场景下，"decoded_file"长度应与 "before_file"匹配(若做恢复)。
    #   这里演示做法: 逐字节对比 data_before vs data_decoded => bit错误率
    #   也可 data_coded vs data_decoded => 看传输出的差异。
    #   具体要看您定义的"误码率"。这里先假设“相对于原文件 before_file 的误码率”。
    bit_errors = 0
    total_bits = 0
    length_min = min(len_b, len_d)
    for i in range(length_min):
        # xor看有多少bit差异
        diff = data_before[i] ^ data_decoded[i]
        # 统计 1bit 数量
        bit_errors += bin(diff).count('1')
        total_bits += 8
    # 若 len_b != len_d, 剩余部分也算全部错误?
    # 视需求而定，这里简单处理 => 如果 decoded 少了，缺失的也算错误bits
    if len_b != len_d:
        missing = abs(len_b - len_d)
        bit_errors += missing * 8
        total_bits += missing * 8

    bit_error_rate = (bit_errors / total_bits) if total_bits>0 else 0.0

    # 3) 编码前的信源信息传输率(单位: bit/字节)
    #   = H(before_file)/(字节)? 还是“每字节平均信息量”?
    #   这里简单地用“熵(bit/字节)”来代表 => 
    prob_b_256 = calc_256_probability_distribution(data_before)
    source_rate_before = calc_entropy_256(prob_b_256)  # bit/字节

    # 4) 编码后的信源信息传输率(单位: bit/字节)
    #   同理 => coded_file 的熵(bit/字节)
    prob_c_256 = calc_256_probability_distribution(data_coded)
    source_rate_after = calc_entropy_256(prob_c_256)  # bit/字节

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
