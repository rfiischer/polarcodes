"""
Compare the output of different decoders

Created on 03/07/2020 11:50

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import bhattacharyya
from tcc.core.utils.awgn import AWGN
from tcc.core.utils.mod_demod import Modulator, Demodulator
from tcc.core.utils.constellation import PolarConstellation


# Larger test with R = 1/2
n = 12
K = 2048
esn0 = 0
pc_ssc = PolarCoding(n, K, bhattacharyya(n, esn0)[0], 'ssc')
pc_fssc = PolarCoding(n, K, bhattacharyya(n, esn0)[0], 'fast-ssc')

rng = np.random.RandomState(120987)
const = PolarConstellation()
mod = Modulator(const)
dem = Demodulator(const)
awgn = AWGN(1, rng, snr_unit="EsN0_dB")

larger_errors = 0
reps = 10000
for i in range(reps):
    print(f'n: {n}, rep: {i}')
    bits = rng.randint(0, 2, K)
    encoded = pc_ssc.encode(bits)

    modulated = mod(encoded)
    received = awgn(modulated, snr=esn0)
    demodulated = dem(received)

    decoded_ssc = pc_ssc.decode(demodulated)
    decoded_fssc = pc_fssc.decode(demodulated)
    if not np.all(decoded_ssc == decoded_fssc):
        print("ERROR!")
        print('\n')
        larger_errors += 1

    else:
        print('No errors.\n')

print("Total errors: {}".format(larger_errors))
