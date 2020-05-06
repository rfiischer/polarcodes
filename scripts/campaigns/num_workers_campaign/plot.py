"""

Created on 17/03/2020 10:17

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt
import re

import glob


def plot_ber(graphs, legends, title, linestyle, xlabel=r'$E_b/N_0$ (dB)', ylabel='BER', ylim=None, xlim=None,
             fontsize=10):
    fig, ax = plt.subplots()
    for i, graph in enumerate(graphs):
        ax.semilogy(graph[0], graph[1], linestyle[i], fillstyle='none', markersize=8, subsy=[2, 5, 8])

    ax.grid(which='both')
    ax.legend(legends, fontsize=fontsize)
    ax.set_xlabel(xlabel, fontsize=fontsize)
    h = ax.set_ylabel(ylabel, fontsize=fontsize)
    # h.set_rotation(0)
    ax.set_title(r"{} for ".format(ylabel) + title)

    if ylim is not None:
        ax.set_ylim(ylim)

    if xlim is not None:
        ax.set_xlim(xlim)

    fig.tight_layout()

    return fig, ax


# Change plot font
plt.rcParams.update({'font.size': 12})

plot_list = []
methods = []
num_workers = []

for subdir in glob.glob('results/**/'):
    method_name = subdir.split('\\')[-2]
    workers = int(re.split('(\d+)', method_name)[-2])
    num_workers.append(workers)
    if workers > 1:
        plural = 's'
    else:
        plural = ''
    methods.append('{} Worker{}'.format(workers, plural))

    ber = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 1]
    ber_range = np.loadtxt('results//{}//ber.txt'.format(method_name))[:, 0]

    ber = ber[np.where(ber > 0)[0]]
    ber_range = ber_range[np.where(ber > 0)[0]]

    plot_list.append([ber_range, ber])

# QPSK plot - EbN0
methods = [i[0] for i in sorted(zip(methods, num_workers), key=lambda item: item[1])]
plot_list = [i[0] for i in sorted(zip(plot_list, num_workers), key=lambda item: item[1])]

desired_curves = [0, 4, 8]
methods = [methods[i] for i in desired_curves]
plot_list = [plot_list[i] for i in desired_curves]

fig, ax = plot_ber(plot_list,
                   tuple(methods),
                   "Polar Coding",
                   ['g--o', 'r-.^', 'b:*'],
                   ylim=[1e-7, 1],
                   xlim=[-3.2, 0.2],
                   xlabel=r'$E_s/N_0$ (dB)',
                   fontsize=13)

plt.grid(True, which="minor", ls="--")
ax.set_yticklabels(['1e-{}'.format(i) for i in range(8, -1, -1)])
# ax.yaxis.set_label_coords(-0.05,1.02)

plt.show()
