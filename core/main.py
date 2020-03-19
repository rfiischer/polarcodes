"""


Created on 10/03/2020 20:40

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from time import time, strftime, gmtime
import logging
import subprocess

from core.polar_modem.polar_simulation import PolarSimulation
from core.parameters.parameter_handler import ParameterHandler
from core.logger import setup_logging


def main(parameter_file=None, args=None):
    handler = ParameterHandler(parameter_file, args)

    setup_logging(handler.log_file, handler.log_debug)
    logger = logging.getLogger(__name__)

    simulation = PolarSimulation(handler)

    try:
        label = subprocess.check_output(["git", "describe", "--always"]).strip()

    except subprocess.CalledProcessError:
        label = b'**no git**'

    logger.info("\n### Running simulation! \n### Version: {}\n".format(label.decode()))
    logger.info('parameters = \n {}'.format(handler.dump_params()))

    start_time = time()
    simulation.run()
    run_time = time() - start_time

    logger.info("Simulation ended in {}!".format(strftime('%Hhr:%Mmin:%Ssec', gmtime(run_time))))
