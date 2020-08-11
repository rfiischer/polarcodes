"""

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

import glob

from tcc.core.utils.plotting import plot_ber


plot_list_s = []
plot_list_n = []
methods_s = []
methods_n = []

for subdir in glob.glob('results/**/'):
    method_name = subdir.split('\\')[-2]
    if method_name[0] == 's':
        methods_s.append(method_name)

        ber = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 1]
        ber_range = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 0]

        ber = ber[np.where(ber > 0)[0]]
        ber_range = ber_range[np.where(ber > 0)[0]]

        plot_list_s.append([ber_range, ber])

    else:
        methods_n.append(method_name)

        ber = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 1]
        ber_range = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 0]

        ber = ber[np.where(ber > 0)[0]]
        ber_range = ber_range[np.where(ber > 0)[0]]

        plot_list_n.append([ber_range, ber])

# QPSK plot - EbN0
thickness = [2] * len(methods_s)
colours = []
plot_ber(plot_list_s,
         tuple(methods_s),
         "Polar",
         colours[:len(methods_s)],
         thickness,
         ylim=[1e-7, 1],
         xlim=[-3, 2],
         xlabel=r'$E_s/N_0$ (dB)',
         font_size=12)

# QPSK plot - EbN0
thickness = [2] * len(methods_n)
colours = []
plot_ber(plot_list_n,
         tuple(methods_n),
         "Polar",
         colours[:len(methods_n)],
         thickness,
         ylim=[1e-7, 1],
         xlim=[-3, 2],
         xlabel=r'$E_s/N_0$ (dB)',
         font_size=12)

plt.show()
