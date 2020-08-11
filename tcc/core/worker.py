from abc import ABC, abstractmethod
import logging

import numpy as np


class Worker(ABC):

    def __init__(self, rng, results_queue, shutdown_event, job_queue):

        self.logger = logging.getLogger(__name__)

        # Set up the simulation objects
        self.rng = rng

        # Queue
        self.results_queue = results_queue
        self.job_queue = job_queue

        # Shutdown
        self.shutdown_event = shutdown_event

    @abstractmethod
    def run(self):
        pass
