"""

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc


def plot_ber(graphs, legends, title, styl_arr, width, xlabel=r'$E_b/N_0$ (dB)', ylabel='BER'):
    fig, ax = plt.subplots()
    for i, graph in enumerate(graphs):
        ax.semilogy(graph[0], graph[1], styl_arr[i], linewidth=width[i])

    ax.grid(which='both')
    ax.legend(legends)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(r"{} for ".format(ylabel) + title)
    fig.tight_layout()


# Change plot font
plt.rcParams.update({'font.size': 12})

# Simulated BER
ber2_id0 = np.loadtxt('results//ber.txt')[:, 1]
ber2_id0_range = np.loadtxt('results//ber.txt')[:, 0]

# QPSK plot - EbN0
plot_ber([[ber2_id0_range, ber2_id0],
          [ber2_id0_range, 1 / 2 * erfc(np.sqrt(2 * np.power(10, ber2_id0_range / 10)) * np.sin(np.pi / 4))]],
         ('Coded', 'Uncoded - Theoretical'),
         "Polar",
         ['r', 'b'],
         [2, 2])

plt.show()
