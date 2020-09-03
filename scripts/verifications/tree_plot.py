"""
Plot the decoding tree with color-coded nodes identifying Rate-0, Rate-1, SPC, REP or other nodes.

Created on 20/05/2020 19:03

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import tahir
import matplotlib.pyplot as plt


# Setup
n = 11
K = 2 ** (n - 1)
esn0 = -1
decoding_type = 'sscl-spc'
pc = PolarCoding(n, K, tahir(n, esn0)[0], decoding_type, list_size=8, implementation_type='python')

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

# Plot
plt.scatter(x, y, c=nodes, cmap='Accent')
plt.show()
