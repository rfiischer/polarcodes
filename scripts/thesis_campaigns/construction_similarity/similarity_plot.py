"""


Created on 25/11/2020 17:04

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import matplotlib.pyplot as plt
import numpy as np

from tcc.coding.polarcoding.construction import bhattacharyya, dega, mdega, tahir
from tcc.core.utils.awgn import AWGN

n = 12
k = 2 ** (n - 1)
snreb = 2.5

rng = np.random.RandomState()
awgn = AWGN(1, rng)
snr = awgn.unit_conversion(snreb, 1, k / 2 ** n, "EbN0_dB", "EsN0_dB")

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

err_bhat = np.logical_xor(bhat_sheet, bhat_sheet)
err_dega = np.logical_xor(bhat_sheet, dega_sheet)
err_mdega = np.logical_xor(bhat_sheet, mdega_sheet)
err_tahir = np.logical_xor(bhat_sheet, tahir_sheet)


# Plot configuration
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 15
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 14
plt.rcParams['figure.figsize'] = (9, 4.5)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex='all')

dega_eq = np.where(err_dega == 0)[0]
dega_dif0 = np.where(np.logical_and(err_dega == 1, bhat_sheet == 1))[0]
dega_dif1 = np.where(np.logical_and(err_dega == 1, bhat_sheet == 0))[0]
ax1.scatter(dega_eq, [0] * len(dega_eq), color='deepskyblue', s=5)
ax1.scatter(dega_dif0, [0] * len(dega_dif0), color='red', s=100, marker=2)
ax1.scatter(dega_dif1, [0] * len(dega_dif1), color='orange', s=100, marker=3)

mdega_eq = np.where(err_mdega == 0)[0]
mdega_dif0 = np.where(np.logical_and(err_mdega == 1, bhat_sheet == 1))[0]
mdega_dif1 = np.where(np.logical_and(err_mdega == 1, bhat_sheet == 0))[0]
ax2.scatter(mdega_eq, [0] * len(mdega_eq), color='deepskyblue', s=5)
ax2.scatter(mdega_dif0, [0] * len(mdega_dif0), color='red', s=100, marker=2)
ax2.scatter(mdega_dif1, [0] * len(mdega_dif1), color='orange', s=100, marker=3)

tahir_eq = np.where(err_tahir == 0)[0]
tahir_dif0 = np.where(np.logical_and(err_tahir == 1, bhat_sheet == 1))[0]
tahir_dif1 = np.where(np.logical_and(err_tahir == 1, bhat_sheet == 0))[0]
ax3.scatter(tahir_eq, [0] * len(tahir_eq), color='deepskyblue', s=5, label="Equal to Bhattacharyya")
ax3.scatter(tahir_dif0, [0] * len(tahir_dif0), color='red', s=100, label="Information in Bhattacharyya", marker=2)
ax3.scatter(tahir_dif1, [0] * len(tahir_dif1), color='orange', s=100, label="Frozen in Bhattacharyya", marker=3)

ax1.set_yticks([])
ax2.set_yticks([])
ax3.set_yticks([])

ax1.set_title("DEGA")
ax2.set_title("M-DEGA")
ax3.set_title("BEE")

ax3.set_xlabel("Bit Index")
handles, labels = ax3.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', fancybox=False, edgecolor='k', bbox_to_anchor=(0.5, 0.11),
           ncol=4)
fig.subplots_adjust(left=0.02, bottom=0.21, right=0.98, top=0.92, hspace=0.57)

plt.show()
