"""
Verifies class construction

Created on 12/02/2020 12:13

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

from polarcoding import PolarCoding


p4 = PolarCoding(2)
print("n: {}".format(p4.n))
print("N: {}".format(p4.N))
print("F:\n{}".format(p4.F))
print("Fn:\n{}".format(p4.Fn))
print("idx: {}".format(p4.rel_idx))
print("Encode [0, 1, 0, 1]: {}".format(p4.encode(np.array([0, 1, 0, 1]))))
print("Rate: {}".format(p4.encode.rate))
print("Encode [0, 1]: {}".format(p4.encode(np.array([0, 1]))))
print("Rate: {}".format(p4.encode.rate))
