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


def read_input(in_file_name) -> (np.ndarray, int):
    """使用numpy的fromfile函数读取文件并计算其信息熵"""
    # 使用 numpy.fromfile 以无符号整数形式读取文件
    arr = np.fromfile(in_file_name, dtype=np.uint8)
    return arr, len(arr)

def generate_error_channel(arr, noise) -> np.ndarray:
    """
    使用np.searchsorted对np.random.uniform的结果做分类，使其中1的概率为p（二元对称信道错误传输概率），
    即0的概率为1-p，为了方便使用byteSource产生随机序列，将二元概率空间以8个bit一组，合并为1byte长度，即N=8次扩展。
    然后使用异或将NOISE加载到256元的信源X上。这种方法仅适用于BSC

    Parameters:
        arr (numpy.ndarray): 信源X。
        noise (numpy.ndarray): 信道的噪声。

    Returns:
        numpy.ndarray: 信道输出的信源Y。
    """
    if len(arr) * 8 == len(noise):
        noise = np.packbits(noise)
    out = np.bitwise_xor(arr, noise)
    return out


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

        write_export(export_256_csv , prob_256)


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


noise = read_input(noise_path)
noise_file = generate_error_channel(arr, noise)

def calc_channel_info(channel_in_file: str,
                      noise_file: str,
                      channel_out_file: str,
                      channel_info_csv: str):
    """
    2.2.2. 信道指标计算（融合异或生成输出 + 理想/非理想信道判定）

    输入:
      - channel_in_file  : 信道输入消息序列 (uint8字节序列)
      - noise_file       : 噪声文件 (bit级或byte级), 若 len(arr_in)*8 == len(noise), 则需 packbits
      - channel_out_file : 信道输出消息序列 (uint8字节序列), 由 (in XOR noise) 生成
      - channel_info_csv : 结果CSV文件, 追加以下字段:
         [
           channel_in_file, channel_out_file, noise_file,
           H_in(bit/二元), H_out(bit/二元), I(bit/二元),
           length_in(bytes), length_out(bytes), p
         ]
      其中:
        - p     : (噪声文件中 '1' 的比特占比) => 实际错误传递概率
        - H_in  : 输入消息熵（bit/二元消息）
        - H_out : 输出消息熵（bit/二元消息）
        - I     : 互信息（bit/二元消息），若 p=0 则默认 I=H_in，否则调用外部calc_joint_H_xy等计算
    """

    # ========== 1) 读取输入及噪声 ==========
    data_in = read_file_as_bytes(channel_in_file)
    noise   = read_file_as_bytes(noise_file)

    len_in   = len(data_in)
    len_noise = len(noise)

    # 若输入为空，直接写入CSV并结束
    if len_in == 0:
        need_header = not os.path.isfile(channel_info_csv)
        with open(channel_info_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            if need_header:
                writer.writerow([
                    "channel_in_file", "channel_out_file", "noise_file",
                    "H_in(bit/二元)", "H_out(bit/二元)", "I(bit/二元)",
                    "length_in(bytes)", "length_out(bytes)", "p"
                ])
            writer.writerow([channel_in_file, channel_out_file, noise_file, 0, 0, 0, 0, 0, 0])
        return

    # ========== 2) 解析噪声 (bit级 / byte级) ==========
    # 若 len_in*8 == len_noise => noise是bit级, 需 np.packbits
    # 若 len_in == len_noise  => 已是字节级
    # 否则视为非法输入
    if len_in * 8 == len_noise:
        noise = np.packbits(noise)
    elif len_in == len_noise:
        pass
    else:
        raise ValueError(f"[ERROR] 噪声长度不匹配: len_in={len_in}, len_noise={len_noise}.")

    # 计算噪声中的 '1' 比特占比 => 实际传输错误率 p
    total_bits   = len_in * 8
    num_one_bits = np.unpackbits(noise).sum()
    p = num_one_bits / total_bits

    # ========== 3) 生成信道输出: data_out = data_in XOR noise ==========
    data_out = np.bitwise_xor(data_in, noise)
    # 把 data_out 写到 channel_out_file
    data_out.tofile(channel_out_file)
    len_out = len(data_out)

    # ========== 4) 计算输入消息熵 H_in (bit/二元) ==========
    prob_in_256 = calc_probability(data_in)
    H_in_256 = calc_entropy_256(prob_in_256)  # bit/字节
    H_in_bit = H_in_256 / 8.0                 # bit/二元消息

    # ========== 5) 区分理想 (p=0) / 非理想 (p>0) 信道，计算输出熵 / 互信息 ==========
    if np.isclose(p, 0.0, atol=1e-12):
        # 理想信道 => data_out ~ data_in
        prob_out_256 = calc_probability(data_out)
        H_out_256 = calc_entropy_256(prob_out_256)
        H_out_bit = H_out_256 / 8.0
        I_bit = H_in_bit  # 对无差错信道, I(X;Y)=H(X)=H_in_bit
    else:
        # 非理想信道 => p>0
        # 输出熵 H_out
        prob_out_256 = calc_probability(data_out)
        H_out_256 = calc_entropy_256(prob_out_256)
        H_out_bit = H_out_256 / 8.0

        # 互信息 I(X;Y) = H(X) + H(Y) - H(X,Y)
        try:
            # 若外部模块calcBSCInfo提供了calc_joint_H_xy(data_in, data_out) => 返回bit/字节
            H_xy_256 = calcBSCInfo.calc_joint_H_xy(data_in, data_out)
        except AttributeError:
            # 若尚未实现, 暂用0或自行实现
            H_xy_256 = 0.0
        I_256 = H_in_256 + H_out_256 - H_xy_256
        I_bit = I_256 / 8.0

    # ========== 6) 写结果到 CSV ==========

    need_header = not os.path.isfile(channel_info_csv)
    with open(channel_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([

                "channel_in_file", "channel_out_file", "noise_file",
                "H_in(bit/二元)", "H_out(bit/二元)", "I(bit/二元)",
                "length_in(bytes)", "length_out(bytes)", "p"

            ])
        row = [
            channel_in_file,
            channel_out_file,

            noise_file,
            f"{H_in_bit:.6f}",
            f"{H_out_bit:.6f}",
            f"{I_bit:.6f}",
            f"{len_in}",
            f"{len_out}",
            f"{p:.8f}"

        ]
        writer.writerow(row)

##############################################################################
# 2.3.3. 信源编码指标计算模块
##############################################################################

def calc_source_codec_info(before_file: str,

                           pmf_file_name: str,
                           after_file: str,

                           source_codec_info_csv: str):
    """
    输入:
      - before_file: 编码前文件(原始)

      - pmf_file_name: PMF（概率质量函数）CSV 文件，用于构建霍夫曼编码器
      - after_file: 编码后文件
    输出:
       在 source_codec_info_csv 追加写入一行:
         [
           before_file, after_file, compression_ratio,
           avg_codelen(bit/origin_byte), codec_efficiency,
           H_before(bit/byte), H_after(bit/byte),
           length_before, length_after
         ]
       各符号说明:
         - compression_ratio = (原文件大小)/(编码后文件大小)
         - avg_codelen       = (编码后文件的比特数)/(原文件字节数)
         - codec_efficiency  = (1 - 1/ratio)*100%
         - H_before          = 原文件信息熵(bit/字节)
         - H_after           = 编码后文件信息熵(bit/字节)
    """
    # >>> 1. 使用 PMF 做霍夫曼编码 <<<
    # 调用 encode() 函数 (来自 bytesourceCoder 模块)
    # 将 before_file 编码后写入 after_file
    source_len, encoded_len = bytesourceCoder.encode(pmf_file_name, before_file, after_file, byteorder='little')

    # 如果原文件为空(或异常)，则直接记录并返回
    if source_len == 0:
        # 写入结果 CSV
        need_header = not os.path.isfile(source_codec_info_csv)
        with open(source_codec_info_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            if need_header:
                writer.writerow([
                    "before_file", "after_file",
                    "compression_ratio",
                    "avg_code_len(bit/origin_byte)",
                    "codec_efficiency(%)",
                    "H_before(bit/byte)",
                    "H_after(bit/byte)",
                    "length_before(bytes)",
                    "length_after(bytes)"
                ])
            writer.writerow([before_file, after_file, 0, 0, 0, 0, 0, 0, 0])
        return

    # >>> 2. 分析编码前、编码后文件 <<<
    data_before = read_file_as_bytes(before_file)
    data_after  = read_file_as_bytes(after_file)

    len_b = len(data_before)  # 原文件字节数
    len_a = len(data_after)   # 编码后文件字节数

    # 压缩比
    ratio = calc_compress_ratio(len_b, len_a)
    # 平均码长
    avlen = calc_code_avlen(len_b, len_a)
    # 编码效率
    efficiency = calc_efficiency(ratio)

    # 编码前文件的信息熵 (bit/字节)
    prob_before = calc_probability(data_before)
    H_before = calc_entropy(prob_before)

    # 编码后文件的信息熵 (bit/字节)，跳过头部，对实际编码数据做熵计算
    H_after = calc_huffman_encoded_entropy(after_file)

    # >>> 3. 写入结果 CSV <<<

    need_header = not os.path.isfile(source_codec_info_csv)
    with open(source_codec_info_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if need_header:
            writer.writerow([
                "before_file", "after_file",
                "compression_ratio",
                "avg_code_len(bit/origin_byte)",

                "codec_efficiency(%)",

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

            f"{H_before:.6f}",
            f"{H_after:.6f}",

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

    parser_encode.add_argument('PMF', type=str, help='Path to probability mass function CSV file')
    calc_source_codec_info(source_file, source_codec_file,pmf_file_name, source_codec_info_csv)


    # (4) 2.4.3. 信道编解码指标: RC.info.csv
    channel_codec_info_csv = os.path.join(data_dir, "RC.info.csv")
    calc_channel_codec_info(source_file, channel_in_file, channel_decode_file, channel_codec_info_csv)

    print("[INFO] All done. Check the CSV outputs in:", data_dir)

if __name__ == "__main__":
    main()
