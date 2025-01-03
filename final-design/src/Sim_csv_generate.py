import csv
import math
import os

from Sim_theoretical_calc import (
    binary_entropy,
    calc_source_info_rate,
    calc_channel_data_rate,
    calc_channel_input_info_rate,
    calc_channel_output_info_rate,
    calc_sink_info_rate,
    calc_sink_error_rate
)

def generate_scenario_csv(
        scenario_id,
        p,
        Pe,
        use_source_coding,
        use_channel_coding,
        n,
        # 下列参数可用于直接覆盖理论计算，使用表格中值
        RS_table=None,
        rc_table=None,
        Rci_table=None,
        Rco_table=None,
        RI_table=None,
        er_table=None
    ):
    """
    针对某一个场景，生成对应的 CSV 文件。
    scenario_id: 用于区分不同场景，比如 1~8.
    其余参数为该场景的设定 + (可选)直接覆盖值。
    """

    # 1. 信源信息率 RS
    if RS_table is not None:
        RS = RS_table
    else:
        RS = calc_source_info_rate(p, rs=1.0, use_source_coding=use_source_coding)

    # 2. 信道数据率 rc
    if rc_table is not None:
        rc = rc_table
    else:
        rc = calc_channel_data_rate(RS, use_channel_coding=use_channel_coding, n=n)
    
    # 3. 信道输入信息率 Rci
    if Rci_table is not None:
        Rci = Rci_table
    else:
        Rci = calc_channel_input_info_rate(RS)
    
    # 4. 信道输出信息率 Rco
    if Rco_table is not None:
        Rco = Rco_table
    else:
        # 演示：先简单用无信道编码公式 or 理想信道编码公式
        if use_channel_coding:
            # 若理想纠错
            Rco = Rci  # 或者有误码时可以自行计算
        else:
            Rco = (1 - Pe) * Rci
    
    # 5. 信宿信息率 RI
    if RI_table is not None:
        RI = RI_table
    else:
        # 演示：直接用 Rco 当做 RI （如果无进一步衰减）
        RI = Rco
    
    # 6. 信宿的误码率 er
    if er_table is not None:
        er = er_table
    else:
        # 若未指定，从函数自动计算
        er = calc_sink_error_rate(Pe, use_channel_coding, repeated_code_n=n)
        # 如果理想纠错 => er 近似 0；这里只是演示，具体等待zzx推导确定后再调整
        if use_channel_coding:
            er = 0.0 if Pe > 0.0 else 0.0  # 这里可自行微调
    
    # 7. 生成输出CSV
    #   指标横向排列：RS, rc, Rci, Rco, RI, er
    headers = ["RS(bit/s)", "rc(bit/s)", "Rci(bit/s)", "Rco(bit/s)", "RI(bit/s)", "er"]
    row_data = [RS, rc, Rci, Rco, RI, er]

    # 定义输出目录
    output_dir = "final-design/data/theoretical_output/"  # 你可以修改为需要的路径
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    # 生成完整的文件路径
    filename = os.path.join(output_dir, f"scenario_{scenario_id}.csv")
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(row_data)

    print(f"[场景 {scenario_id}] CSV文件已生成: {filename}")

if __name__ == "__main__":
    # 若不存在输出文件夹，可以自定义一个文件夹:
    # os.makedirs("scenario_csv", exist_ok=True)
    # 然后把文件都输出到该文件夹下。
    # 这里示例直接输出到当前目录。

    # 下面按照题目给出的表格数据，分别生成 8 个场景的 CSV 文件。
    # 注意：题目中的数值单位均为 比特/秒；误码率是无单位。
    # 为了方便对比，直接把题目表格里的“理论数值”写进来。

    # 场景1
    generate_scenario_csv(
        scenario_id=1,
        p=0.1,
        Pe=0.0,
        use_source_coding=False,
        use_channel_coding=False,
        n=1,
        RS_table=0.469,
        rc_table=1.0,
        Rci_table=0.469,
        Rco_table=0.469,
        RI_table=0.469,
        er_table=0.0
    )

    # 场景2
    generate_scenario_csv(
        scenario_id=2,
        p=0.1,
        Pe=0.0,
        use_source_coding=True,   # 有信源编码
        use_channel_coding=False,
        n=1,
        RS_table=0.469,
        rc_table=0.469,
        Rci_table=0.469,
        Rco_table=0.469,
        RI_table=0.469,
        er_table=0.0
    )

    # 场景3
    generate_scenario_csv(
        scenario_id=3,
        p=0.5,
        Pe=0.01,
        use_source_coding=False,
        use_channel_coding=False,
        n=1,
        RS_table=1.0,
        rc_table=1.0,
        Rci_table=1.0,
        Rco_table=0.99,   # 表格给出
        RI_table=0.99,    # 表格给出
        er_table=0.01
    )

    # 场景4
    generate_scenario_csv(
        scenario_id=4,
        p=0.5,
        Pe=0.01,
        use_source_coding=False,
        use_channel_coding=True,  # 有重复编码
        n=3,
        RS_table=1.0,
        rc_table=3.0,
        Rci_table=1.0,
        Rco_table=0.971,  # 表格给出
        RI_table=0.971,   # 表格给出
        er_table=0.029
    )

    # 场景5
    generate_scenario_csv(
        scenario_id=5,
        p=0.1,
        Pe=0.01,
        use_source_coding=False,
        use_channel_coding=False,
        n=1,
        RS_table=0.469,
        rc_table=1.0,
        Rci_table=0.469,
        Rco_table=0.464,  # 表格给出
        RI_table=0.464,   # 表格给出
        er_table=0.01
    )

    # 场景6
    generate_scenario_csv(
        scenario_id=6,
        p=0.1,
        Pe=0.01,
        use_source_coding=False,
        use_channel_coding=True,
        n=3,
        RS_table=0.469,
        rc_table=3.0,
        Rci_table=0.469,
        Rco_table=0.455,  # 表格给出
        RI_table=0.455,   # 表格给出
        er_table=0.029
    )

    # 场景7
    generate_scenario_csv(
        scenario_id=7,
        p=0.1,
        Pe=0.01,
        use_source_coding=True,
        use_channel_coding=False,
        n=1,
        RS_table=0.469,
        rc_table=0.469,
        Rci_table=0.469,
        Rco_table=0.464,  # 表格给出
        RI_table=0.464,
        er_table=0.01
    )

    # 场景8
    generate_scenario_csv(
        scenario_id=8,
        p=0.1,
        Pe=0.01,
        use_source_coding=True,
        use_channel_coding=True,
        n=3,
        RS_table=0.469,
        rc_table=3.0,
        Rci_table=0.469,
        Rco_table=0.455,  # 表格给出
        RI_table=0.455,
        er_table=0.029
    )
