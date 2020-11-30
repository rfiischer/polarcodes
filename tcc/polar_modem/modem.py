"""


Created on 10/03/2020 20:00

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.core.utils.mod_demod import Modulator, Demodulator
from tcc.core.utils.constellation import PolarConstellation
from tcc.coding.polarcoding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import construction
from tcc.coding.crc import CRC
from tcc.core.utils.awgn import AWGN
from tcc.coding.interleaving import Interleaver


class Modem:
    def __init__(self, parameters, rng):
        # Parameters
        self.K = parameters.k
        self.n = parameters.n
        self._snr = parameters.base_design_snr
        self.construction_method = parameters.construction_method
        self.frozen_design = parameters.frozen_design
        self.bits_p_symbol = parameters.bits_p_symbol
        self.snr_unit = parameters.snr_unit

        # Objects
        self.rng = rng
        self.mod = Modulator(PolarConstellation(), parameters.bits_p_symbol)
        self.dem = Demodulator(PolarConstellation(), parameters.demod_type, parameters.bits_p_symbol)

        if parameters.decoding_algorithm in ['scl-crc', 'sscl-crc', 'sscl-spc-crc']:
            if parameters.crc_id:
                self.crc = CRC(parameters.crc_id)
                self.tx_size = self.K - self.crc.len_bit
                self.rate = self.tx_size / 2 ** self.n

            else:
                raise ValueError("A CRC ID must be provided.")

        else:
            self.crc = None
            self.tx_size = self.K
            self.rate = self.tx_size / 2 ** self.n

        base_design_snr = AWGN.unit_conversion(parameters.base_design_snr, parameters.bits_p_symbol,
                                               self.rate, parameters.snr_unit,
                                               'EsN0_dB')
        rel_idx = construction(parameters.construction_method, parameters.n, base_design_snr)

        self.polar = PolarCoding(parameters.n, self.K, rel_idx,
                                 decoding_algorithm=parameters.decoding_algorithm,
                                 list_size=parameters.list_size,
                                 encoding_mode=parameters.encoding_mode,
                                 implementation_type=parameters.implementation_type,
                                 crc=self.crc)

        if parameters.interleaver_columns != 0:
            self.interleaver = Interleaver(columns=parameters.interleaver_columns)
            self.inter = True

        else:
            self.interleaver = None
            self.inter = False

        # Initialization
        self.txbits = None
        self.rxbits = None

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, value):
        self._snr = value
        if not self.frozen_design:
            design_snr = AWGN.unit_conversion(self._snr, self.bits_p_symbol,
                                              self.rate, self.snr_unit,
                                              'EsN0_dB')
            rel_idx = construction(self.construction_method, self.n, design_snr)
            self.polar.rel_idx = rel_idx

    def tx(self):
        self.txbits = self.rng.integers(0, 2, self.tx_size, dtype=np.uint8)
        coded = self.polar.encode(self.txbits)
        if self.inter:
            coded = self.interleaver.interleave(coded)
        modulated = self.mod(coded)
        return modulated

    def rx(self, signal, variance):
        demodulated = self.dem(signal, variance)
        if self.inter:
            demodulated = self.interleaver.deinterleave(demodulated)
        rxbits = self.polar.decode(demodulated)
        return rxbits

    def compute_errors(self, rxbits):
        errors = np.bitwise_xor(self.txbits, rxbits)
        num_bit_errors = np.sum(errors)
        num_frame_errors = 1 if num_bit_errors != 0 else 0

        return num_bit_errors, num_frame_errors
