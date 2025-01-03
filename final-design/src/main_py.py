"""仿真主程序
仿真场景
序号      场景       信源概率分布	信源编码	信道编码	信道错误传递概率
1       信源非理想	P(0)=0.1	有   	无	    0
2       信源非理想	P(0)=0.1	无   	无	    0
3       信道非理想	等概率	    无	    有       0.01
4       信道非理想	等概率	    无	    无       0.01
5       一般非理想	P(0)=0.1	有   	有	    0.01
6       一般非理想	P(0)=0.1	有   	无	    0.01
7       一般非理想	P(0)=0.1	无   	有	    0.01
8       一般非理想	P(0)=0.1	无   	无	    0.01

"""


import os
import sys
import shutil
import typing

sys.path.append('.\\lib\\')
from lib import (byteSource, byteChannel, generate, byteSourceCoder, repetitionCoder,
                 calcDMSInfo, calcBSCInfo, calcCodecInfo, calcErrorRate, calcInfo)


class CASE_BASE(typing.TypedDict):
    prob0: float
    source_codec: bool
    channel_codec: bool
    error_rate: float

cmd_source = byteSource.work_flow
cmd_channel = byteChannel.work_flow
cmd_DMS_create = generate.main
cmd_codec_source = byteSourceCoder.main
cmd_codec_channel = repetitionCoder.main
cmd_calc_source = calcDMSInfo.main
cmd_calc_channel = calcBSCInfo.workflow
cmd_calc_codec_source = calcCodecInfo.work_flow
cmd_calc_codec_channel = calcErrorRate.compare_files
cmd_calc_theory = calcInfo.main
msg_length = 102400
repeat_length = 3
repeat_header_size = 5
rs = 1.0
data_dir = '..\\data'
case_dir = os.path.join(data_dir, 'case_{:d}')
verbose = True

info = [
    (0.1, True, False, 0),
    (0.1, False, False, 0),
    (0.5, False, True, 0.01),
    (0.5, False, False, 0.01),
    (0.1, True, True, 0.01),
    (0.1, True, False, 0.01),
    (0.1, False, True, 0.01),
    (0.1, False, False, 0.01),
]
cases = [CASE_BASE(prob0=x[0], source_codec=x[1], channel_codec=x[2], error_rate=x[3]) for x in info]
# case1 = CASE_BASE(prob0=0.1, source_codec=True, channel_codec=False, error_rate=0)
# case2 = CASE_BASE(prob0=0.1, source_codec=False, channel_codec=False, error_rate=0)
# case3 = CASE_BASE(prob0=0.5, source_codec=False, channel_codec=True, error_rate=0.01)
# case4 = CASE_BASE(prob0=0.5, source_codec=False, channel_codec=False, error_rate=0.01)
# case5 = CASE_BASE(prob0=0.1, source_codec=True, channel_codec=True, error_rate=0.01)
# case6 = CASE_BASE(prob0=0.1, source_codec=True, channel_codec=False, error_rate=0.01)
# case7 = CASE_BASE(prob0=0.1, source_codec=False, channel_codec=True, error_rate=0.01)
# case8 = CASE_BASE(prob0=0.1, source_codec=False, channel_codec=False, error_rate=0.01)
def read_file_size(path):
    with open(path, 'rb') as f:
        f.seek(0, 2)
        return f.tell()

def read_header_size(path):
    with open(path, 'rb') as f:
        return int.from_bytes(f.read(2), 'little')


if not os.path.exists(data_dir) or os.path.isfile(data_dir):
    if os.path.isfile(data_dir):
        os.remove(data_dir)
    os.mkdir(data_dir)

source_info_path = os.path.join(data_dir, 'DMS.info.csv')
channel_info_path = os.path.join(data_dir, 'BSC.info.csv')
channel_codec_info_path = os.path.join(data_dir, 'RC.info.csv')
source_codec_info_path = os.path.join(data_dir, 'HC.info.csv')
theory_info_path = os.path.join(data_dir, 'results.csv')
for info_path in (source_info_path, channel_info_path, channel_codec_info_path, source_codec_info_path, theory_info_path):
    if os.path.isfile(info_path):
        os.remove(info_path)

for i,case in enumerate(cases):
    i+=1
    print('case %d:' % i)
    case_path = case_dir.format(i)
    if os.path.exists(case_path):
        shutil.rmtree(case_path)

    os.mkdir(case_path)
    # 信源
    prob1 = [1. - case['prob0']]
    source_csv_path = os.path.join(case_path, 'DMS.p0=%.3f.csv' % case['prob0'])
    source_path = os.path.join(case_path, 'DMS.p0=%.3f.dat' % case['prob0'])
    cmd_DMS_create(prob1, [source_csv_path])
    cmd_source(source_csv_path, source_path, msg_length, message_state=verbose)
    # 信源编码
    if case['source_codec']:
        source_codec_path = os.path.join(case_path, 'HC.en.p0={:.3f}.dat'.format(case['prob0']))
        cmd_codec_source('encode', PMF=source_csv_path, INPUT=source_path, OUTPUT=source_codec_path, verbose=verbose)
        source_codec_header_path = source_codec_path
        source_codec_header = read_header_size(source_codec_path)
    else:
        source_codec_path = source_path
        source_codec_header_path = ''
        source_codec_header = 0
    # 信道编码
    if case['channel_codec']:
        channel_codec_path = os.path.join(case_path, 'RC.en.p0={:.3f}.dat'.format(case['prob0']))
        cmd_codec_channel('encode', LEN=repeat_length, INPUT=source_codec_path, OUTPUT=channel_codec_path, verbose=verbose)
        channel_codec_header = repeat_header_size
    else:
        channel_codec_header = 0
        channel_codec_path = source_codec_path
    channel_codec_length = read_file_size(channel_codec_path) - (channel_codec_header + repeat_length * source_codec_header)

    # 噪声
    error_rate = case['error_rate']
    noise_csv_path = os.path.join(case_path, 'BSC.p=%.3f.csv' % error_rate)
    noise_path = os.path.join(case_path, 'BSC.p=%.3f.len=%d.dat' % (error_rate, channel_codec_length))
    cmd_DMS_create([error_rate], [noise_csv_path])
    cmd_source(noise_csv_path, noise_path, channel_codec_length,
               pad=(channel_codec_header + repeat_length * source_codec_header,0,0,0), message_state=verbose)
    # 信道传输
    channel_path = os.path.join(case_path, 'BSC.p0=%.3f.p=%.3f.dat' % (case['prob0'], error_rate))
    cmd_channel(channel_codec_path, channel_path, noise_path, message_state=verbose)

    # 信道解码
    if case['channel_codec']:
        channel_decode_path = os.path.join(case_path, 'RC.de.p0=%.3f.p=%.3f.dat' % (case['prob0'], error_rate))
        cmd_codec_channel('decode', INPUT=channel_path, OUTPUT=channel_decode_path, verbose=verbose)
    else:
        channel_decode_path = channel_path
    # 信源解码
    if case['source_codec']:
        source_decode_path = os.path.join(case_path, 'HC.de.p0={:.3f}.p={:.3f}.dat'.format(case['prob0'], error_rate))
        cmd_codec_source('decode', INPUT=channel_decode_path, OUTPUT=source_decode_path, verbose=verbose)
    else:
        source_decode_path = channel_decode_path

    # 计算实测指标
    source_pmf_path = os.path.join(case_path, 'DMS.pmf.p0=%.3f.csv' % case['prob0'])
    cmd_calc_source(source_path, source_info_path, export_p=source_pmf_path, message_state=verbose)
    cmd_calc_channel(channel_codec_path, channel_path, channel_info_path, verbose=verbose)
    cmd_calc_codec_channel(source_codec_path, channel_codec_path, channel_decode_path, channel_codec_info_path,
                        case['channel_codec'], verbose)
    cmd_calc_codec_source(source_path, source_codec_path, source_codec_info_path,
                        header_size=source_codec_header, message_state=verbose)
    # 理论计算和表格统计
    cmd_calc_theory(
        source_info_path, source_codec_info_path, channel_codec_info_path, theory_info_path,
        p0=case['prob0'], p=error_rate, rs=rs, source_codec_header=source_codec_header_path, LEN=repeat_length, message_state=verbose
    )

