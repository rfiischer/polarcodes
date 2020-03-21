from tcc.core.simulation import Simulation
from tcc.core.utils.awgn import AWGN
from tcc.core.utils.snr_manager import snr_manager_builder, SnrConfig
from tcc.polar_modem.modem import Modem


class PolarSimulation(Simulation):

    def __init__(self, parameters):
        # Call super class initialization
        super().__init__(parameters)

        # Set up the simulation objects
        self.statistics.add_categories([('ber', True),
                                        ('fer', True)])

        self.modem = Modem(parameters, self.rng)

        self.awgn = AWGN(parameters.bits_p_symbol, rng=self.rng, snr_unit=parameters.snr_unit,
                         efficiency_factor=self.modem.rate)

        self.snr_config = SnrConfig({'counter_name': 'ber',
                                     'counter_specs': {'min_relative_accuracy': parameters.min_bit_accuracy,
                                                       'max_counter': parameters.max_bit_counter,
                                                       'min_counter': parameters.min_bit_counter,
                                                       'target_stats': parameters.bit_target_stats}},
                                    {'counter_name': 'fer',
                                     'counter_specs': {'min_relative_accuracy': parameters.min_frame_accuracy,
                                                       'max_counter': parameters.max_frame_counter,
                                                       'min_counter': parameters.min_frame_counter,
                                                       'target_stats': parameters.frame_target_stats}})

        if parameters.dynamic_shannon_start:
            start_snr_db = self.awgn.shannon_limit()

        else:
            start_snr_db = parameters.start_snr_db

        self.snr_manager = snr_manager_builder(parameters.snr_range_type, self.statistics, self.snr_config,
                                               min_snr_db=parameters.min_snr_db,
                                               max_snr_db=parameters.max_snr_db,
                                               snr_db_step=parameters.snr_db_step,
                                               start_snr_db=start_snr_db,
                                               min_snr_step_db=parameters.min_snr_step_db,
                                               start_level=parameters.start_dynamic_level)

    def run(self):
        for snr_db in self.snr_manager:

            self.statistics.add_snr(snr_db)
            self.modem.snr = snr_db

            self.logger.info("Simulating SNR {}".format(snr_db))

            while not self.snr_manager.snr_stop():

                # Transmit a single frame
                tx_signal = self.modem.tx()

                # Add noise to the transmitted signal
                noise_symbols = self.awgn(tx_signal, snr=snr_db)

                # Get the detected user data bits
                detected_bits = self.modem.rx(noise_symbols, self.awgn.variance)

                # Get statistics
                bit_err_cnt, frame_err_cnt = self.modem.compute_errors(detected_bits)

                self.statistics.update_stats(('ber', bit_err_cnt, self.modem.K),
                                             ('fer', frame_err_cnt, 1))

            self.statistics.gen_rate()
            self.snr_manager.sim_stop()
