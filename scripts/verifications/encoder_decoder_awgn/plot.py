"""

Created on 17/03/2020 15:12

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import tahir

# Plot config
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 15
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 14
plt.rcParams['figure.figsize'] = (6.6, 4.5)

data = np.loadtxt('results.txt')

marker_style_0 = dict(linestyle='', marker='o',
                      markersize=10, markeredgecolor='red')

marker_style_1 = dict(linestyle='', marker='*',
                      markersize=10, markeredgecolor='blue')

data_len = len(data)
n = int(np.log2(data_len))

fig, ax = plt.subplots()
ax.semilogy(data, fillstyle='none', **marker_style_0)
ax.semilogy(tahir(4, -2)[1], fillstyle='none', **marker_style_1)
ax.set_ylim([1e-6, 1])
ax.set_ylabel("BER")
ax.set_xlabel("Bit Channel")
ax.set_xticks(np.arange(0, data_len))
ax.grid(True, which="both")

plt.show()
