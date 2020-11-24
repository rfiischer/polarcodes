"""

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

import glob
import os

from tcc.core.utils.plotting import plot_ber


plot_list = []
ber_vals = []
snr_vals = []

for subdir in glob.glob('results/**/'):
    method_name = subdir.split('\\')[-2]
    snr = float(method_name.split('_')[-1])

    _, ber = np.loadtxt('results//{}//ber.txt'.format(method_name))

    ber_vals.append(ber)
    snr_vals.append(snr)

ber_data = np.zeros((len(ber_vals), 2))
ber_data[:, 0] = snr_vals
ber_data[:, 1] = ber_vals

if not os.path.exists('results//condensed'):
    os.makedirs('results//condensed')

np.savetxt('results//condensed//ber.txt', ber_data)

# QPSK plot - EbN0
thickness = [2]
colours = ['r']
plot_ber([[snr_vals, ber_vals]],
         ('SNR',),
         "SNR",
         colours[:0],
         thickness,
         ylim=[1e-7, 1],
         xlim=[1, 5],
         xlabel=r'$E_s/N_0$ (dB)',
         font_size=12)

plt.show()
