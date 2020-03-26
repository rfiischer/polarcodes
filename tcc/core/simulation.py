"""

Created on 25/03/2020 18:12

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from abc import abstractmethod, ABC


class Simulation(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self):
        pass
