from queue import Empty

from tcc.core.worker import Worker
from tcc.core.utils.awgn import AWGN
from tcc.polar_modem.modem import Modem


class PolarWorker(Worker):

    def __init__(self, parameters, rng, results_queue, shutdown_event, job_queue):
        # Call super class initialization
        super().__init__(rng, results_queue, shutdown_event, job_queue)

        self.parameters = parameters
        self.snr_id = None

    def run(self):

        # Initialize Modem and AWGN
        modem = Modem(self.parameters, self.rng)
        awgn = AWGN(self.parameters.bits_p_symbol, rng=self.rng, snr_unit=self.parameters.snr_unit,
                    efficiency_factor=modem.rate)

        while not self.shutdown_event.is_set():

            try:
                # Get simulation instruction
                snr_db, snr_id = self.job_queue.get(block=False)

                # Set SNR
                if snr_id != self.snr_id:
                    self.snr_id = snr_id
                    modem.snr = snr_db

                # Transmit a single frame
                tx_signal = modem.tx()

                # Add noise to the transmitted signal
                noise_symbols = awgn(tx_signal, snr=snr_db)

                # Get the detected user data bits
                detected_bits = modem.rx(noise_symbols, awgn.variance)

                # Get statistics
                bit_err_cnt, frame_err_cnt = modem.compute_errors(detected_bits)

                # Send statistics
                self.results_queue.put((('fer', frame_err_cnt, 1), ('ber', bit_err_cnt, modem.tx_size)))

                self.job_queue.task_done()

            except Empty:
                pass
