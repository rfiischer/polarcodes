"""


Created on 27/09/2020 19:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


def read_data(f_name):
    data = []
    snr = []
    total = []
    with open(f_name) as f:
        # Read header
        f.readline()
        for line in f:
            # Load lines
            line = np.fromstring(line, sep='\t')
            data.append(line[2:])
            snr.append(line[0])
            total.append(line[1])

    return data, snr, total
