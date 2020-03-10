"""Contains the Modulator and Demodulator classes."""

import numpy as np

from core.int_bit import int2bit_constructor, bit2int_constructor


class Modulator(object):
    """Creates the modulator object."""

    def __init__(self, constellation, order=4, spread_factor=1):
        """Initialize object.

        :param constellation: constellation object
        :param order: modulation order, namely
            - 2: pi/2-BPSK
            - 4: QPSK
            - 8: 8PSK
            - 16: 16APSK
        """

        if constellation.phase_func[order] is not None:
            self.phase = True
            self.phase_shift = constellation.phase_func[order]

        else:
            self.phase = False

        self.constellation = constellation.mod_schemes[order]()
        self.order = order
        self.bits_p_symbol = int(np.log2(order))
        self.spread_factor = spread_factor
        self.bit2int = bit2int_constructor(self.bits_p_symbol)

    def __call__(self, stream):
        """Modulate the bit sequence in stream.

        The MSB should be the first element of the input array

        *NOTE: for the pi/2-BPSK constellation, phase shifts may be observed on multidimensional inputs,
        since the input is flattened and treated as a unidimensional stream before modulating.

        :stream: nympy array with '0' and '1'
        :returns: numpy complex array
        """

        # Flattens stream for easier manipulation
        original_shape = stream.shape
        stream = stream.flatten()

        # Each column inside tuple(...) is a group of bits_p_symbol bits that will be mapped;
        #   order='F' ensures that the reshaping will be column-wise
        # Note that array[[a0, b0, c0],[a1, b1, c1],[a2, b2, c2]] = [array[a0, a1, a2], ..., array[c0, c1, c2]]
        symbolsindex = self.bit2int[tuple(stream.reshape((self.bits_p_symbol, -1), order='F'))]

        # Map to modulation scheme using symbolsindex
        mapped = self.constellation[symbolsindex]

        # Apply spreading
        spread = np.repeat(mapped, self.spread_factor)

        # Apply phase shift
        # Wrong shift may be applied if the stream dimension is other than one
        if self.phase:
            phase_shift = self.phase_shift(len(spread))
            spread = spread * phase_shift

        # Creates new shape tuple to reajust only last dimension
        new_shape = original_shape[:-1] + (-1, )

        # Returns output with same dimensions as input
        return np.reshape(spread, new_shape)


class Demodulator(object):

    def __init__(self, constellation, demod_type='max-log', order=4, spread_factor=1):
        """Initialize object.

        :param demod_type:
            - "max-log" Approximates LLR with Max-Log approach, without implementing decision regions
            - "llr_exact"
            - "bits" Hard demodulation
        :param constellation: constellation object
        :param order: modulation order, namely
            - 2: pi/2-BPSK
            - 4: QPSK
            - 8: 8PSK
            - 16: 16APSK
        """

        if constellation.phase_func[order] is not None:
            self.phase = True
            self.phase_shift = constellation.phase_func[order]

        else:
            self.phase = False

        self.constellation = constellation.mod_schemes[order]()
        self.order = order
        self.bits_p_symbol = int(np.log2(order))
        self.spread_factor = spread_factor
        self.int2bit = int2bit_constructor(self.bits_p_symbol)
        self.demod_type = demod_type

    def __call__(self, symbols, variance=1):
        """Demodulate the symbol sequence in 'symbols'.

        *NOTE: for the pi/2-BPSK constellation, phase shifts may be observed on multidimensional inputs,
        since the input is flattened and treated as a unidimensional stream before modulating.

        :symbols: complex nympy.ndarray
        :variance: variance for LLR computation
        :returns: LLR or bits
        """

        # Flatten and preserve original shape
        stream_leng = symbols.size
        unspread_leng = stream_leng // self.spread_factor
        original_shape = symbols.shape
        symbols = symbols.flatten()

        # Apply phase shift
        if self.phase:
            phase_shift = self.phase_shift(stream_leng)
            symbols = symbols * np.conj(phase_shift)

        # IDEA: instead of using distance, hardcode decision regions for 'bits' decoding
        if self.demod_type == 'bits':
            # Hard demodulation using decision regions with equal symbol probability
            dist = np.abs(np.subtract.outer(symbols, self.constellation)) ** 2

            # Sum distances
            dist = np.reshape(dist, (unspread_leng, self.spread_factor, self.order))
            dist = np.sum(dist, axis=1)

            # Dist is shaped (stream_leng, order), and for each line the minimum is selected
            symbolsindex = np.argmin(dist, axis=-1)

            # Get bits and return output
            demod_output = self.int2bit[symbolsindex].flatten()

        elif self.demod_type == 'max-log':
            # Approximates LLR with Max-Log approach, without implementing decision regions
            # Creates output array
            demod_output = np.empty(self.bits_p_symbol * stream_leng)

            # Gets squared distances to all constellation points
            dist = np.abs(np.subtract.outer(symbols, self.constellation)) ** 2 / (2 * variance)

            if self.order == 2:
                demod_output = dist[:, 1] - dist[:, 0]

            elif self.order == 4:
                # LLR for the MSB
                demod_output[::2] = np.min(dist[:, [2, 3]], axis=1) - np.min(dist[:, [0, 1]], axis=1)

                # LLR for the LSB
                demod_output[1::2] = np.min(dist[:, [1, 3]], axis=1) - np.min(dist[:, [0, 2]], axis=1)

            elif self.order == 8:
                # LLR for the MSB
                demod_output[::3] = np.min(dist[:, [4, 5, 6, 7]], axis=1) - np.min(dist[:, [0, 1, 2, 3]], axis=1)

                demod_output[1::3] = np.min(dist[:, [2, 3, 6, 7]], axis=1) - np.min(dist[:, [0, 1, 4, 5]], axis=1)

                # LLR for the LSB
                demod_output[2::3] = np.min(dist[:, [1, 3, 5, 7]], axis=1) - np.min(dist[:, [0, 2, 4, 6]], axis=1)

            elif self.order == 16:
                # LLR for the MSB
                demod_output[::4] = np.min(dist[:, [8, 9, 10, 11, 12, 13, 14, 15]],
                                           axis=1) - np.min(dist[:, [0, 1, 2, 3, 4, 5, 6, 7]], axis=1)

                demod_output[1::4] = np.min(dist[:, [4, 5, 6, 7, 12, 13, 14, 15]],
                                            axis=1) - np.min(dist[:, [0, 1, 2, 3, 8, 9, 10, 11]], axis=1)

                demod_output[2::4] = np.min(dist[:, [2, 3, 6, 7, 10, 11, 14, 15]],
                                            axis=1) - np.min(dist[:, [0, 1, 4, 5, 8, 9, 12, 13]], axis=1)

                # LLR for the LSB
                demod_output[3::4] = np.min(dist[:, [1, 3, 5, 7, 9, 11, 13, 15]],
                                            axis=1) - np.min(dist[:, [0, 2, 4, 6, 8, 10, 12, 14]], axis=1)

            else:
                raise ValueError("Modulation order not implemented: {}".format(self.order))

            # Sum LLR's
            demod_output = np.reshape(demod_output, (unspread_leng, -1, self.spread_factor))
            demod_output = np.sum(demod_output, axis=2)

        elif self.demod_type == 'llr_exact':
            # Creates output array
            demod_output = np.empty(self.bits_p_symbol * stream_leng)

            # Gets squared distances to all constellation points
            dist = np.abs(np.subtract.outer(symbols, self.constellation)) ** 2 / (2 * variance)

            # Obtain exponentials
            dist = np.exp(-dist)

            if self.order == 2:
                demod_output = np.log(dist[:, 0] / dist[:, 1])

            elif self.order == 4:
                # LLR for the MSB
                demod_output[::2] = np.log(np.sum(dist[:, [0, 1]], axis=1) / np.sum(dist[:, [2, 3]], axis=1))

                # LLR for the LSB
                demod_output[1::2] = np.log(np.sum(dist[:, [0, 2]], axis=1) / np.sum(dist[:, [1, 3]], axis=1))

            elif self.order == 8:
                # LLR for the MSB
                demod_output[::3] = np.log(np.sum(dist[:, [0, 1, 2, 3]], axis=1) /
                                           np.sum(dist[:, [4, 5, 6, 7]], axis=1))

                demod_output[1::3] = np.log(np.sum(dist[:, [0, 1, 4, 5]], axis=1) /
                                            np.sum(dist[:, [2, 3, 6, 7]], axis=1))

                # LLR for the LSB
                demod_output[2::3] = np.log(np.sum(dist[:, [0, 2, 4, 6]], axis=1) /
                                            np.sum(dist[:, [1, 3, 5, 7]], axis=1))

            elif self.order == 16:
                # LLR for the MSB
                demod_output[::4] = np.log(np.sum(dist[:, [0, 1, 2, 3, 4, 5, 6, 7]], axis=1) /
                                           np.sum(dist[:, [8, 9, 10, 11, 12, 13, 14, 15]], axis=1))

                demod_output[1::4] = np.log(np.sum(dist[:, [0, 1, 2, 3, 8, 9, 10, 11]], axis=1) /
                                            np.sum(dist[:, [4, 5, 6, 7, 12, 13, 14, 15]], axis=1))

                demod_output[2::4] = np.log(np.sum(dist[:, [0, 1, 4, 5, 8, 9, 12, 13]], axis=1) /
                                            np.sum(dist[:, [2, 3, 6, 7, 10, 11, 14, 15]], axis=1))

                # LLR for the LSB
                demod_output[3::4] = np.log(np.sum(dist[:, [0, 2, 4, 6, 8, 10, 12, 14]], axis=1) /
                                            np.sum(dist[:, [1, 3, 5, 7, 9, 11, 13, 15]], axis=1))

            else:
                raise ValueError("Modulation order not implemented: {}".format(self.order))

            # Sum LLR's
            demod_output = np.reshape(demod_output, (unspread_leng, -1, self.spread_factor))
            demod_output = np.sum(demod_output, axis=2)

        else:
            raise ValueError("Invalid demodulation type: {}".format(self.demod_type))

        # Computes new shape
        new_shape = original_shape[:-1] + (-1, )

        # Returns output
        return demod_output.reshape(new_shape)
