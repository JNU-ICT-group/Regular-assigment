import numpy as np

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
