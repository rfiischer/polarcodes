"""

Created on 23/07/2020 11:46

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import matplotlib.pyplot as plt


def plot_ber(graphs, legends, title, styl_arr, width, xlabel=r'$E_b/N_0$ (dB)', ylabel='BER', ylim=None, xlim=None,
             font_size=12, rotate_ylabel=False):
    fig, ax = plt.subplots()
    for i, graph in enumerate(graphs):
        ax.semilogy(graph[0], graph[1], styl_arr[i], linewidth=width[i])

    ax.grid(which='both')
    ax.legend(legends, fontsize=font_size)
    ax.set_xlabel(xlabel, fontsize=font_size)
    if rotate_ylabel:
        h = ax.set_ylabel(ylabel, fontsize=font_size)
        h.set_rotation(0)
        ax.yaxis.set_label_coords(-0.05,1.02)

    else:
        ax.set_ylabel(ylabel, fontsize=font_size)

    ax.set_title(r"{} for ".format(ylabel) + title, fontsize=font_size)

    if ylim is not None:
        ax.set_ylim(ylim)

    if xlim is not None:
        ax.set_xlim(xlim)

    plt.rcParams.update({'font.size': font_size})

    fig.tight_layout()
