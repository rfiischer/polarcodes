"""


Created on 10/03/2020 13:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


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

    return sorted_return
