#generate.py#

import sys

def bit_count(n):
    return bin(n).count('1')

bit_counts = bytearray(map(bit_count, range(256)))

def main(ones, output_paths):
    for p, output_path in zip(ones, output_paths):
        w = 1-p
        with open(output_path, 'w') as f:
            for i, one in enumerate(bit_counts):
                p_one = p ** one * w ** (8-one)
                f.write('%d,%.8f\n' % (i, p_one))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python generate.py <概率列表> <输出文件列表>")
        print("示例: python generate.py \"0.1,0.2,0.3\" \"output1.txt;output2.txt;output3.txt\"")
        sys.exit(1)
    
    ones = map(float, sys.argv[-2].split(','))
    output_paths = filter(None, map(str.strip, sys.argv[-1].split(';')))
    main(ones, output_paths)
