import sys

"""
生成二进制数据概率分布
"""

bit_counts = bytearray(map(int.bit_count, range(256)))

def main(ones, output_paths):
    for p, output_path in zip(ones, output_paths):
        w = 1-p
        with open(output_path, 'w') as f:
            for i, one in enumerate(bit_counts):
                p_one = p ** one * w ** (8-one)
                f.write('%d,%.8f\n' % (i, p_one))


if __name__ == "__main__":
    ones = map(float, sys.argv[-2].split(','))
    output_paths = filter(None, map(str.strip, sys.argv[-1].split(';')))
    main(ones, output_paths)
