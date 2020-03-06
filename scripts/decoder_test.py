"""


Created on 17/02/2020 14:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from coding.polarcoding import PolarCoding

permutation = [0, 1, 2, 4, 3, 5, 6, 7]
pc = PolarCoding(3, permutation)

for K in range(1, 9):
    for i in range(0, 2 ** K):
        bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
        encoded = pc.encode(bits)
        llr = [10 if value == 0 else -10 for value in encoded]
        decoded = pc.decode(llr)
        assert np.all(decoded == bits)
        print(bits)
        print(decoded)
        print('\n')
