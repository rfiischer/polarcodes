"""


Created on 30/11/2020 01:05

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


class Interleaver:

    def __init__(self, columns=4):
        self.columns = columns

    def interleave(self, bits):
        try:
            reshaped = np.reshape(bits, (-1, self.columns), order='F')

        except ValueError:
            raise ValueError("Number of bits is not multiple of the number of columns.")

        return reshaped.flatten()

    def deinterleave(self, bits):
        try:
            reshaped = np.reshape(bits, (-1, self.columns))

        except ValueError:
            raise ValueError("Number of bits is not multiple of the number of columns.")

        return reshaped.flatten('F')
