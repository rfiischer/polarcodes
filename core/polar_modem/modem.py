"""


Created on 10/03/2020 20:00

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from core.utils.mod_demod import Modulator, Demodulator
from core.utils.constellation import PolarConstellation
from coding.polarcoding import PolarCoding
from coding.polarcoding.construction import construction


class Modem:
    def __init__(self, parameters, rng):
        # Parameters
        self.K = parameters.k
        self.n = parameters.n
        self.rate = self.K / 2 ** self.n
        self._snr = parameters.base_design_snr
        self.construction_method = parameters.construction_method

        # Objects
        self.rng = rng
        self.mod = Modulator(PolarConstellation(), parameters.bits_p_symbol)
        self.dem = Demodulator(PolarConstellation(), parameters.demod_type, parameters.bits_p_symbol)
        rel_idx = construction(parameters.construction_method, parameters.n, parameters.base_design_snr)
        self.polar = PolarCoding(parameters.n, rel_idx)

        # Initialization
        self.txbits = None
        self.rxbits = None

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, value):
        self._snr = value
        rel_idx = construction(self.construction_method, self.n, self._snr)
        self.polar = PolarCoding(self.n, rel_idx)

    def tx(self):
        self.txbits = self.rng.randint(0, 2, self.K, dtype=np.uint8)
        coded = self.polar.encode(self.txbits)
        modulated = self.mod(coded)
        return modulated

    def rx(self, signal, variance):
        demodulated = self.dem(signal, variance)
        rxbits = self.polar.decode(demodulated)
        return rxbits

    def compute_errors(self, rxbits):
        errors = np.bitwise_xor(self.txbits, rxbits)
        num_bit_errors = np.sum(errors)
        num_frame_errors = 1 if num_bit_errors != 0 else 0

        return num_bit_errors, num_frame_errors
