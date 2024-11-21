""" A basic source coder.

This program is a basic demo showing a real-world example of source coding. The key point here is how to handle meta-data, such as codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |header_size  : uint16, number of bytes for header
        |symbol_count : uint8, (number of symbols in codebook)-1
  ______|source_len   : uint32, number of symbols in source
  Code-1|symbol       : uint8, symbol
        |word_len     : uint8, number of bits for codeword
  ______|word         : ceil(word_len/8)*uint8, codeword
    ....|...
  ______|
  Code-n|symbol
        |word_len
________|word
Payload |encoded-data : many unit8

Note: This program is intended for use in course, Principle of Information and Coding Theory.

"""

import csv
import io

# Non-standard library
import numpy as np
from dahuffman_no_EOF import HuffmanCodec

__author__ = "Guo, Jiangling"
__email__ = "tguojiangling@jnu.edu.cn"
__version__ = "20201111.1702"

def encode(pmf_file_name, in_file_name, out_file_name):
    with open(pmf_file_name, newline='') as csv_file:
        pmf = dict([(np.uint8(row[0]), float(row[1])) for row in csv.reader(csv_file)])
    codec = HuffmanCodec.from_frequencies(pmf)

    source = np.fromfile(in_file_name, dtype='uint8')
    encoded = codec.encode(source)

    codebook = codec.get_code_table()
    byteorder = 'little'
    header = bytearray(2)
    header.append(len(codebook)-1)
    header.extend(len(source).to_bytes(4, byteorder))
    for symbol, (word_len, word) in codebook.items():
        (word_len, word) = codebook[symbol]
        word_bytes = int(np.ceil(word_len / 8))
        header.append(symbol)
        header.append(word_len)
        header.extend(word.to_bytes(word_bytes, byteorder))
    header[0:2] = len(header).to_bytes(2, byteorder)

    with open(out_file_name, 'wb') as out_file:
        out_file.write(header)
        out_file.write(encoded)
    
    return (len(source), len(encoded))

def decode(in_file_name, out_file_name):

    byteorder = 'little'
    with open(in_file_name, 'rb') as in_file:
        header_size = int.from_bytes(in_file.read(2), byteorder)
        header = io.BytesIO(in_file.read(header_size-2))
        encoded = in_file.read()
    
    codebook = {}
    symbol_count = header.read(1)[0]
    source_len = int.from_bytes(header.read(4), byteorder)
    for k in range(symbol_count+1):
        symbol = np.uint8(header.read(1)[0])
        word_len = header.read(1)[0]
        word_bytes = int(np.ceil(word_len / 8))
        word = int.from_bytes(header.read(word_bytes), byteorder)
        codebook[symbol] = (word_len, word)
    
    codec = HuffmanCodec(codebook)
    decoded = np.asarray(codec.decode(encoded))[:source_len]
    decoded.tofile(out_file_name)

    return (len(encoded), len(decoded))

def compare_file(file_name_1, file_name_2):
    """Compare two files and count number of different bytes."""
    data1 = np.fromfile(file_name_1, dtype='uint8')
    data2 = np.fromfile(file_name_2, dtype='uint8')

    compare_size = min(data1.size, data2.size)
    if data1.size != data2.size:
        print('[WARNING] These two files have different sizes (in bytes): %d vs %d' % (data1.size, data2.size))
        print('          Comparing the first %d bytes only.' % (compare_size))

    diff_total = np.sum(data1[:compare_size] != data2[:compare_size])
    print('Total %d bytes are different.' % (diff_total))

    return diff_total

def test():
    test_data_dir = 'test-data/'
    pmf_file_name = test_data_dir + 'pmf.byte.p0=0.8.csv'
    source_file_name = test_data_dir + 'source.p0=0.8.len=64KB.dat'
    encoded_file_name = test_data_dir + '_encoded.tmp'
    decoded_file_name = test_data_dir + '_decoded.tmp'

    print('Encoding...')
    (source_len, encoded_len) = encode(pmf_file_name, source_file_name, encoded_file_name)
    print(' source len:', source_len)
    print('encoded len:', encoded_len)
    print('     ratio :', source_len/encoded_len)
    print('')

    print('Decoding...')
    (encoded_len, decoded_len) = decode(encoded_file_name, decoded_file_name)
    print('encoded len:', encoded_len)
    print('decoded len:', decoded_len)
    print('')

    print('Comparing source and decoded...')
    compare_file(source_file_name, decoded_file_name)
    print('')

if __name__ == '__main__':
    test()
