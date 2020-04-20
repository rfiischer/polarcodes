"""


Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding import PolarCoding

n = 10
frames = 1000
pc = PolarCoding(n)

for frame in range(0, frames):
    bits = np.random.randint(0, 2, 512, dtype=np.uint8)
    encoded = pc.encode(bits)
    llr = [5 if value == 0 else -5 for value in encoded]
    decoded = pc.decode(llr)
    assert np.all(decoded == bits)
