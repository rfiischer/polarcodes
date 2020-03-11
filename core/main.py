"""


Created on 10/03/2020 20:40

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from core.polar_modem.polar_simulation import PolarSimulation
from core.parameters.parameter_handler import ParameterHandler
from core.logger import setup_logging


def main(parameter_file=None):
    handler = ParameterHandler(parameter_file)
    setup_logging(handler.log_file)
    simulation = PolarSimulation(handler)

    simulation.run()
