"""
Polar coding module

Created on 12/02/2020 11:25

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


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

        self.F = np.array([[1, 0], [1, 1]])

        self.Fn = self._generate_g()

        if rel_idx is not None:
            if not np.array_equal(np.sort(rel_idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            rel_idx = np.arange(0, self.N)

        self.rel_idx = rel_idx

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
            self.Fn = obj.Fn
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

            bit_vector = np.zeros(self.N, dtype=int)
            bit_vector[self.rel_idx[:bits.size]] = bits
            self.K = bits.size
            self.rate = self.K / self.N
            self.information = self.rel_idx[:bits.size]
            return np.mod(np.matmul(bit_vector, self.Fn), 2)

    class Decode(object):
        def __init__(self, obj):
            self.encode = obj.encode
            self.N = obj.N
            self.dec_bits = None

        def __call__(self, llr):
            self.dec_bits = np.zeros(self.N, dtype=int)
            _ = self._compute_node(llr, self.N, 0)
            return self.dec_bits[self.encode.information]

        @staticmethod
        def _fl(a, b):
            return np.log((1 + np.exp(a + b)) / (np.exp(a) + np.exp(b)))

        @staticmethod
        def _fr(a, b, c):
            return b + (1 - 2 * c) * a

        def _alpha_left(self, alphas):
            out_size = len(alphas) // 2
            alphas_out = np.zeros(out_size)
            for i in range(0, out_size):
                alphas_out[i] = self._fl(alphas[i], alphas[i + out_size])

            return alphas_out

        def _alpha_right(self, alphas, betas):
            out_size = len(alphas) // 2
            alphas_out = np.zeros(out_size)
            for i in range(0, out_size):
                alphas_out[i] = self._fr(alphas[i], alphas[i + out_size], betas[i])

            return alphas_out

        @staticmethod
        def _betas(betas_left, betas_right):
            betas_size = len(betas_left)
            out_size = 2 * betas_size
            betas_out = np.zeros(out_size, dtype=int)
            for i in range(0, betas_size):
                betas_out[i] = betas_left[i] ^ betas_right[i]
                betas_out[i + betas_size] = betas_right[i]

            return betas_out

        def _compute_node(self, alphas, level, counter):
            """

            :param alphas: LLR's
            :param level: tree level
            :param counter: leaf counter
            :return: betas
            """

            if len(alphas) > 1:
                alpha_l = self._alpha_left(alphas)
                beta_l = self._compute_node(alpha_l, level // 2, counter)
                alpha_r = self._alpha_right(alphas, beta_l)
                beta_r = self._compute_node(alpha_r, level // 2, counter + level // 2)
                beta = self._betas(beta_l, beta_r)

            else:
                if counter in self.encode.information:
                    beta = np.array([0]) if alphas > 0 else np.array([1])
                    self.dec_bits[counter] = beta[0]

                else:
                    beta = np.array([0])

            return beta
