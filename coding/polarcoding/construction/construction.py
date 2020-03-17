"""


Created on 10/03/2020 20:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
from scipy.stats import norm
import logging
import sys

logger = logging.getLogger(__name__)


def bhattacharyya(n, design_snr):
    start_parameter = [np.exp(- 10 ** (design_snr / 10))]
    for i in range(n):
        size = len(start_parameter)
        out_parameter = np.zeros(size * 2, dtype=np.float64)
        for j, parameter in enumerate(start_parameter):
            out_parameter[j] = 2 * parameter - parameter ** 2
            out_parameter[j + size] = parameter ** 2

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1])]

    return sorted_return, start_parameter


def tahir(n, design_snr):
    start_parameter = [norm.sf(np.sqrt(2 * 10 ** (design_snr / 10)))]
    for i in range(n):
        j = 2 ** i
        out_parameter = np.zeros(j * 2, dtype=np.float64)
        for k, parameter in enumerate(start_parameter):
            out_parameter[k] = 2 * parameter * (1 - parameter)
            out_parameter[k + j] = norm.sf(np.sqrt(2) * norm.isf(parameter))

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1])]

    return sorted_return, start_parameter


def construction(method, n, design_snr):
    if method == "bhattacharyya":
        rel_idx = bhattacharyya(n, design_snr)[0]

    elif method == "tahir":
        rel_idx = tahir(n, design_snr)[0]

    else:
        logger.error("Construction method not implemented {}".format(method))
        sys.exit(1)

    return rel_idx
