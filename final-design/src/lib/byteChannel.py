""" Generate a channel with specified error transmission probability of a BSC.

This program is intended for used in course, Principle of Information and Coding Theory.
Usage details can be displayed by passing command line argument `--help`.

Note: All information contents calculated are bit-wise, i.e. in (information-)bit per (binary-)bit.
v1.2 改为无扩展二元信道
模块输入
	信道输入消息序列文件
    错误传递概率p
模块输出
	信道输出消息序列文件

"""

# Standard library
import os.path
import argparse

# Non-standard library
import numpy as np

__author__ = "Chen, Jin; "
__email__ = "miracle@stu2022.jnu.edu.cn; "
__version__ = "20241031.1001"


bit_counts = np.float32(bytearray(map(int.bit_count, range(256))))

def generate(ones):
    probs = []
    for p in ones:
        w1 = p ** bit_counts
        w2 = (1-p) ** (8 - bit_counts)
        probs.append(w1 * w2)
    return probs


def main(input_path, output_path, noises, **kwgs):
    input_paths = path_split(input_path)
    output_paths = path_split(output_path)
    ones = map(float, noises.split(','))
    probs = generate(ones)

    for input_path, noise, output_path, prob in zip(input_paths, noises, output_paths, probs):
        if kwgs.get('message_state'):
            print('Processing INPUT "%s" OUTPUT "%s" with NOISE "%.3f"...' % (input_path, output_path, float(noise)))
        work_flow(input_path, output_path, prob, **kwgs)


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


def work_flow(input_path, output_path, prob, **kwgs):
    if kwgs.get('base_path'):
        input_path = os.path.join(kwgs['base_path'], input_path)
        output_path = os.path.join(kwgs['base_path'], output_path)
    if kwgs.get('message_state') == 1:
        print('\tInput path:', input_path)
        print('\tOutput path:', output_path)
    if not os.path.isfile(input_path):
        raise RuntimeError("input_path must be an exist file.")
    if os.path.exists(output_path) and not os.path.isfile(output_path):
        raise RuntimeError("output_path must be a file, not a folder.")

    if kwgs.get('message_state') == 1:
        print()
    arr = read_input(input_path)
    noise = random_sequence(prob, len(arr))
    pad_left, v1, pad_right, v2 = kwgs.get('pad', (0,0,0,0))
    if pad_left:
        noise[:pad_left] = v1
    if pad_right:
        noise[-pad_right:] = v2

    out = generate_error_channel(arr, noise)
    write_output(output_path, out)


def read_input(input_path) -> np.ndarray:
    """
    从CSV文件中读取信源数据。

    Parameters:
        input_path (str): 文件路径。

    Returns:
        numpy.ndarray: 256元信源数据。
    """
    return np.fromfile(input_path, dtype=np.uint8)


def random_sequence(symbol_prob, msg_len) -> np.ndarray:
    """
    使用 np.searchsorted 生成符合指定概率分布的随机序列（蒙特卡罗法）

    Parameters:
        symbol_prob (numpy.ndarray): 符号的概率分布。
        msg_len (int): 生成的消息长度（符号数量）。

    Returns:
        numpy.ndarray: 生成的符号序列。
    """
    # 计算累积概率分布 F(i)
    symbol_cumsum = symbol_prob.cumsum()

    # 生成符合均匀分布的随机数，并通过累积概率分布查找对应符号
    msg_len = int(msg_len)
    symbol_random = np.random.uniform(size=msg_len)
    msg = np.searchsorted(symbol_cumsum, symbol_random)
    return msg.astype(np.uint8)


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


def write_output(output_path, sequence) -> None:
    """

    Parameters:
        output_path (str): 输出文件的路径。
        sequence (numpy.ndarray): 生成的符号序列。
    """
    sequence.tofile(output_path)


def parse_sys_args() -> dict:
    """
    Parse command line arguments using argparse and return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="Process some commands for byteChannel.")
    parser.add_argument('INPUT', nargs='?', help='Input file path')
    parser.add_argument('p', help='Probability of Error-Rate.')
    parser.add_argument('OUTPUT', nargs='?', help='Output file path')
    parser.add_argument('-d', '--dir', type=str, help='Base directory path')
    parser.add_argument('-O', action='store_true', help='Full prompt output')
    parser.add_argument('-S', action='store_true', help='Weak prompt output')
    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    args = parser.parse_args()
    return dict(
        input_path=args.INPUT,
        noises=args.p,
        output_path=args.OUTPUT,
        base_path=args.dir,
        message_state=1 if args.O else 2 if args.S else 0,
        test_flow=args.test,
        show_version=args.version,
    )


if __name__ == "__main__":
    kwgs = parse_sys_args()

    if kwgs['show_version']:
        print(__version__)

    if kwgs['test_flow']:
        import byteChannelTest
        byteChannelTest.test_flow()

    if kwgs['base_path']:
        if not os.path.exists(kwgs['base_path']) or os.path.isfile(kwgs['base_path']):
            raise RuntimeError("base-path must be an exist folder.")

    if kwgs['input_path'] and kwgs['output_path']:
        main(**kwgs)
