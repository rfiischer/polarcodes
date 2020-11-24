"""
Plot the decoding tree with color-coded nodes identifying Rate-0, Rate-1, SPC, REP or other nodes.

Created on 20/05/2020 19:03

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import matplotlib.pyplot as plt
import numpy as np

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import dega

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 14
plt.rcParams["mathtext.fontset"] = "stix"

# Setup
n = 10
K = 2 ** (n - 1)
esn0 = 0
decoding_type = 'ssc'
pc = PolarCoding(n, K, dega(n, esn0)[0], decoding_type, list_size=8, implementation_type='python')

# Gather info
nodes = pc.decode.node_sheet
node_data = pc.decode.address_list
steps = pc.decode.tasks

# Create vectors
x = []
for i in range(2 ** (n + 1) - 1):
    x.append((i + 1 - 2 ** (n - node_data[i, 6])) / (2 ** (n - node_data[i, 6])) -
             (2 ** (n - node_data[i, 6]) - 1) / (2 ** (n - node_data[i, 6] + 1)))

y = [2 ** node_data[i, 6] for i in range(2 ** (n + 1) - 1)]

x = np.array(x)
y = np.array(y)

# Plot
cdict = {0: 'lawngreen', 1: 'darkturquoise', 2: 'goldenrod', 3: 'darkviolet', 255: 'slategrey'}
ldict = {0: 'Rate-0', 1: 'Rate-1', 2: 'REP', 3: 'SPC', 255: 'Neither'}
fig, ax = plt.subplots()
for g in np.unique(nodes):
    ix = np.where(nodes == g)
    ax.scatter(x[ix], y[ix], color=cdict[g], label=ldict[g])

ax.set_yticks([2 ** i for i in range(n, n-5, -1)])
ax.set_yticklabels([f'$s={n}$', f'$s={n-1}$', f'$s={n-2}$', f'$s={n-3}$', f'$s={n-4}$'])
ax.set_xticks([])

ax.legend()
plt.show()
