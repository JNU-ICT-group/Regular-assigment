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
import subprocess
from subprocess import check_call
import typing


class CASE_BASE(typing.TypedDict):
    prob0: float
    source_codec: bool
    channel_codec: bool
    error_rate: float

cmd_source = r'python lib\byteSource.py '
cmd_channel = r'python lib\byteChannel.py '
cmd_DMS_create = r'python lib\generate.py '
cmd_codec_source = r'python lib\byteSourceCoder.py '
cmd_codec_channel = r'python lib\repetitionCoder.py '
cmd_calc_source = r'python lib\calcDMSInfo.py '
cmd_calc_channel = r'python lib\calcBSCInfo.py '
cmd_calc_codec_source = r'python lib\calcCodecInfo.py '
cmd_calc_codec_channel = r'python lib\calcErrorRate.py '
cmd_calc_theory = r'python lib\calcInfo.py '
msg_length = 102400
repeat_length = 3
repeat_header_size = 5
rs = 1.0
data_dir = '..\\data'
case_dir = os.path.join(data_dir, 'case_{:d}')

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
# for info_path in (source_info_path, channel_info_path, channel_codec_info_path, source_codec_info_path, theory_info_path):
#     if os.path.isfile(info_path):
#         os.remove(info_path)

for i,case in enumerate(cases):
    i+=1
    print('case %d:' % i)
    case_path = case_dir.format(i)
    if os.path.exists(case_path):
        shutil.rmtree(case_path)

    os.mkdir(case_path)
    # 信源
    prob1 = 1. - case['prob0']
    source_csv_path = os.path.join(case_path, 'DMS.p0=%.3f.csv' % case['prob0'])
    source_path = os.path.join(case_path, 'DMS.p0=%.3f.dat' % case['prob0'])
    check_call(cmd_DMS_create + ' {:.3f} {:s}'.format(prob1, source_csv_path))
    check_call(cmd_source + ' "{:s}" "{:s}" {:d}'.format(source_csv_path, source_path, msg_length))
    # 信源编码
    if case['source_codec']:
        source_codec_path = os.path.join(case_path, 'HC.en.p0={:.3f}.dat'.format(case['prob0']))
        check_call(cmd_codec_source + ' -v encode "{}" "{}" "{}"'.format(source_csv_path, source_path, source_codec_path))
        source_codec_header_path = source_codec_path
        source_codec_header = read_header_size(source_codec_path)
    else:
        source_codec_path = source_path
        source_codec_header_path = ''
        source_codec_header = 0
    # 信道编码
    if case['channel_codec']:
        channel_codec_path = os.path.join(case_path, 'RC.en.p0={:.3f}.dat'.format(case['prob0']))
        check_call(cmd_codec_channel + ' -v encode {:d} "{}" "{}"'.format(repeat_length, source_codec_path, channel_codec_path))
        channel_codec_header = repeat_header_size
    else:
        channel_codec_header = 0
        channel_codec_path = source_codec_path
    channel_codec_length = read_file_size(channel_codec_path) - (channel_codec_header + repeat_length * source_codec_header)

    # 噪声
    error_rate = case['error_rate']
    noise_csv_path = os.path.join(case_path, 'BSC.p=%.3f.csv' % error_rate)
    noise_path = os.path.join(case_path, 'BSC.p=%.3f.len=%d.dat' % (error_rate, channel_codec_length))
    check_call(cmd_DMS_create + ' {:.3f} {:s}'.format(error_rate, noise_csv_path))
    check_call(cmd_source + ' "{:s}" "{:s}" {:d} -p ({},0,0,0)'.format(
        noise_csv_path, noise_path, channel_codec_length, (channel_codec_header + repeat_length * source_codec_header)))
    # 信道传输
    channel_path = os.path.join(case_path, 'BSC.p0=%.3f.p=%.3f.dat' % (case['prob0'], error_rate))
    check_call(cmd_channel + ' "{}" "{}" "{}" -O'.format(channel_codec_path, noise_path, channel_path))

    # 信道解码
    if case['channel_codec']:
        channel_decode_path = os.path.join(case_path, 'RC.de.p0=%.3f.p=%.3f.dat' % (case['prob0'], error_rate))
        check_call(cmd_codec_channel + ' -v decode "{}" "{}"'.format(channel_path, channel_decode_path))
    else:
        channel_decode_path = channel_path
    # 信源解码
    if case['source_codec']:
        source_decode_path = os.path.join(case_path, 'HC.de.p0={:.3f}.p={:.3f}.dat'.format(case['prob0'], error_rate))
        check_call(cmd_codec_source + ' -v decode "{}" "{}"'.format(channel_decode_path, source_decode_path))
    else:
        source_decode_path = channel_decode_path

    # 计算实测指标
    source_pmf_path = os.path.join(case_path, 'DMS.pmf.p0=%.3f.csv' % case['prob0'])
    check_call(cmd_calc_source + ' "{}" "{}" --export-p "{}"'.format(source_path, source_info_path, source_pmf_path))
    check_call(cmd_calc_channel + ' "{}" "{}" "{}" -v'.format(
        channel_codec_path, channel_path, channel_info_path))
    check_call(cmd_calc_codec_channel + ' "{}" "{}" "{}" "{}" -v {}'.format(
        source_codec_path, channel_codec_path, channel_decode_path, channel_codec_info_path,
        ('' if case['channel_codec'] else '--no-header')))
    check_call(cmd_calc_codec_source + ' "{}" "{}" "{}" -p {:d} -O'.format(
        source_path, source_codec_path, source_codec_info_path, source_codec_header))
    # 理论计算和表格统计
    check_call(cmd_calc_theory + ' --p0 {:.4f} -p {:.5f} --rs {:.3f} --HEADER "{}" --LEN {:d}'
                                 ' "{}" "{}" "{}" "{}"'.format(
        case['prob0'], error_rate, rs, source_codec_header_path, repeat_length,
        theory_info_path, source_info_path, source_codec_info_path, channel_codec_info_path
    ))

