"""


Created on 25/11/2020 12:44

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import bhattacharyya


# Plot config
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 15
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 14
plt.rcParams['figure.figsize'] = (8.8, 4)

# Method config
snr = -1.5
n = 10
plot_range = np.arange(0, 2 ** n)
rel = bhattacharyya(n, snr)[1]
idx = bhattacharyya(n, snr)[0]

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [5, 1]})

frozen = idx[2 ** (n - 1):]
rel_frozen = rel[frozen]

info = idx[:2 ** (n - 1)]
rel_info = rel[info]

ax1.scatter(frozen, rel_frozen, color='deepskyblue', s=2)
ax1.scatter(info, rel_info, color='red', s=2)

ax2.scatter(frozen, [0] * len(frozen), color='deepskyblue', s=2, label='Frozen')
ax2.scatter(info, [0] * len(info), color='red', s=2, label='Information')

ax1.set_xticks([])
ax1.set_ylabel("Bhattacharyya Parameter")

ax2.set_xlabel("Bit Index")
ax2.set_yticks([])

fig.subplots_adjust(left=0.09, bottom=0.14, right=0.99, top=0.95, hspace=0.3)
fig.legend(loc='upper center', fancybox=False, edgecolor='k', bbox_to_anchor=(0.52, 0.376),
           ncol=4)

plt.show()
