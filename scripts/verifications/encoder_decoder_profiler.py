"""
Profile of the encoding/decoding operation on noiseless channel

Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import bhattacharyya

n = 12
k = 2048
esn0 = 10
frames = 10
list_size = 1
decoding_type = 'sscl-spc'
encoding_mode = 'systematic'
implementation_type = 'pythran'
pc = PolarCoding(n, k, bhattacharyya(n, esn0)[0], decoding_algorithm=decoding_type, list_size=list_size,
                 encoding_mode=encoding_mode, implementation_type=implementation_type)

for frame in range(0, frames):
    bits = np.random.randint(0, 2, k, dtype=np.uint8)
    encoded = pc.encode(bits)
    llr = np.array([5.0 if value == 0 else -5.0 for value in encoded])
    decoded = pc.decode(llr)
    assert np.all(decoded == bits)
