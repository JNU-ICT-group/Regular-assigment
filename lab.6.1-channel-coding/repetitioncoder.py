import sys
import os
from bitstring import BitStream, Bits

#####张朋洋12.12####

def encode_repetition(len_code, input_path, output_path):
    """
    Encodes the input file using repetition code of length len_code.

    len_code: int, repetition code length (must be an odd number and 2 < len_code < 10)
    input_path: str, path to the input file
    output_path: str, path to the output file
    """
    if len_code <= 2 or len_code >= 10 or len_code % 2 == 0:
        raise ValueError("Code length must be an odd number and 2 < len_code < 10.")

    # Read the input file as binary
    with open(input_path, 'rb') as input_file:
        data = input_file.read()

    # Create a BitStream to represent the encoded data
    encoded_stream = BitStream()

    # Encode each bit using repetition code
    for byte in data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            # 将每个比特重复 len_code 次
            encoded_stream.append(Bits(uint=bit, length=1) * len_code)



    # Write the encoded data to the output file
    with open(output_path, 'wb') as output_file:
        encoded_stream.tofile(output_file)


def decode_repetition(input_path, output_path):
    """
    Decodes the repetition code from the input file.

    input_path: str, path to the encoded input file
    output_path: str, path to the decoded output file
    """
    # Read the encoded file as a BitStream
    encoded_stream = BitStream(filename=input_path)

    # Determine the repetition length from the bitstream length (assume constant repetition length)
    len_code = None
    for bit_pos in range(0, len(encoded_stream), 8):
        byte = encoded_stream[bit_pos: bit_pos + 8]
