"""


Created on 09/03/2020 20:39

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


def int2bit_constructor(num_bits, msb_first=True):
    """Returns array that maps integers into binary arrays.

    :num_bits: number of bits to display
    :msb_first: indicates the significance of the return first bit
    :returns: numpy array a = [[0, 0, ..., 0], [0, 0, ..., 1], ...] such that a[x] = array([0, 1, ..., 0])
    """

    out_array = []

    # Creates toggle memory array
    toggle_array_new = [0] * num_bits

    for i in range(0, 2 ** num_bits):
        if msb_first:
            out_array.append(toggle_array_new[::-1])
        else:
            out_array.append(toggle_array_new.copy())

        # Copies old state
        toggle_array_old = toggle_array_new.copy()

        # Performs toggle of LSB
        toggle_array_new[0] = 1 - toggle_array_new[0]

        for j in range(1, num_bits):

            # Checks for 1 to 0 transition
            if (toggle_array_old[j-1] == 1) and (toggle_array_new[j-1] == 0):

                # Copy old state
                toggle_array_old = toggle_array_new.copy()

                # Toggle next bit
                toggle_array_new[j] = 1 - toggle_array_new[j]

    return np.array(out_array, dtype=int)


def bit2int_constructor(num_bits, msb_first=True):
    """Returns array that maps binary arrays into bit arrays.

    :num_bits: number of bits to display
    :msb_first: indicates the significance of the return first bit
    :returns: numpy array 'a' such that a[0,1,...,0] = int(01...0)
    """

    out_array = np.array([i for i in range(0, 2 ** num_bits)], dtype=int)

    if msb_first:
        ordering = 'C'

    else:
        ordering = 'F'

    dim_tuple = tuple([2] * num_bits)

    return np.reshape(out_array, dim_tuple, ordering)
