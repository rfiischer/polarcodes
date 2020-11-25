"""


Created on 25/11/2020 17:04

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from tcc.coding.polarcoding.construction import bhattacharyya, dega, mdega, tahir
from tcc.core.utils.awgn import AWGN

n = 12
k = 3 * 2 ** n // 4
min_ebsnr = 0
max_ebsnr = 3.5
steps = 21

rng = np.random.RandomState()
awgn = AWGN(1, rng)
min_snr = awgn.unit_conversion(min_ebsnr, 1, k / 2 ** n, "EbN0_dB", "EsN0_dB")
max_snr = awgn.unit_conversion(max_ebsnr, 1, k / 2 ** n, "EbN0_dB", "EsN0_dB")

bhat_data = []
dega_data = []
mdega_data = []
tahir_data = []
for snr in np.linspace(min_snr, max_snr, steps):
    print(snr)
    bhat_rel = bhattacharyya(n, snr)[0]
    dega_rel = dega(n, snr)[0]
    mdega_rel = mdega(n, snr)[0]
    tahir_rel = tahir(n, snr)[0]

    bhat_sheet = np.zeros(2 ** n)
    dega_sheet = np.zeros(2 ** n)
    mdega_sheet = np.zeros(2 ** n)
    tahir_sheet = np.zeros(2 ** n)

    bhat_i = bhat_rel[:k]
    dega_i = dega_rel[:k]
    mdega_i = mdega_rel[:k]
    tahir_i = tahir_rel[:k]

    bhat_sheet[bhat_i] = 1
    dega_sheet[dega_i] = 1
    mdega_sheet[mdega_i] = 1
    tahir_sheet[tahir_i] = 1

    bhat_data.append((2 ** n - np.sum(np.logical_xor(bhat_sheet, bhat_sheet))) / 2 ** n)
    dega_data.append((2 ** n - np.sum(np.logical_xor(bhat_sheet, dega_sheet))) / 2 ** n)
    mdega_data.append((2 ** n - np.sum(np.logical_xor(bhat_sheet, mdega_sheet))) / 2 ** n)
    tahir_data.append((2 ** n - np.sum(np.logical_xor(bhat_sheet, tahir_sheet))) / 2 ** n)


# Plot configuration
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 15
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 14
plt.rcParams['figure.figsize'] = (6.6, 4.5)

fig, ax = plt.subplots()
ax.yaxis.set_major_formatter(ticker.PercentFormatter(1, symbol=''))

plot_range = np.linspace(min_ebsnr, max_ebsnr, steps)
ax.plot(plot_range, bhat_data, label='Bhattacharyya', color='blue', marker='s',
        fillstyle='none', markersize=8)
ax.plot(plot_range, dega_data, label='DEGA', color='red', marker='o', fillstyle='none',
        markersize=8)
ax.plot(plot_range, mdega_data, label='M-DEGA', color='deepskyblue', marker='^',
        fillstyle='none', markersize=8)
ax.plot(plot_range, tahir_data, label='BEE', color='orange', marker='d', fillstyle='none',
        markersize=8)

ax.set_xlabel("Design $E_b/N_0$ [dB]")
ax.set_ylabel("Similarity to Bhattacharyya (%)")
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', fancybox=False, edgecolor='k', bbox_to_anchor=(0.5, 0.11),
           ncol=4)
fig.subplots_adjust(left=0.15, bottom=0.22, right=0.98, top=0.99)

plt.show()
