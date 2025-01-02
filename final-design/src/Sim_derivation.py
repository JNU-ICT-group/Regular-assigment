"""
calc_pipeline_from_config.py

读取 config.json 中的脚本路径及 8 种场景配置，依次执行:
1) calcDMSInfo.py
2) calcBSCInfo.py
3) calcErrorRate.py (or calcCodecInfo.py, naming depends on your usage)
4) calcCodecInfo.py
5) calcInfo.py

并把统计结果输出到 data_dir 下的若干 csv 文件。
"""

import os
import sys
import json
import subprocess
from subprocess import CalledProcessError
from pathlib import Path


def load_config(config_path="config.json"):
    """从配置文件中加载JSON配置，并返回一个dict。"""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def run_command(cmd):
    """封装子进程调用，并在出错时抛出异常。"""
    print("[CMD] ", cmd)
    try:
        subprocess.check_call(cmd, shell=True)
    except CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(e.returncode)

def main():
    # 1. 读取配置
    config = load_config("config.json")

    # 获取当前脚本路径
    current_path = Path(__file__).parent
    # 获取上级目录中的 data 目录
    data_dir = current_path.parent / 'data'
    # 确保目录存在
    data_dir.mkdir(exist_ok=True)

    # 2. 取出公共配置
    data_dir = config.get("data_dir", "./data")
    rs = config.get("rs", 1.0)
    repeat_length = config.get("repeat_length", 3)
    source_codec_header = config.get("source_codec_header", 0)

    # 3. 取出子脚本路径
    calc_source = config["calc_source"]             # e.g. "lib/calcDMSInfo.py"
    calc_channel = config["calc_channel"]           # e.g. "lib/calcBSCInfo.py"
    calc_codec_channel = config["calc_codec_channel"]  # e.g. "lib/calcErrorRate.py"
    calc_codec_source = config["calc_codec_source"] # e.g. "lib/calcCodecInfo.py"
    calc_theory = config["calc_theory"]            # e.g. "lib/calcInfo.py"

    # 4. 对应的输出 CSV (可以固定写，或者灵活命名)
    source_info_path = os.path.join(data_dir, 'DMS.info.csv')
    channel_info_path = os.path.join(data_dir, 'BSC.info.csv')
    channel_codec_info_path = os.path.join(data_dir, 'RC.info.csv')
    source_codec_info_path = os.path.join(data_dir, 'HC.info.csv')
    theory_info_path = os.path.join(data_dir, 'results.csv')

    # 5. 获取 8 种场景的列表
    cases = config["cases"]
    print(f"[INFO] Loaded {len(cases)} case(s)")

    for i, case in enumerate(cases):
        prob0 = case["prob0"]
        source_codec_flag = case["source_codec"]
        channel_codec_flag = case["channel_codec"]
        error_rate = case["error_rate"]

        print("\n" + "="*60)
        print(f"[CASE {i+1}] prob0={prob0}, source_codec={source_codec_flag}, "
              f"channel_codec={channel_codec_flag}, error_rate={error_rate}")
        print("="*60 + "\n")

        # 计算 p1
        p1 = 1.0 - prob0

        # 已经有了诸如:
        #   source_path, channel_codec_path, channel_path, channel_decode_path, 等文件
        #   这里假设文件命名规律类似：
        source_file_base  = f"DMS.p0={prob0:.3f}.dat"             # 原始信源文件
        source_codec_file = f"HC.en.p0={prob0:.3f}.dat"           # 源编码后文件
        channel_codec_file = f"RC.en.p0={prob0:.3f}.dat"          # 信道编码后文件
        channel_file = f"BSC.p0={prob0:.3f}.p={error_rate:.3f}.dat"  # 信道输出文件
        channel_decode_file = f"RC.de.p0={prob0:.3f}.p={error_rate:.3f}.dat"  # 信道解码后文件

        # 实际路径
        source_path           = os.path.join(data_dir, source_file_base)
        source_codec_path     = os.path.join(data_dir, source_codec_file)
        channel_codec_path    = os.path.join(data_dir, channel_codec_file)
        channel_path          = os.path.join(data_dir, channel_file)
        channel_decode_path   = os.path.join(data_dir, channel_decode_file)













        # 6) 构造对各脚本的命令行

        # 6.1) calc_source => 统计信源指标
        #     --export-p "..." =>  输出 256元分布
        source_pmf_path = os.path.join(
            data_dir,
            f"DMS.pmf.p0={prob0:.3f}.p={error_rate:.3f}.csv"
        )
        cmd_calc_source = (
            f'python "{calc_source}" '
            f'"{source_path}" '       # 读信源文件
            f'"{source_info_path}" '  # 写/追加结果
            f'--export-p "{source_pmf_path}"'
        )

        # 6.2) calc_channel => 统计信道指标(BSC)
        #     输入: channel_codec_path (信道输入), channel_path (信道输出), channel_info_path
        cmd_calc_channel = (
            f'python "{calc_channel}" '
            f'"{channel_codec_path}" '
            f'"{channel_path}" '
            f'"{channel_info_path}" '
            f'-v'
        )

        # 6.3) calc_codec_channel => 统计信道编解码指标
        #     输入: source_codec_path + channel_codec_path + channel_decode_path + channel_codec_info_path
        cmd_calc_codec_channel = (
            f'python "{calc_codec_channel}" '
            f'"{source_codec_path}" '
            f'"{channel_codec_path}" '
            f'"{channel_decode_path}" '
            f'"{channel_codec_info_path}" '
            f'-v'
        )

        # 6.4) calc_codec_source => 统计源编解码指标
        #     -p {source_codec_header} => 头部大小
        cmd_calc_codec_source = (
            f'python "{calc_codec_source}" '
            f'"{source_path}" '
            f'"{source_codec_path}" '
            f'"{source_codec_info_path}" '
            f'-p {source_codec_header} '
            f'-O'
        )

        # 6.5) calc_theory => 理论计算
        #     --p1 {p1} -p {error_rate} --rs {rs} --LEN {repeat_length} ...
        cmd_calc_theory = (
            f'python "{calc_theory}" '
            f'--p1 {p1:.3f} '
            f'-p {error_rate:.3f} '
            f'--rs {rs:.3f} '
            f'--LEN {repeat_length} '
            f'--SOURCE "{source_info_path}" '
            f'--SOURCE_CODEC "{source_codec_info_path}" '
            f'--CHANNEL_CODEC "{channel_codec_info_path}" '
        )

        # 7) 依次调用
        run_command(cmd_calc_source)
        run_command(cmd_calc_channel)
        run_command(cmd_calc_codec_channel)
        run_command(cmd_calc_codec_source)
        run_command(cmd_calc_theory)

    print("\n[INFO] All 8 cases done!")
    print("[INFO] Check CSV outputs in:", data_dir)
    print("[INFO] source_info_path =", source_info_path)
    print("[INFO] channel_info_path =", channel_info_path)
    print("[INFO] channel_codec_info_path =", channel_codec_info_path)
    print("[INFO] source_codec_info_path =", source_codec_info_path)
    print("[INFO] theory_info_path =", theory_info_path)

if __name__ == "__main__":
    main()
