"""
Plot all the results on the results folder

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

import glob

from tcc.core.utils.plotting import plot_ber


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
thickness = [2] * len(methods)
colours = []
plot_ber(plot_list,
         tuple(methods),
         "Polar",
         colours[:len(methods)],
         thickness,
         ylim=[1e-7, 1],
         xlim=[0, 3],
         xlabel=r'$E_s/N_0$ (dB)')

plt.show()
