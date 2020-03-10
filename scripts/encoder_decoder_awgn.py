"""


Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from coding.polarcoding import PolarCoding
from core.awgn import AWGN
from core.constellation import PolarConstellation
from core.mod_demod import Modulator, Demodulator

n = 4
k = 1
frames = 1000000
snr = 1
rng = np.random.RandomState(seed=12465)
awgn = AWGN(1, rng, snr_unit="EsN0_dB")
constellation = PolarConstellation()
mod = Modulator(constellation, 2)
dem = Demodulator(constellation, 'llr_exact', 2)

err_sum = np.zeros(2 ** n)
for i in range(0, 2 ** n):
    for frame in range(0, frames):
        rel = np.concatenate(([i], np.delete(np.arange(0, 16), i)))
        pc = PolarCoding(n, rel_idx=rel)
        bits = np.random.randint(0, 2, k, dtype=np.uint8)
        encoded = pc.encode(bits)
        modulated = mod(encoded)
        noise_symbols = awgn(modulated, snr=snr)
        llr = dem(noise_symbols, variance=awgn.variance)
        decoded = pc.decode(llr)
        err_sum[i] += np.sum(np.bitwise_xor(bits, decoded))

print(err_sum / frames)
