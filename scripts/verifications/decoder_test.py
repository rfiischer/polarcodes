"""


Created on 17/02/2020 14:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import bhattacharyya

# Perform noiseless tests on polar encoding and decoding

# Simple SC test
sc_errors = 0
permutation = [7, 6, 5, 3, 4, 2, 1, 0]
for K in range(1, 9):
    for i in range(0, 2 ** K):
        print(f'K: {K}, bits: {i}')
        pc = PolarCoding(3, K, permutation)
        bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('\n')
            sc_errors += 1
        else:
            print('No errors.\n')

# Simple list SC test
lsc_errors = 0
for K in range(1, 9):
    for i in range(0, 2 ** K):
        print(f'K: {K}, bits: {i}')
        pc = PolarCoding(3, K, permutation, 'list-sc', 4)
        bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('\n')
            lsc_errors += 1
        else:
            print('No errors.\n')

# Larger SC test with R = 1/2
larger_sc_errors = 0
reps = 1000
for n in range(1, 10):
    for i in range(reps):
        print(f'n: {n}, rep: {i}')
        K = 2 ** (n - 1)
        esn0 = 10
        pc = PolarCoding(n, K, bhattacharyya(n, esn0)[0])
        bits = np.random.randint(0, 2, K)
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('\n')
            larger_sc_errors += 1

        else:
            print('No errors.\n')

# Larger list SC test with R = 1/2
larger_list_sc_errors = 0
reps = 1000
for n in range(1, 10):
    for i in range(reps):
        print(f'n: {n}, rep: {i}')
        K = 2 ** (n - 1)
        esn0 = 10
        pc = PolarCoding(n, K, bhattacharyya(n, esn0)[0], 'list-sc', 4)
        bits = np.random.randint(0, 2, K)
        encoded = pc.encode(bits)
        llr = np.array([1.5 if value == 0 else -1.5 for value in encoded])
        decoded = pc.decode(llr)
        if not np.all(decoded == bits):
            print(bits)
            print(decoded)
            print('\n')
            larger_list_sc_errors += 1

        else:
            print('No errors.\n')

print(f'Total SC errors: {sc_errors}\n'
      f'Total List-SC errors: {lsc_errors}\n'
      f'Total large test SC errors: {larger_sc_errors}\n'
      f'Total large test list SC errors: {larger_list_sc_errors}')
