from abc import ABC, abstractmethod
import logging

import numpy as np

from tcc.core.utils.statistics import Statistics


class Simulation(ABC):

    def __init__(self, parameters):

        self.logger = logging.getLogger(__name__)

        # Set up the simulation objects
        self.parameters = parameters
        self.rng = np.random.RandomState(seed=self.parameters.seed)
        self.statistics = Statistics(parameters)

    @abstractmethod
    def run(self):
        pass
