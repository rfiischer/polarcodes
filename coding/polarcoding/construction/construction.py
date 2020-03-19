"""


Created on 10/03/2020 20:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
from scipy.stats import norm
import logging
import sys
from pynverse import inversefunc

logger = logging.getLogger(__name__)


def phi(x):
    if 10 > x >= 0:
        out = np.exp(-0.4527 * x ** 0.86 + 0.0218)

    elif x >= 10:
        out = np.sqrt(np.pi / x) * np.exp(- x / 4) * (1 - 10 / (7 * x))

    else:
        out = 0

    return out


iphi = inversefunc(phi, domain=0, open_domain=[True, False])


def bhattacharyya(n, design_snr):
    start_parameter = [np.exp(- 10 ** (design_snr / 10))]
    for i in range(n):
        size = len(start_parameter)
        out_parameter = np.zeros(size * 2, dtype=np.float64)
        for j, parameter in enumerate(start_parameter):
            out_parameter[2 * j] = 2 * parameter - parameter ** 2
            out_parameter[2 * j + 1] = parameter ** 2

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1])]

    return sorted_return, start_parameter


def tahir(n, design_snr):
    start_parameter = [norm.sf(np.sqrt(2 * 10 ** (design_snr / 10)))]
    for i in range(n):
        j = 2 ** i
        out_parameter = np.zeros(j * 2, dtype=np.float64)
        for k, parameter in enumerate(start_parameter):
            out_parameter[2 * k] = 2 * parameter * (1 - parameter)
            out_parameter[2 * k + 1] = norm.sf(np.sqrt(2) * norm.isf(parameter))

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1])]

    return sorted_return, start_parameter


def mdega(n, design_snr):
    start_parameter = [4 * 10 ** (design_snr / 10)]
    for i in range(n):
        j = 2 ** i
        out_parameter = np.zeros(j * 2, dtype=np.float64)
        for k, parameter in enumerate(start_parameter):
            out_parameter[2 * k] = 2 * norm.isf(2 * norm.sf(np.sqrt(parameter / 2)) *
                                                (1 - norm.sf(np.sqrt(parameter / 2)))) ** 2
            out_parameter[2 * k + 1] = 2 * parameter

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1], reverse=True)]

    return sorted_return, start_parameter


def dega(n, design_snr):
    start_parameter = [4 * 10 ** (design_snr / 10)]
    for i in range(n):
        j = 2 ** i
        out_parameter = np.zeros(j * 2, dtype=np.float64)
        for k, parameter in enumerate(start_parameter):
            out_parameter[2 * k] = iphi(1 - (1 - phi(parameter)) ** 2)
            out_parameter[2 * k + 1] = 2 * parameter

        start_parameter = out_parameter

    sorted_return = [x[0] for x in sorted(enumerate(start_parameter), key=lambda item: item[1], reverse=True)]

    return sorted_return, start_parameter


def construction(method, n, design_snr):
    if method == "bhattacharyya":
        rel_idx = bhattacharyya(n, design_snr)[0]

    elif method == "tahir":
        rel_idx = tahir(n, design_snr)[0]

    elif method == "mdega":
        rel_idx = mdega(n, design_snr)[0]

    elif method == "dega":
        rel_idx = mdega(n, design_snr)[0]

    else:
        logger.error("Construction method not implemented {}".format(method))
        sys.exit(1)

    return rel_idx
