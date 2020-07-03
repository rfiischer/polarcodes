"""
Polar coding module

Created on 12/02/2020 11:25

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from tcc.coding.polarcoding.polarfuncs import ssc_decode, fast_ssc_decode, list_decode, encode, address_list_factory, \
                                              ssc_node_classifier, fast_ssc_node_classifier, \
                                              ssc_scheduler, fast_ssc_scheduler, list_scheduler


class PolarCoding(object):
    """
    Implements polar encoding and decoding
    """

    def __init__(self, n, k, rel_idx=None, decoding_type='ssc', list_size=None):
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

        self.dec_type = decoding_type
        self.list_size = list_size

        if rel_idx is not None:
            if not np.array_equal(np.sort(rel_idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            rel_idx = np.arange(0, self.N)

        self._rel_idx = np.array(rel_idx, dtype=np.uint32)

        self.information = self._rel_idx[:self.K]
        self.frozen = self._rel_idx[self.K:]

        self.encode = self.Encode(self)
        self.decode = self.Decode(self)

    @property
    def rel_idx(self):
        return self._rel_idx

    @rel_idx.setter
    def rel_idx(self, idx):

        if idx is not None:
            if not np.array_equal(np.sort(idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            idx = np.arange(0, self.N)

        self._rel_idx = np.array(idx, dtype=np.uint32)

        self.information = self._rel_idx[:self.K]
        self.frozen = self._rel_idx[self.K:]

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
            self.frozen = obj.frozen

            self.enc = self.systematic

        def __call__(self, bits):
            """
            Perform polar encoding
            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            return self.enc(bits)

        def non_systematic(self, bits):
            """
            Perform non-systematic polar encoding

            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            # TODO: pass these operations to inside 'encode'
            bit_vector = np.zeros(self.N, dtype=np.uint8)
            bit_vector[self.information] = bits
            return encode(bit_vector, self.n)

        def systematic(self, bits):
            """
            Perform systematic polar encoding

            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            # TODO: pass these operations to inside 'encode'
            bit_vector = np.zeros(self.N, dtype=np.uint8)
            bit_vector[self.information] = bits
            first_encoded = encode(bit_vector, self.n)

            first_encoded[self.frozen] = 0

            return encode(first_encoded, self.n)

    class Decode(object):
        def __init__(self, obj):

            self.N = obj.N
            self.n = np.uint8(obj.n)
            self.address_list = address_list_factory(self.n).astype(np.uint32)
            self.information = obj.information
            self.dec_bits = None

            if obj.dec_type == 'ssc':
                self.node_sheet = ssc_node_classifier(self.n, obj.information, obj.frozen)
                self.tasks = ssc_scheduler(self.n, self.node_sheet)

                self.decoder = self.ssc_dec

            elif obj.dec_type == 'fast-ssc':
                self.node_sheet = fast_ssc_node_classifier(self.n, obj.information, obj.frozen)
                self.tasks = fast_ssc_scheduler(self.n, self.node_sheet)

                self.decoder = self.fast_ssc_dec

            elif obj.dec_type == 'list-sc':
                self.node_sheet = ssc_node_classifier(self.n, obj.information, obj.frozen)
                self.list_size = np.uint8(obj.list_size)
                self.tasks = list_scheduler(self.n, self.node_sheet)

                self.decoder = self.list_dec

            else:
                raise ValueError('Invalid decoding type: {}'.format(obj.dec_type))

        def __call__(self, llr):
            return self.decoder(llr)

        def ssc_dec(self, llr):
            dec_bits = ssc_decode(self.n, llr, self.tasks, self.address_list)
            return dec_bits[self.information]

        def fast_ssc_dec(self, llr):
            dec_bits = fast_ssc_decode(self.n, llr, self.tasks, self.address_list)
            return dec_bits[self.information]

        def list_dec(self, llr):
            dec_bits = list_decode(self.n, self.list_size, llr, self.tasks, self.address_list)
            return dec_bits[self.information]
