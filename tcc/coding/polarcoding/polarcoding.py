"""
Polar coding module

Created on 12/02/2020 11:25

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding.polarfuncs import resolve_node, encode, node_classifier, child_list_maker, list_decode, \
                                              beta_maker


class PolarCoding(object):
    """
    Implements polar encoding and decoding
    """

    def __init__(self, n, k, rel_idx=None, decoding_type='list-sc', list_size=4):
        """

        :param n: Block size N = 2^n
        :param rel_idx: Reliability indexes in descending order
        """

        self.N = 2 ** n
        self.n = n
        self.K = k
        self.rate = self.K / self.N

        self.F = np.array([[1, 0], [1, 1]], dtype=np.uint8)

        self.Fn = self._generate_g()

        # TODO: verify rel_idx after SNR change
        if rel_idx is not None:
            if not np.array_equal(np.sort(rel_idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            rel_idx = np.arange(0, self.N)

        self.rel_idx = np.array(rel_idx, dtype=np.uint64)

        self.information = self.rel_idx[:self.K]
        self.frozen = self.rel_idx[self.K:]

        self.dec_type = decoding_type
        self.list_size = list_size

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
            self.information = obj.information

        def __call__(self, bits):
            """
            Perform polar encoding
            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            bit_vector = np.zeros(self.N, dtype=np.uint8)
            bit_vector[self.information] = bits
            return encode(bit_vector, self.n)

    class Decode(object):
        def __init__(self, obj):
            if obj.dec_type == 'sc':
                self.N = obj.N
                self.n = obj.n
                self.node_sheet = node_classifier(self.n, obj.information, obj.frozen)
                self.child_list = child_list_maker(self.n)
                self.information = obj.information
                self.dec_bits = None

                self.decoder = self.sc_dec

            elif obj.dec_type == 'list-sc':
                self.n = obj.n
                self.list_size = obj.list_size
                self.information = obj.information

                node_sheet = node_classifier(self.n, obj.information, obj.frozen)
                beta_tree, beta_sheet = beta_maker(self.n, node_sheet)
                self.beta_trees = [beta_tree]
                self.beta_sheet = beta_sheet

                self.decoder = self.list_sc_dec

            else:
                raise ValueError('Invalid decoding type: {}'.format(obj.dec_type))

        def __call__(self, llr):
            return self.decoder(llr)

        def sc_dec(self, llr):
            dec_bits = np.zeros(self.N, dtype=np.uint8)

            _ = resolve_node(np.array(llr, dtype=np.float64),
                             self.n,
                             0,
                             dec_bits,
                             self.node_sheet,
                             self.child_list)
            return dec_bits[self.information]

        def list_sc_dec(self, llr):
            dec_bits = list_decode(self.n, self.list_size, np.array(llr, dtype=np.float64),
                                   self.information, self.beta_trees, self.beta_sheet)
            return dec_bits[self.information]
