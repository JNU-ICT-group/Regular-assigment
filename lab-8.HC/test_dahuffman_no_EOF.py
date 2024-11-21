""" A test for `dahuffman_no_EOF`.

This test consists of three parts:
1. `dahuffman`
2. `dahuffman_no_EOF` (with decode-triming)
3. `dahuffman_no_EOF` without decode-triming

This program is intended for use in course, Principle of Information and Coding Theory.
"""

import csv
import os

# Non-standard library
import numpy as np
import dahuffman
import dahuffman_no_EOF

__author__ = "Guo, Jiangling"
__email__ = "tguojiangling@jnu.edu.cn"
__version__ = "20201127.1106"

def read_pmf(pmf_file_name):
    """Read PMF from a CSV file and return it as a dictionary."""
    with open(pmf_file_name, newline='') as csv_file:
        pmf = dict([(np.uint8(row[0]), float(row[1])) for row in csv.reader(csv_file)])
    return pmf

def encode(codec_class, pmf_file_name, in_file_name, out_file_name):
    """Encode a file using specified codec."""
    pmf = read_pmf(pmf_file_name)
    codec = codec_class.from_frequencies(pmf)

    source = np.fromfile(in_file_name, dtype='uint8')
    encoded = codec.encode(source)
    with open(out_file_name, 'wb') as out_file:
        out_file.write(encoded)

    return (len(source), len(encoded))

def decode(codec_class, pmf_file_name, in_file_name, out_file_name, source_len=None):
    """Decode a file using specified codec.
    If source_len is given, only decode up to source_len bytes.
    """
    pmf = read_pmf(pmf_file_name)
    codec = codec_class.from_frequencies(pmf)

    encoded = np.fromfile(in_file_name, dtype='uint8')

    decoded = np.asarray(codec.decode(encoded))
    if source_len is not None:
        decoded = decoded[:source_len]

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

def test_run(codec_class, decode_triming=True):
    """Run a test with given codec class."""
    test_data_dir = 'test-data/'
    pmf_file_name = test_data_dir + 'pmf.byte.p0=0.8.csv'
    source_file_name = test_data_dir + 'source.p0=0.8.len=64KB.dat'
    encoded_file_name = test_data_dir + '_encoded.tmp'
    decoded_file_name = test_data_dir + '_decoded.tmp'

    print('Encoding...')
    (source_len, encoded_len) = encode(codec_class, pmf_file_name, source_file_name, encoded_file_name)
    print(' source len:', source_len)
    print('encoded len:', encoded_len)
    print('     ratio :', source_len/encoded_len)
    print('')

    print('Decoding...')

    if decode_triming:
        (encoded_len, decoded_len) = decode(codec_class, pmf_file_name, encoded_file_name, decoded_file_name, source_len)
    else:
        (encoded_len, decoded_len) = decode(codec_class, pmf_file_name, encoded_file_name, decoded_file_name)

    print('encoded len:', encoded_len)
    print('decoded len:', decoded_len)
    print('')

    print('Comparing source and decoded...')
    compare_file(source_file_name, decoded_file_name)
    print('')

    os.remove(encoded_file_name)
    os.remove(decoded_file_name)

def main():
    print('###############################')
    print('# Testing dahuffman')
    print('###############################')
    test_run(dahuffman.HuffmanCodec)

    print('###############################')
    print('# Testing dahuffman_no_EOF')
    print('###############################')
    test_run(dahuffman_no_EOF.HuffmanCodec)

    print('###############################')
    print('# Testing dahuffman_no_EOF (do not trim decoded)')
    print('###############################')
    test_run(dahuffman_no_EOF.HuffmanCodec, decode_triming=False)

if __name__ == '__main__':
    main()
