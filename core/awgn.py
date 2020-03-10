import numpy as np


class AWGN(object):
    """Class responsible for additive white gaussian noise."""

    def __init__(self, bits_p_symbol, rng: np.random.RandomState, num_samp_symbol=1, snr_unit="EbN0_dB",
                 efficiency_factor=1):
        """ AWGN object initialization

        :param snr_unit: unit of the specified noise figure
        :param bits_p_symbol: Number of user bits per symbol (modulation and coding efficiency)
        :param num_samp_symbol: Oversampling factor
        :param rng: Random Number Generator
        :param efficiency_factor: Multiplication of external efficiencies (coding efficiency, signaling efficiency)
        """

        self.bits_p_symbol = bits_p_symbol
        self.snr = None
        self.signal_power = None
        self.variance = None
        self.rng = rng
        self.num_samp_symbol = num_samp_symbol
        self.efficiency_factor = efficiency_factor

        if snr_unit in ["EbN0_dB", "EsN0_dB"]:
            self.snr_unit = snr_unit

        else:
            raise ValueError('Invalid SNR unit: {}'.format(snr_unit))

    def __call__(self, signal, **kwargs):
        """Adds AWGW noise to the input symbols.

        If signal_power is specified, the mean bit energy is computed from it, considering signal_power as
        being the same as Es, the symbol energy. If not, the mean bit energy is taken from input signal power.
        Noise variance can be specified from the argument list, or evaluated from ebn0 in decibels.

        In the case the signal_power is not specified, it is assumed that the symbol transmission rate is 1/k;
        that is, the spacing between samples is one unit of time.

        :param signal: input signal. If num_samp_symbol == 1, correspond to symbols sent.
        :param kwargs:
        : keyword arguments
            :variance the noise variance
            :snr signal to noise ratio value (EbN0, EsN0)
        :return: input with added awgn noise
        """

        # Number of samples to take average on
        num_samples = len(signal)

        # Compute the modulated symbol energy Es
        if 'signal_power' in kwargs.keys():
            self.signal_power = kwargs['signal_power']
            es = self.signal_power

        else:
            self.signal_power = np.sum(np.abs(signal) ** 2) / num_samples

            # Psignal = Rs * Es = 1 / k * Es => Es = k * Psignal
            es = self.num_samp_symbol * self.signal_power

        # Bit energy
        eb = es / (self.bits_p_symbol * self.efficiency_factor)

        if 'variance' in kwargs.keys():
            self.variance = kwargs['variance']

        elif 'snr' in kwargs.keys():
            self.snr = kwargs['snr']

            # var = No / 2
            if self.snr_unit == "EbN0_dB":
                ebn0dec = 10 ** (self.snr / 10)
                self.variance = eb / (2 * ebn0dec)

            elif self.snr_unit == "EsN0_dB":
                esn0dec = 10 ** (self.snr / 10)
                self.variance = es / (2 * esn0dec)

        else:
            raise ValueError('Either the SNR or variance must be set')

        std_dev = np.sqrt(self.variance)
        n = std_dev * (self.rng.randn(num_samples) + 1j * self.rng.randn(num_samples))

        return signal + n
