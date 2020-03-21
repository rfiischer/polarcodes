"""


Created on 17/02/2020 17:33

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
from time import time, strftime, gmtime

from tcc.coding.polarcoding import PolarCoding
from tcc.core.utils.awgn import AWGN
from tcc.core.utils.constellation import PolarConstellation
from tcc.core.utils.mod_demod import Modulator, Demodulator

n = 4
k = 1
frames = 10
snr = 1 + 10 * np.log10(0.5)
rng = np.random.RandomState(seed=12465)
awgn = AWGN(1, rng, snr_unit="EsN0_dB")
constellation = PolarConstellation()
mod = Modulator(constellation, 1)
dem = Demodulator(constellation, 'llr_exact', 1)

start_time = time()
err_sum = np.zeros(2 ** n)
for i in range(0, 2 ** n):
    print('{}\n'.format(i))
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

tot_time = time() - start_time
print("Total time: {}".format(strftime('%Hhr:%Mmin:%Ssec', gmtime(tot_time))))

print(err_sum / frames)
np.savetxt('results.txt', err_sum / frames)
