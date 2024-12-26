import numpy as np

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
    try:
        source = np.fromfile(input_path, dtype=np.uint8)
    except ValueError:
        raise ValueError("Decoding a File Empty.")
    len_code = int(source[0])
    encoder_length = len(source)
    if encoder_length < 5:
        raise TypeError("Haven't a Header.")
    msg_length = int.from_bytes(source[1:5].tobytes(), 'big')
    # print(len_code, msg_length)
    if encoder_length - 5 < msg_length * len_code:
        raise TypeError("Payload doesn't follow the rules of Header.")
    data = np.unpackbits(source[5:]).astype(np.uint8)
    code_length = msg_length * 8 * len_code
    threshord = len_code // 2
    data = data[:code_length]
    data.resize((msg_length * 8, len_code))
    data = (data.sum(axis=1) > threshord).view(np.uint8)
    data.resize((msg_length, 8))
    data = np.packbits(data, axis=1)
    data.tofile(output_path)

    return (len(source)-5, len(data))  # 返回编码数据的长度和解码后的数据长度

