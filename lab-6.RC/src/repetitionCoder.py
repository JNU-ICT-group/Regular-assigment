""" A simple repetition coder.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |LEN  : uint8, code length n, must be odd number and 2 < n < 10
        |source length : uint32, number of symbols in source divided by 8
Payload |codeword sequence : many uint
End |pad : some bits as 0

Note: This program is intended for use in course, Principle of Information and Coding Theory.

"""

import csv
import os
import argparse
import bitstring

# Non-standard library
import numpy as np

__author__ = "Zhang, Pengyang; Chen, Jin; "
__email__ = "miracle@stu2022.jnu.edu.cn"
__version__ = "20241212.2220"


def main():
    parser = argparse.ArgumentParser(description="Lossless source coder for encoding and decoding.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to run (encode or decode)')

    # Encode sub-command
    parser_encode = subparsers.add_parser('encode', help='Encode a source file')
    parser_encode.add_argument('LEN', type=int, help='int, code length n, must be odd number and 2 < n < 10')
    parser_encode.add_argument('INPUT', type=str, help='Path to the encoder input file')
    parser_encode.add_argument('OUTPUT', type=str, help='Path to the encoder output file')

    # Decode sub-command
    parser_decode = subparsers.add_parser('decode', help='Decode an encoded file')
    parser_decode.add_argument('INPUT', type=str, help='Path to the decoder input file')
    parser_decode.add_argument('OUTPUT', type=str, help='Path to the decoder output file')

    parser.add_argument('-t', '--test', action='store_true', help='Check test flow and state')

    args = parser.parse_args()
    INPUT = path_split(args.INPUT)
    OUTPUT = path_split(args.OUTPUT)

    # Execute based on sub-command
    if args.command == 'encode':
        for INPUT, OUTPUT in zip(INPUT, OUTPUT):
            print('Encoding %s (repeats=%d) ...' % (os.path.basename(INPUT), args.LEN))
            (source_len, encoded_len) = encode(args.LEN, INPUT, OUTPUT)
            print(f'\t Source len: {source_len} B')
            print(f'\tEncoded len: {encoded_len} B')
            print(f'\tCompression ratio: {source_len / encoded_len if encoded_len else np.nan:.4f}')

    elif args.command == 'decode':
        for INPUT, OUTPUT in zip(INPUT, OUTPUT):
            print('Decoding %s ...' % os.path.basename(INPUT))
            (encoded_len, decoded_len) = decode(INPUT, OUTPUT)
            print(f'\tEncoded len: {encoded_len} B')
            print(f'\tDecoded len: {decoded_len} B')

    elif args.test:
        test()
    else:
        parser.print_help()


def path_split(path):
    return filter(None, map(str.strip, path.replace('"', '').replace("'", "").split(';')))


# 编码函数
def encode(len_code, input_path, output_path):
    """
    Encodes the input file using repetition code of length len_code.

    len_code: int, repetition code length (must be an odd number and 2 < len_code < 10)
    input_path: str, path to the input file
    output_path: str, path to the output file
    """
    if len_code <= 2 or len_code >= 10 or len_code % 2 == 0:
        raise ValueError("Code length must be an odd number and 2 < len_code < 10.")

    # # Create a BitStream to represent the encoded data
    # stream = bitstring.ConstBitStream(filename=input_path)
    # with open(output_path, 'wb') as f:
    #     encoded = bitstring.BitArray('uint:8=%d, uint:32=%d' % (len_code, stream.length // 8))
    #     one = bitstring.Bits('int:%d=-1' % len_code)
    #     for val in stream:
    #         encoded.append(one if val else len_code)
    #
    #     encoded.tofile(f)

    # Read the input file as binary
    source = np.fromfile(input_path, dtype=np.uint8)

    # Encode each bit using repetition code
    data = np.unpackbits(source).astype(np.uint8)
    data = np.repeat(data, len_code)
    if data.size % 8:
        data = np.pad(data, (0, 8 - (data.size % 8)))
    data.resize((data.size // 8, 8))
    data = np.packbits(data, axis=1)

    # Write the encoded data to the output file
    with open(output_path, 'wb') as output_file:
        output_file.write(len_code.to_bytes(1, 'big'))
        output_file.write(len(source).to_bytes(4, 'big'))
        data.tofile(output_file)

    return (len(source), len(data)-5)  # 返回源数据的长度和编码后的数据长度


# 解码函数
def decode(input_path, output_path):
    """
    Decodes the repetition code from the input file.

    input_path: str, path to the encoded input file
    output_path: str, path to the decoded output file
    """
    # # Read the encoded file as a BitStream
    # encoded_stream = bitstring.ConstBitStream(filename=input_path)
    # # Determine the repetition length from the bitstream length (assume constant repetition length)
    # len_code = encoded_stream.read(8).uint
    # length = encoded_stream.read(32).uint * 8
    # threshord = len_code // 2
    # with open(output_path, 'wb') as f:
    #     decoded_stream = bitstring.BitArray()
    #
    #     one = bitstring.Bits('uint:1=1')
    #     for i in range(length):
    #         decoded_stream.append(one if encoded_stream.read(len_code).count(1) > threshord else 1)
    #
    #     decoded_stream.tofile(f)

    source = np.fromfile(input_path, dtype=np.uint8)
    len_code = source[0]
    msg_length = int.from_bytes(source[1:5].tobytes(), 'big')
    # print(len_code, msg_length)
    data = np.unpackbits(source[5:]).astype(np.uint8)
    code_length = msg_length * 8 * len_code
    threshord = len_code // 2
    data = data[:code_length]
    data.resize((msg_length * 8, len_code))
    data = data.sum(axis=1)
    np.putmask(data, data > threshord, 1)
    data.resize((msg_length, 8))
    data = np.packbits(data, axis=1)
    data.tofile(output_path)

    return (len(source)-5, len(data))  # 返回编码数据的长度和解码后的数据长度


# 测试函数
def test():
    import unittest
    ...


# 主程序入口
if __name__ == '__main__':
    main()
