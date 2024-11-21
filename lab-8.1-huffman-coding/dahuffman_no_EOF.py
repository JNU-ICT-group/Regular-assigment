import dahuffman

class HuffmanCodec(dahuffman.HuffmanCodec):
    """A wrapper class of `dahuffman.HuffmanCodec` for NOT using EOF symbol.

    `dahuffman` adds an EOF symbol to provide auto end-of-data-stream detection. However, it significantly reduces compression ratio in many cases, and has much less error tolerance.

    This class provides a no-EOF alternative. It is a drop-in replacement for `dahuffman.HuffmanCodec`, but now it is user's responsibility to handle end-of-data-stream detection.
    
    A simple and efficient way is to send the length of the source message to the decoder (as header of the encoded data stream, e.g.), then the decoder just decode up to the specified length.

    The following is a basic usage example.

    ```python
    from dahuffman_no_EOF import HuffmanCodec
    codec = HuffmanCodec.from_frequencies({'e': 100, 'n':20, 'x':1, 'i': 40, 'q':3})
    source = 'exeneeeexniqneieinie'
    encoded = codec.encode(source)
    decoded = codec.decode(encoded)[:len(source)]
    ```
    """

    def __init__(self, code_table, concat=list, check=True, eof=None):
        # Set EOF symbol to be the first symbol in `code_table`, so that encode() `dahuffman` will not fail. 
        eof = next(iter(code_table.keys()))
        super().__init__(code_table, concat=concat, check=check, eof=eof)

    @classmethod
    def from_frequencies(cls, frequencies, concat=None):
        # Set EOF symbol to be the first symbol in `frequencies`, so that `dahuffman` will not add a new EOF symbol while building a Huffman tree. 
        eof = next(iter(frequencies.keys()))
        return super().from_frequencies(frequencies, concat, eof=eof)

    def decode(self, data, concat=None):
        # Temporarily set EOF symbol to `None`, so that `dahuffman` will decode till the end of the `data`. 
        eof = self._eof
        self._eof = None

        decoded = super().decode(data, concat=concat)

        # Restore the EOF symbol, otherwise calling encode() again will fail.
        self._eof = eof
        return decoded
