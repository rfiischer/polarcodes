"""


Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from coding.polarcoding import PolarCoding

n = 10
frames = 1000
pc = PolarCoding(n)

bits = np.random.randint(0, 2, 2 ** n, dtype=np.uint8)

for frame in range(0, frames):
    encoded = pc.encode(bits)
    llr = [1. if value == 0 else -1. for value in encoded]
    pc.decode(llr)
