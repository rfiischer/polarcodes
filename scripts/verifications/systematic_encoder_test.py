"""
Test the systematic encoding verifying if the information bits are on the codeword

Created on 02/07/2020 16:22

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding


# Polar coding configuration
n = 3
K = 4
permutation = [7, 6, 5, 3, 4, 2, 1, 0]
decoding_type = 'fast-ssc'
list_size = None

errors = 0
for i in range(0, 2 ** K):
    print(f'K: {K}, bits: {i}')
    pc = PolarCoding(3, K, permutation, decoding_type, list_size)
    bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
    encoded = pc.encode(bits)

    if not np.all(encoded[pc.information] == bits):
        print(bits)
        print(encoded)
        print('\n')
        errors += 1

    else:
        print('No errors.\n')

print(f"Total errors: {errors}")
