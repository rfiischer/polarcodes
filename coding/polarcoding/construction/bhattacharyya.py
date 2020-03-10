"""


Created on 10/03/2020 13:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


def bhattacharyya(n):
    start_couples = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    for i in range(1, n):
        size = start_couples.shape[0]
        out_couples = np.zeros((size * 2, 2), dtype=np.uint8)
        for j, couple in enumerate(start_couples):
            out_couples[j, :] = [couple[0] + 1, couple[1]]
            out_couples[j + size, :] = [2 * couple[0], couple[1] + 1]

        start_couples = out_couples

    first_sort = sorted(enumerate(start_couples), key=lambda item: item[1][0])
    second_sort = sorted(first_sort, key=lambda item: item[1][1], reverse=True)

    return [elm[0] for elm in second_sort]
