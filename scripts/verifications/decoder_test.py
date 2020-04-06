"""


Created on 17/02/2020 14:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding

permutation = [7, 6, 5, 3, 4, 2, 1, 0]
pc = PolarCoding(3, permutation)

for K in range(1, 9):
    for i in range(0, 2 ** K):
        bits = np.unpackbits(np.array([i], dtype=np.uint8))[8 - K:]
        encoded = pc.encode(bits)
        llr = [1.5 if value == 0 else -1.5 for value in encoded]
        decoded = pc.decode(llr)
        print(bits)
        print(decoded)
        print('\n')
        assert np.all(decoded == bits)
