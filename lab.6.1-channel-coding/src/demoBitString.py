""" A demo program to do bit-packing with `bitstring` module.

Bit-packing is an essential procedure in coding and communication, to efficiently represent a sequence of values in binary form. It can be summarized as

- Store minimum amount of bits for each value.
- Bits of all values are stored consecutively, without any gaps (other bits) in between.

Although bit-packing is relatively simple to implement in digital circuits, it is not trivial to implement in computer program. One of the main reasons is that, in most computer language, byte (8 bits) is the smallest data unit. Even if a language has boolean type (True/False), it is usually represented by one whole byte, not a single bit.

Therefore, to implement bit-packing in computer program, some difficulties must be dealt with, such as

- How to 'pack' several values' bits into one single byte? (bit-merging)
- How to put a value's bits across two or more bytes? (bit-splitting)
- How to handle the last byte, if the values' bits does not fill it? (bit-padding)
- How to do all of the above fast and with low memory footprint? (performance)

Fortunately, there are some convineint libraries to do bit-packing, and `bitstring` is one such pure Python module.

- Homepage: <https://github.com/scott-griffiths/bitstring> (or <https://pypi.org/project/bitstring/>)
- can be installed using command: `pip install bitstring`

This program shows the basic usage of `bitstring` module, simply run it with `python demoBitString.py`.

For detailed information on `bitstring`, see its documentation.

[NOTE] This program is intended for use in course, Principle of Information and Coding Theory.
"""

import bitstring
from bitstring import Bits, BitStream

__author__ = "Guo, Jiangling"
__email__ = "tguojiangling@jnu.edu.cn"
__version__ = "20201125.1416"

def demo1():
    """Demonstrate basic usage of BitStream.

    The following figure illustrates how the values are packed into bit-stream in this demo.

    data type  | uint:3 |   uint:4  | uint:3 |int:2|
    value      |    5   |     2     |    6   |  -1 |
               |--------|-----------|--------|-----|--padding--|
    bit-stream | 1  0  1  0  0  1  0  1  1  0  1  1  0  0  0  0|
               |-----------------------|-----------------------|
    bytes      |         byte-1        |         byte-2        |

    [NOTE] Many values are hardcoded for ease of understanding.
    """

    print('##########')
    print('# demo1 - basic usage')
    print('##########')

    # Construct a BitStream by appending values to it in various ways.
    A = BitStream()
    A.append(Bits(uint=5, length=3))    # 3-bit-uint of 5
    A.append('uint:4=2')                # 4-bit-uint of 2
    A.append('0b110')                   # 3-bit-uint of 6
    A += Bits(int=-1, length=2)         # 2-bit-int of -1

    # Write the BitStream to a file.
    FILE_NAME = '_tmp.demo1.dat'
    with open(FILE_NAME, 'wb') as out_file:
        A.tofile(out_file)

    A_bytes = A.tobytes()
    print('A is a BitStream')
    print('  packed from: 5 (uint:3), 2 (uint:4), 6 (uint:3), -1 (int:2)')
    print('      as bits: %s (%d bits)' % (A.bin, A.length))
    print('     as bytes: %s (%d bytes)' % (A_bytes.hex(), len(A_bytes)))
    print('     saved to: %s' % (FILE_NAME))
    print('')

    # Read the BitStream from the file.
    B = BitStream(filename=FILE_NAME)

    B_bytes = B.tobytes()
    print('B is a BitStream')
    print('  read from: %s' % (FILE_NAME))
    print('    as bits: %s (%d bits. It has more bits than A!)' % (B.bin, B.length))
    print('   as bytes: %s (%d bytes)' % (B_bytes.hex(), len(B_bytes)))
    print('')
    
    print('Read data from B consecutively')
    print("  B.read('uint:3'): %d" % (B.read('uint:3')))
    print("  B.read('uint:4'): %d" % (B.read('uint:4')))
    print("  B.read('uint:3'): %d" % (B.read('uint:3')))
    print("  B.read('uint:2'): %d (intentionally wrong interpretation)" % (B.read('uint:2')))
    print("       B.bitpos is: %d" % (B.bitpos))
    print('')

    B_slice_start = 2
    B_slice_end = 5
    B_slice = B[B_slice_start:B_slice_end]
    print('B[%s:%s] is a slice of B' % (B_slice_start, B_slice_end))
    print('   as bin: %s' % (B_slice.bin))
    print('  as uint: %d' % (B_slice.uint))
    print('   as int: %d' % (B_slice.int))
    print(' B.bitpos: %d (slicing does not change bitpos)' % (B.bitpos))
    print('')

def demo2():
    """Demonstrate packing and unpacking a list with fixed bit-length per element."""

    print('##########')
    print('# demo2 - pack & unpack')
    print('##########')

    # Common values shared implicitly between 'encoder' and 'decoder'.
    # [BEST PRACTICE] Use all uppercase for constant values.
    HEADER_BYTES_VALUE_COUNT = 2    # number of bytes to store the value_count
    HEADER_BYTES_BIT_LEN = 1        # number of bytes to store the bit_len
    HEADER_BYTE_ORDER = 'little'    # endianness of header (see <https://en.wikipedia.org/wiki/Endianness>)
    FILE_NAME = '_tmp.demo2.dat'    # temporary data file for this demo

    # Generate a list of values.
    A_value_count = 7
    A_value = list(range(A_value_count))

    # Pack the values into a BitStream and save it to a file.
    A_bit_len = 3   # number of bits per element in value list
    A = bitstring.pack('%d*uint:%d' % (A_value_count, A_bit_len), *A_value)
    A_bytes = A.tobytes()
    with open(FILE_NAME, 'wb') as out_file:
        # Write header
        out_file.write(A_value_count.to_bytes(HEADER_BYTES_VALUE_COUNT, byteorder=HEADER_BYTE_ORDER))
        out_file.write(A_bit_len.to_bytes(HEADER_BYTES_BIT_LEN, byteorder=HEADER_BYTE_ORDER))

        # Write payload
        out_file.write(A_bytes)

    print('A is a BitStream')
    print('  packed from:', A_value, '(with', A_bit_len, 'bits/element)')
    print('      as bits: %s (%d bits)' % (A.bin, A.length))
    print('     as bytes: %s (%d bytes)' % (A_bytes.hex(), len(A_bytes)))
    print('     saved to: %s (with additional %d bytes of header)' % (FILE_NAME, HEADER_BYTES_VALUE_COUNT+HEADER_BYTES_BIT_LEN))
    print('')

    # Read from the file and unpack it to a list of values.
    with open(FILE_NAME, 'rb') as in_file:
        # Read header
        B_value_count = int.from_bytes(in_file.read(HEADER_BYTES_VALUE_COUNT), byteorder=HEADER_BYTE_ORDER)
        B_bit_len = int.from_bytes(in_file.read(HEADER_BYTES_BIT_LEN), byteorder=HEADER_BYTE_ORDER)
        
        # Read payload
        B_bytes = in_file.read()
    B = BitStream(B_bytes)
    B_value = B.unpack('%d*uint:%d' % (B_value_count, B_bit_len))

    print('B is a BitStream')
    print('    read from: %s (excluding the 3 bytes of header)' % (FILE_NAME))
    print('      as bits: %s (%d bits. It may have more bits than A.)' % (B.bin, B.length))
    print('     as bytes: %s (%d bytes)' % (B_bytes.hex(), len(B_bytes)))
    print('  unpacked to:', B_value, '(with', B_bit_len, 'bits/element)')
    print('')

if __name__ == '__main__':
    demo1()
    demo2()
