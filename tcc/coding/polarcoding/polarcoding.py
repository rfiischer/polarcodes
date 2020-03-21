"""
Polar coding module

Created on 12/02/2020 11:25

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding.polarfuncs import compute_node, encode


class PolarCoding(object):
    """
    Implements polar encoding and decoding
    """

    def __init__(self, n, rel_idx=None):
        """

        :param n: Block size N = 2^n
        :param rel_idx: Reliability indexes in descending order
        """

        self.N = 2 ** n
        self.n = n

        self.F = np.array([[1, 0], [1, 1]], dtype=np.uint8)

        self.Fn = self._generate_g()

        if rel_idx is not None:
            if not np.array_equal(np.sort(rel_idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            rel_idx = np.arange(0, self.N)

        self.rel_idx = np.array(rel_idx, dtype=np.uint64)

        self.encode = self.Encode(self)
        self.decode = self.Decode(self)

    def _generate_g(self):
        """
        Generates F^(kron)n
        :return: n-th Kronecker power of F
        """

        new_matrix = self.F
        for i in range(1, self.n):
            new_matrix = np.kron(self.F, new_matrix)

        return new_matrix

    class Encode(object):
        def __init__(self, obj):
            self.N = obj.N
            self.n = obj.n
            self.rel_idx = obj.rel_idx
            self.rate = None
            self.K = None
            self.information = None

        def __call__(self, bits):
            """
            Perform polar encoding
            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            self.K = bits.size
            self.rate = self.K / self.N
            self.information = self.rel_idx[:bits.size]
            bit_vector = np.zeros(self.N, dtype=np.uint8)
            bit_vector[self.rel_idx[:bits.size]] = bits
            return encode(bit_vector, self.n)

    class Decode(object):
        def __init__(self, obj):
            self.encode = obj.encode
            self.N = obj.N
            self.dec_bits = None

        def __call__(self, llr):
            dec_bits = np.zeros(self.N, dtype=np.uint8)

            _ = compute_node(np.array(llr, dtype=np.float64),
                             self.N,
                             0,
                             self.encode.information,
                             dec_bits)
            return dec_bits[self.encode.information]
