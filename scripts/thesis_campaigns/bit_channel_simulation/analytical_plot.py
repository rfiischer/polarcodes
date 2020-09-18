"""


Created on 17/09/2020 16:40

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import tahir
from tcc.core.utils.plotting import plot_ber


n = 8
start_snr = 2
end_snr = 6
num_div = 5

idxs = [129, 13, 130]
results = [[] for i in range(len(idxs))]

for i in np.linspace(start_snr, end_snr, num_div):
    statistics = tahir(n, i)[1]
    for j in range(len(idxs)):
        results[j].append(statistics[idxs[j]])

# Plot
thickness = [2] * len(idxs)
colours = []
plot_ber([[np.linspace(start_snr, end_snr, num_div), results[j]] for j in range(len(idxs))],
         tuple(idxs),
         "Polar",
         colours[:len(idxs)],
         thickness,
         ylim=[1e-7, 1],
         xlim=[2, 6],
         xlabel=r'$E_s/N_0$ (dB)',
         font_size=12)

plt.show()
