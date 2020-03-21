"""

Created on 17/03/2020 15:12

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import tahir

data = np.loadtxt('results.txt')

marker_style_0 = dict(color='tab:blue', linestyle='', marker='o',
                      markersize=10, markerfacecoloralt='tab:red')

marker_style_1 = dict(color='tab:red', linestyle='', marker='*',
                      markersize=10, markerfacecoloralt='tab:red')

plt.semilogy(data, fillstyle='none', **marker_style_0)
plt.semilogy(tahir(4, -2)[1], fillstyle='none', **marker_style_1)
plt.ylim(1e-6, 1)
plt.ylabel("BER")
plt.xlabel("Bit Channel")
plt.xticks(np.arange(0, 16))
plt.grid(True, which="both")

plt.show()
