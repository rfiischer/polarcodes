"""

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

import glob


def plot_ber(graphs, legends, title, xlabel=r'$E_b/N_0$ (dB)', ylabel='BER', ylim=None, xlim=None):
    fig, ax = plt.subplots()
    for i, graph in enumerate(graphs):
        ax.semilogy(graph[0], graph[1])

    ax.grid(which='both')
    ax.legend(legends)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(r"{} for ".format(ylabel) + title)

    if ylim is not None:
        ax.set_ylim(ylim)

    if xlim is not None:
        ax.set_xlim(xlim)

    fig.tight_layout()


# Change plot font
plt.rcParams.update({'font.size': 12})

plot_list = []
methods = []

for subdir in glob.glob('results/**/'):
    method_name = subdir.split('\\')[-2]
    methods.append(method_name)

    ber = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 1]
    ber_range = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 0]

    ber = ber[np.where(ber > 0)[0]]
    ber_range = ber_range[np.where(ber > 0)[0]]

    plot_list.append([ber_range, ber])

# QPSK plot - EbN0
plot_ber(plot_list,
         tuple(methods),
         "Polar",
         ylim=[1e-7, 1],
         xlim=[-3, 0],
         xlabel=r'$E_s/N_0$ (dB)')

plt.show()
