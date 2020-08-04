"""
Perform noiseless and AWGN tests.

On the noiseless test, every code rate is tested for every message on a certain block size.
On the AWGN case, a certain number of trials are made with the same code rate and SNR.

Created on 17/02/2020 14:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import bhattacharyya

# Perform noiseless tests on polar encoding and decoding


# Polar coding configuration
permutation = [7, 6, 5, 3, 4, 2, 1, 0]
n = 3
decoding_type = 'sscl-spc'
encoding_mode = 'systematic'
list_size = 1
rng = np.random.RandomState(seed=124598)

# Simple test
errors = 0
for K in range(1, 9):
    for i in range(0, 2 ** K):
        print(f'K: {K}, bits: {i}')
        pc = PolarCoding(3, K, permutation, decoding_type, list_size, encoding_mode)
        bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('ERRORS!\n')
            errors += 1
        else:
            print('No errors.\n')


# Larger test with R = 1/2
larger_errors = 0
reps = 1000
esn0 = 10
for n in range(1, 10):
    K = 2 ** (n - 1)
    pc = PolarCoding(n, K, bhattacharyya(n, esn0)[0], decoding_type, list_size, encoding_mode)

    for i in range(reps):
        print(f'n: {n}, rep: {i}')
        bits = rng.randint(0, 2, K)
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('\n')
            larger_errors += 1

        else:
            print('No errors.\n')


print(f'Total simple test errors: {errors}\n'
      f'Total large test errors: {larger_errors}\n')
