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

    def __init__(self, n, k, rel_idx=None, decoding_algorithm='ssc', list_size=None, encoding_mode='systematic',
                 implementation_type='pythran', crc=None):
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

        self.dec_type = decoding_algorithm
        self.list_size = list_size
        self.enc_mode = encoding_mode
        self.imp_type = implementation_type
        self.crc = crc

        if rel_idx is not None:
            if not np.array_equal(np.sort(rel_idx), np.arange(0, self.N)):
                raise ValueError("Invalid frozen bits indexes: rel_idx should be a permutation vector of size 2^n")

        else:
            rel_idx = np.arange(0, self.N)

        self._rel_idx = np.array(rel_idx, dtype=np.uint32)

        self.information = self._rel_idx[:self.K]
        self.frozen = self._rel_idx[self.K:]

        self.encode = PolarCoding.Encode(self)
        self.decode = PolarCoding.Decode(self)

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

        self.encode = PolarCoding.Encode(self)
        self.decode = PolarCoding.Decode(self)

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

            if obj.enc_mode == "systematic":
                self.enc = self.systematic

            elif obj.enc_mode == "non-systematic":
                self.enc = self.non_systematic

            else:
                raise ValueError("The encoding mode should be 'systematic' or 'non-systematic'")

            if obj.imp_type == 'python':
                from .polarfuncs.polarfuncs import encode

                self.encode = encode

            elif obj.imp_type == 'pythran' or obj.imp_type == 'hybrid':
                try:
                    from .polarfuncs.polarfuncs_compiled import encode

                    self.encode = encode

                except ImportError:
                    raise ImportError("Was not able to load the compiled encoder.")

            else:
                raise ValueError("Invalid implementation type: {}".format(obj.imp_type))

            self.crc = obj.crc

        def __call__(self, bits):
            """
            Perform polar encoding
            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            if self.crc is not None:
                crc = self.crc(bits)
                bits = np.concatenate((bits, crc))

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
            return self.encode(bit_vector, self.n)

        def systematic(self, bits):
            """
            Perform systematic polar encoding

            :param bits: integer unidimensional ndarray of 0's and 1's
            :return: b * Fn
            """

            # TODO: pass these operations to inside 'encode'
            bit_vector = np.zeros(self.N, dtype=np.uint8)
            bit_vector[self.information] = bits
            first_encoded = self.encode(bit_vector, self.n)

            first_encoded[self.frozen] = 0

            return self.encode(first_encoded, self.n)

    class Decode(object):
        def __init__(self, obj):

            from .polarfuncs.polarfuncs import fast_ssc_scheduler, sscl_spc_scheduler, ssc_scheduler

            if obj.imp_type == 'python':
                from .polarfuncs.polarfuncs import (
                    address_list_factory,
                    ssc_node_classifier,
                    fast_ssc_node_classifier,
                    encode,
                    ssc_decode,
                    fast_ssc_decode,
                    sscl_spc_decode
                )

                self.encode = encode
                self.ssc_decode = ssc_decode
                self.fast_ssc_decode = fast_ssc_decode
                self.sscl_spc_decode = sscl_spc_decode

            elif obj.imp_type == 'pythran':
                try:
                    from .polarfuncs.polarfuncs_compiled import (
                        address_list_factory,
                        ssc_node_classifier,
                        fast_ssc_node_classifier,
                        encode,
                        ssc_decode,
                        fast_ssc_decode,
                        sscl_spc_decode
                    )

                    self.encode = encode
                    self.ssc_decode = ssc_decode
                    self.fast_ssc_decode = fast_ssc_decode
                    self.sscl_spc_decode = sscl_spc_decode

                except ImportError:
                    raise ImportError("Was not able to load the compiled encoder.")

            elif obj.imp_type == 'hybrid':
                try:
                    from .polarfuncs.polarfuncs_compiled import (
                        address_list_factory,
                        ssc_node_classifier,
                        fast_ssc_node_classifier,
                        encode,
                        ssc_decode,
                        fast_ssc_decode,
                        sscl_spc_decode_hybrid
                    )

                    self.encode = encode
                    self.ssc_decode = ssc_decode
                    self.fast_ssc_decode = fast_ssc_decode
                    self.sscl_spc_decode = sscl_spc_decode_hybrid

                except ImportError:
                    raise ImportError("Was not able to load the compiled encoder.")

            else:
                raise ValueError("Invalid implementation type: {}".format(obj.imp_type))

            self.n = np.uint8(obj.n)
            self.address_list = address_list_factory(self.n).astype(np.uint32)
            self.information = obj.information
            self.enc_mode = obj.enc_mode

            if obj.dec_type == 'ssc':
                self.node_sheet = ssc_node_classifier(self.n, obj.information, obj.frozen)
                self.tasks = ssc_scheduler(self.n, self.node_sheet)

                if self.enc_mode == 'systematic':
                    self.decoder = self.ssc_dec_sys

                else:
                    self.decoder = self.ssc_dec

            elif obj.dec_type == 'fast-ssc':
                self.node_sheet = fast_ssc_node_classifier(self.n, obj.information, obj.frozen)
                self.tasks = fast_ssc_scheduler(self.n, self.node_sheet)

                if self.enc_mode == 'systematic':
                    self.decoder = self.fast_ssc_dec_sys

                else:
                    self.decoder = self.fast_ssc_dec

            elif obj.dec_type in ['sscl-spc', 'sscl-spc-crc']:
                self.node_sheet = fast_ssc_node_classifier(self.n, obj.information, obj.frozen)

                if obj.list_size is None:
                    raise ValueError("Please provide a list size for sscl-spc/spc-crc modes.")

                if obj.dec_type == 'sscl-spc-crc' and obj.crc is None:
                    raise ValueError("Please provide a CRC on sscl-spc-crc mode.")

                self.crc = obj.crc
                self.list_size = np.uint8(obj.list_size)
                self.tasks = sscl_spc_scheduler(self.n, self.node_sheet)

                if self.enc_mode == 'systematic':
                    self.decoder = self.sscl_spc_dec_sys

                else:
                    self.decoder = self.sscl_spc_dec

            else:
                raise ValueError('Invalid decoding type: {}'.format(obj.dec_type))

        def __call__(self, llr):
            return self.decoder(llr)

        def ssc_dec_sys(self, llr):
            dec_bits = self.ssc_decode(self.n, llr, self.tasks, self.address_list)
            return dec_bits[self.information]

        def fast_ssc_dec_sys(self, llr):
            dec_bits = self.fast_ssc_decode(self.n, llr, self.tasks, self.address_list)
            return dec_bits[self.information]

        def sscl_spc_dec_sys(self, llr):
            betas, metrics, n_paths = self.sscl_spc_decode(self.n, self.list_size, llr, self.tasks, self.address_list)

            if self.crc is None:
                dec_bits = betas[0, :2 ** self.n]
                output = dec_bits[self.information]

            else:
                valid_paths = []
                code_word = []
                for path in range(n_paths):
                    code_w = betas[path, :2 ** self.n]
                    bits = code_w[self.information]
                    rec_crc = bits[-self.crc.len_bit:]
                    obt_crc = self.crc(bits[:-self.crc.len_bit])

                    code_word.append(bits)
                    if np.all(rec_crc == obt_crc):
                        valid_paths.append(path)

                # TODO: replace argsort with argmax
                if valid_paths:
                    order = np.argsort(metrics[valid_paths])
                    final_path = valid_paths[order[0]]

                else:
                    order = np.argsort(metrics[:n_paths])
                    final_path = order[0]

                output = code_word[final_path][:-self.crc.len_bit]

            return output

        def ssc_dec(self, llr):
            dec_bits = self.ssc_decode(self.n, llr, self.tasks, self.address_list)
            dec_bits = self.encode(dec_bits, self.n)
            return dec_bits[self.information]

        def fast_ssc_dec(self, llr):
            dec_bits = self.fast_ssc_decode(self.n, llr, self.tasks, self.address_list)
            dec_bits = self.encode(dec_bits, self.n)
            return dec_bits[self.information]

        def sscl_spc_dec(self, llr):
            betas, metrics, n_paths = self.sscl_spc_decode(self.n, self.list_size, llr, self.tasks, self.address_list)

            if self.crc is None:
                dec_bits = betas[0, :2 ** self.n]
                dec_bits = self.encode(dec_bits, self.n)
                output = dec_bits[self.information]

            else:
                valid_paths = []
                code_word = []
                for path in range(n_paths):
                    code_w = betas[path, :2 ** self.n]
                    code_w = self.encode(code_w, self.n)
                    bits = code_w[self.information]
                    rec_crc = bits[-self.crc.len_bit:]
                    obt_crc = self.crc(bits[:-self.crc.len_bit])

                    code_word.append(bits)
                    if np.all(rec_crc == obt_crc):
                        valid_paths.append(path)

                if valid_paths:
                    order = np.argsort(metrics[valid_paths])
                    final_path = valid_paths[order[0]]

                else:
                    order = np.argsort(metrics[:n_paths])
                    final_path = order[0]

                output = code_word[final_path][:-self.crc.len_bit]

            return output
