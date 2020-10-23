"""

Created on 25/03/2020 21:44

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import multiprocessing as mp
import logging
import numpy as np
from time import time

from tcc.core.simulation import Simulation
from tcc.polar_modem.polar_worker import PolarWorker
from tcc.core.utils.statistics import Statistics
from tcc.core.utils.snr_manager import snr_manager_builder, SnrConfig
from tcc.core.utils.awgn import AWGN


class PolarSimulation(Simulation):
    def __init__(self, parameters):
        super().__init__()

        # Logger
        self.logger = logging.getLogger(__name__)

        # Shutdown
        self.shutdown = mp.Event()

        # Statistics
        self.statistics = Statistics(parameters)
        self.statistics.add_categories([('ber', True),
                                        ('fer', True)])

        # Get seeds
        if parameters.seed == -1:
            ss = np.random.SeedSequence()

        else:
            ss = np.random.SeedSequence(parameters.seed)

        self.logger.info("seed = {}\n".format(ss.entropy))

        random_generators = [np.random.default_rng(s) for s in ss.spawn(parameters.num_workers)]

        # Workers
        self.num_workers = parameters.num_workers
        self.frame_pack_size = parameters.frame_pack_size
        self.job_queue = mp.JoinableQueue()
        self.results_queue = mp.Queue()
        self.workers = [PolarWorker(parameters, rng, self.results_queue, self.shutdown, self.job_queue)
                        for rng in random_generators]

        # SNR Manager
        self.snr_config = SnrConfig({'counter_name': 'ber',
                                     'counter_specs': {'min_event_counter': parameters.min_bit_events,
                                                       'max_counter': parameters.max_bit_counter,
                                                       'min_counter': parameters.min_bit_counter,
                                                       'target_stats': parameters.bit_target_stats}},
                                    {'counter_name': 'fer',
                                     'counter_specs': {'min_event_counter': parameters.min_frame_events,
                                                       'max_counter': parameters.max_frame_counter,
                                                       'min_counter': parameters.min_frame_counter,
                                                       'target_stats': parameters.frame_target_stats}})

        if parameters.dynamic_shannon_start:
            start_snr_db = AWGN.shannon_limit(parameters.bits_p_symbol, parameters.k / 2 ** parameters.n,
                                              parameters.snr_unit)

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

        # Start workers
        worker_processes = [mp.Process(target=worker.run) for worker in self.workers]
        for process in worker_processes:
            process.daemon = True
            process.start()

        for snr_db, snr_id in self.snr_manager:

            self.statistics.add_snr(snr_db)

            self.logger.info("Simulating SNR {}".format(snr_db))

            sim_frames = 0
            while not self.snr_manager.snr_stop():
                for _ in range(self.frame_pack_size):
                    self.job_queue.put((snr_db, snr_id))

                self.job_queue.join()

                self.statistics.update_from_queue(self.results_queue)
                self.statistics.gen_stats()
                sim_frames += self.frame_pack_size
                self.logger.debug("Simulated {} frames at SNR {}".format(sim_frames, snr_db))

            # Generate statistics
            self.statistics.gen_rate()
            self.snr_manager.sim_stop()

        self.shutdown.set()
        [process.join() for process in worker_processes]
