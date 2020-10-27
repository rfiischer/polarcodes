"""

Created on 13/08/2020 10:11

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import crcmod
import numpy as np


class CRC:

    # [poly, init, rev, xor, byte_length]
    configurations = {
        "crc-8": [0x107, 0x0, False, 0x0, 1],
        "crc-16": [0x18005, 0x0, False, 0x0, 2],
        "crc-32": [0x104C11DB7, 0x0, False, 0x0, 4],
        "crc-16-lte": [0x11021, 0x0, False, 0x0, 2]
    }

    def __init__(self, crc_id):

        try:
            crc_setup = CRC.configurations[crc_id]

        except KeyError:
            raise ValueError("Invalid crc_id.")

        self.crc_len = crc_setup[-1]
        self.len_bit = 8 * self.crc_len
        self.crc_fun = crcmod.mkCrcFun(*crc_setup[:-1])

    def __call__(self, bits):
        bytes_int = np.packbits(bits)
        crc_int = self.crc_fun(bytes_int)
        crc_bytes = crc_int.to_bytes(self.crc_len, 'big')
        crc_array = np.frombuffer(crc_bytes, dtype=np.uint8)
        crc_bits = np.unpackbits(crc_array)

        return crc_bits
