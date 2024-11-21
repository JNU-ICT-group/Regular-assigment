import argparse
import numpy as np
from exampleSourceCoder import encode, decode


def main():
    parser = argparse.ArgumentParser(description="Lossless source coder for encoding and decoding.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to run (encode or decode)')

    # Encode sub-command
    parser_encode = subparsers.add_parser('encode', help='Encode a source file')
    parser_encode.add_argument('PMF', type=str, help='Path to probability mass function CSV file')
    parser_encode.add_argument('INPUT', type=str, help='Path to the encoder input file')
    parser_encode.add_argument('OUTPUT', type=str, help='Path to the encoder output file')

    # Decode sub-command
    parser_decode = subparsers.add_parser('decode', help='Decode an encoded file')
    parser_decode.add_argument('INPUT', type=str, help='Path to the decoder input file')
    parser_decode.add_argument('OUTPUT', type=str, help='Path to the decoder output file')

    args = parser.parse_args()

    # Execute based on sub-command
    if args.command == 'encode':
        print('Encoding...')
        (source_len, encoded_len) = encode(args.PMF, args.INPUT, args.OUTPUT)
        print(f'Source length: {source_len} bytes')
        print(f'Encoded length: {encoded_len} bytes')
        print(f'Compression ratio: {source_len / encoded_len:.2f}')

    elif args.command == 'decode':
        print('Decoding...')
        (encoded_len, decoded_len) = decode(args.INPUT, args.OUTPUT)
        print(f'Encoded length: {encoded_len} bytes')
        print(f'Decoded length: {decoded_len} bytes')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
