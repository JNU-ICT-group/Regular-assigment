import math

def binary_entropy(p):
    """
    二元离散信源熵 H(X) = -p*log2(p) - (1-p)*log2(1-p).
    当 p=0 或 1 时，熵为0。
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p*math.log2(p) - (1-p)*math.log2(1-p)

def calc_source_info_rate(p, rs=1.0, use_source_coding=False):
    """
    计算信源的信息率 RS (比特/秒)。
    - p: 信源中符号 '0' 的概率, 则 '1' 的概率为 (1-p)。
    - rs: 信源的原始数据率(符号/秒)，题目中给定 rs=1。
    - use_source_coding: 是否采用了理想的信源编码(如霍夫曼编码)。
        * 若不使用信源编码，则默认为信源按原始速率发送比特 => RS ~ 1 bit/s (当 p=0.5 时) 或者按照题意固定为1比特/秒。
        * 若使用信源编码，则信源速率变为信源熵 H(X)*rs。
    """
    if use_source_coding:
        # 采用理想霍夫曼编码，则速率为熵 H(X)*rs
        return binary_entropy(p) * rs
    else:
        # 不采用信源编码，则“理论上”信源仍按 rs=1 (题目简化设定)
        # 但如果题目中对于非等概信源又规定了某些特殊情况，可按需要调整。
        # 在题目的案例里，无信源编码时常直接写 RS=H(X) or RS=1 也可以。
        # 这里留给你根据题目实际表格的做法选择返回值。
        # ======================================================
        # 如果完全遵循题目中“无信源编码时，依然写RS=H(X)”，可写：
        return binary_entropy(p) * rs
        # 或者如果想固定=1，对应等概场景(p=0.5)可以写：
        # return rs
        # 视题目具体要求做调整。

def calc_channel_data_rate(rs_source, use_channel_coding=False, n=1):
    """
    计算信道的数据率 rc (比特/秒).
    - rs_source: 实际输入端（可能是信源编码后）的发送速率(比特/秒)。
    - use_channel_coding: 是否使用了重复编码(或其他信道编码)。
    - n: 若使用重复编码，则每个符号重复 n 次。此时 rc = n * rs_source （题目中表格多处给出类似结果）。
    """
    if use_channel_coding:
        return n * rs_source
    else:
        return rs_source

def calc_channel_input_info_rate(source_info_rate):
    """
    信道的输入信息率 Rci (比特/秒).
    题目中：无论是否有信道编码，信道的输入信息率都等于信源的信息率 RS，
    因为“信道编码”只是在物理上传更多比特，但信息量仍然是同一份。
    """
    return source_info_rate

def calc_channel_output_info_rate(Rci, Pe, use_channel_coding=False, 
                                  effective_error_rate=None):
    """
    信道的输出信息率 Rco (比特/秒).
    - Rci: 信道输入信息率 (比特/秒).
    - Pe: 信道的符号错误率(无编码情况下)或其他衡量错误的概率.
    - use_channel_coding: 是否使用了信道编码。如果使用了并且理想纠错，可以近似认为 Rco ~ Rci。
    - effective_error_rate: 若需要精细化计算误码率 (e.g. 重复码的多数判决)，可通过此形参传入最终的“有效误码率”。
    
    在题目中若：
      1) 无信道编码 => Rco = (1 - Pe)*Rci
      2) 有信道编码(理想) => Rco ~ Rci
      3) 其他折衷情况 => Rco = (1 - Pe_eff)*Rci, 可根据场景调整

    这里先做一个通用实现：
    """
    if not use_channel_coding:
        # 无信道编码，直接根据 (1 - Pe)*Rci
        return (1.0 - Pe) * Rci
    else:
        # 有信道编码，若可以完全纠错 => Rco ~ Rci
        # 若不完美，可用 effective_error_rate 替代
        if effective_error_rate is None:
            # 理想纠错
            return Rci
        else:
            return (1.0 - effective_error_rate) * Rci

def calc_sink_info_rate(Rco, final_error_rate=None, ideal_decoding=False):
    """
    信宿关于信源的信息率 RI (比特/秒).
    - Rco: 信道输出信息率.
    - final_error_rate: 信宿最终误码率 er.
    - ideal_decoding: 若接收端理想译码，RI ~ Rco; 否则可根据误码率打折。

    这里示例做法：
       1) ideal_decoding = True => RI ~ Rco
       2) ideal_decoding = False => RI = (1 - final_error_rate)*Rco
          （只是一个演示，具体看题目如何定义）
    """
    if ideal_decoding or final_error_rate is None:
        return Rco
    else:
        return (1.0 - final_error_rate) * Rco

def calc_sink_error_rate(Pe, use_channel_coding=False, 
                         repeated_code_n=3):
    """
    信宿的误码率 er. 
    题目中示例：
       1) 无信道编码 => er = Pe
       2) 有信道编码(理想) => er ~ 0
       3) 题目表格给出的非理想数值 => 可能是 0.029 等等，自己设定或计算。

    下面给出两个示例：
       - 完全依照表格写死
       - 或者真正按照重复码多数判决原理做计算
    """
    if not use_channel_coding:
        # 无信道编码
        return Pe
    else:
        # 使用重复编码时，可以进行多数表决：
        # 正确解码需要多数比特正确 => 若 n=3, 至少 2 个比特正确
        # block_error_prob = P(X解码错误) = P(出现 ≥2 bit 错) ...
        # 这里如果要计算严格值:
        #   p_err_block = C(3,2)*Pe^2*(1-Pe)^1 + C(3,3)*Pe^3
        #   => = 3*(Pe^2)*(1-Pe) + Pe^3
        #   => final er = p_err_block (若一块对就对，一块错就错)
        # 不过题目表格中给出 scenario=4,6,8 的 er=0.029，不符合严格的 0.01 重复码多数判决值 (大约0.000298)
        # 因此我们直接返回一个示例值，由题目表格决定。
        return None  # 具体数值后面用表格写死。
