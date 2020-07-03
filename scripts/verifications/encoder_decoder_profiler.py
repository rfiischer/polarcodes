"""
Profile of the encoding/decoding operation on noiseless channel

Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding

n = 12
k = 2048
frames = 1000
decoding_type = 'fast-ssc'
pc = PolarCoding(n, k, decoding_type=decoding_type)

for frame in range(0, frames):
    bits = np.random.randint(0, 2, k, dtype=np.uint8)
    encoded = pc.encode(bits)
    llr = np.array([5.0 if value == 0 else -5.0 for value in encoded])
    decoded = pc.decode(llr)
    assert np.all(decoded == bits)
