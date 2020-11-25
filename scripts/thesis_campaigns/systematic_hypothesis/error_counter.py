"""


Created on 24/11/2020 19:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import dega
from tcc.coding.polarcoding import PolarCoding


n = 5
k = 16
esn0 = 2

const = dega(n, esn0)[0]
pc = PolarCoding(n, k, const, encoding_mode='non-systematic')

message_ones = np.zeros(k + 1, dtype=int)
message_coun = np.zeros(k + 1, dtype=int)

num_bytes = k // 8 + 1
for i in range(0, 2 ** k):
    byte_seq = []
    for j in range(num_bytes - 1, -1, -1):
        byte_seq.append(i // (256 ** j) % 256)

    bits = np.unpackbits(np.array(byte_seq, dtype=np.uint8))[num_bytes * 8 - k:]
    tx_bits = pc.encode(bits)
    rx_bits = tx_bits[pc.information]

    num_bits = np.sum(bits)
    message_coun[num_bits] += 1
    message_ones[num_bits] += np.sum(rx_bits)

rates = np.divide(message_ones, message_coun)

fig, ax = plt.subplots()
ax.plot(np.arange(0, k + 1), rates)
plt.show()
