"""

Created on 20/05/2020 19:03

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.coding.polarcoding import PolarCoding
from tcc.coding.polarcoding.construction import bhattacharyya
import matplotlib.pyplot as plt


# Setup
n = 4
K = 2 ** (n - 1)
esn0 = 10
pc = PolarCoding(n, K, bhattacharyya(n, esn0)[0])

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
plt.scatter(x, y, c=nodes)
plt.show()
