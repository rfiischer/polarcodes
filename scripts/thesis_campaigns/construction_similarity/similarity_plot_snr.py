"""


Created on 25/11/2020 17:04

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import matplotlib.pyplot as plt
import numpy as np

from tcc.coding.polarcoding.construction import dega
from tcc.core.utils.awgn import AWGN

n = 10
k_info = 2 ** (n - 1) - 16
k_tot = 2 ** (n - 1)
snreb0 = 2
snreb1 = 2.5

rng = np.random.RandomState()
awgn = AWGN(1, rng)
snr0 = awgn.unit_conversion(snreb0, 1, k_info / 2 ** n, "EbN0_dB", "EsN0_dB")
snr1 = awgn.unit_conversion(snreb1, 1, k_info / 2 ** n, "EbN0_dB", "EsN0_dB")

dega_rel0 = dega(n, snr0)[0]
dega_rel1 = dega(n, snr1)[0]

dega_sheet0 = np.zeros(2 ** n)
dega_sheet1 = np.zeros(2 ** n)

dega_i0 = dega_rel0[:k_tot]
dega_i1 = dega_rel1[:k_tot]

dega_sheet0[dega_i0] = 1
dega_sheet1[dega_i1] = 1

err_dega0 = np.logical_xor(dega_sheet0, dega_sheet0)
err_dega1 = np.logical_xor(dega_sheet0, dega_sheet1)


# Plot configuration
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 15
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 14
plt.rcParams['figure.figsize'] = (9, 2)

fig, ax1 = plt.subplots(1, 1, sharex='all')

dega1_eq = np.where(err_dega1 == 0)[0]
dega1_dif0 = np.where(np.logical_and(err_dega1 == 1, dega_sheet0 == 1))[0]
dega1_dif1 = np.where(np.logical_and(err_dega1 == 1, dega_sheet0 == 0))[0]
ax1.scatter(dega1_eq, [0] * len(dega1_eq), color='deepskyblue', s=5, label=f"Equal to $E_b/N_0={snreb0}$")
ax1.scatter(dega1_dif0, [0] * len(dega1_dif0), color='red', s=100, label=f"Information in $E_b/N_0={snreb0}$", marker=2)
ax1.scatter(dega1_dif1, [0] * len(dega1_dif1), color='orange', s=100, label=f"Frozen in $E_b/N_0={snreb0}$", marker=3)

ax1.set_yticks([])

ax1.set_title(f"$E_b/N_0={snreb1}$")

handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', fancybox=False, edgecolor='k', bbox_to_anchor=(0.5, 0.25),
           ncol=4)
fig.subplots_adjust(left=0.02, bottom=0.37, right=0.98, top=0.84, hspace=0.57)

plt.show()
