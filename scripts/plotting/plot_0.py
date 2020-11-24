"""


Created on 23/11/2020 15:25

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt


# Plot resources
markers = ["s", "o", "^", "d", "x", "*", "1", "+"]

linestyle_tuple = [
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1))),

     ('loosely dashed',        (0, (5, 10)))]

# colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab: purple', 'tab:brown', 'tab:pink', 'tab:gray']
colors = ['red', 'deepskyblue', 'orange', 'blue', 'magenta', 'green', 'darkviolet', 'black']

# Plot configuration
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 14
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["xtick.labelsize"] = 13
plt.rcParams["ytick.labelsize"] = 13
plt.rcParams["axes.labelsize"] = 14
plt.rcParams['figure.figsize'] = (6.4, 5.8)

plot_type = 'ber_fer'
width = 1
fill = 'none'
marker_size = 8
gridline = (0, (5, 10))
rotate_ylabel = True

xlabel = r"$E_b/N_0$ [dB]"

# dict prototype: {'label': ,'dir': }
plot_list = [{'label': 'DEGA', 'dir': 'm_dega'},
             {'label': 'M-DEGA', 'dir': 'm_mdega'}]

# Plot creation
if plot_type == 'ber_fer':
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True)

else:
    fig, ax = plt.subplots(1, 1)

for i, plot_dict in enumerate(plot_list):
    if plot_type in ['ber', 'fer']:
        data = np.loadtxt(f'resources//{plot_dict["dir"]}//{plot_type}.txt')

        error_rate = data[:, 1]
        plot_range = data[:, 0]

        ax.semilogy(plot_range, error_rate, linewidth=width, marker=markers[i], color=colors[i], fillstyle=fill,
                    markersize=marker_size, label=plot_dict['label'])

        ax.grid(True, which='minor', linestyle=gridline)
        ax.grid(True, which='major', linestyle=gridline)

        if rotate_ylabel:
            h = ax.set_ylabel(plot_type.upper())
            h.set_rotation(0)
            ax.yaxis.set_label_coords(-0.05, 1.02)

        else:
            ax.set_ylabel(plot_type.upper())

        ax.set_xlabel(xlabel, fontsize=14)

    else:
        ber_data = np.loadtxt(f'resources//{plot_dict["dir"]}//ber.txt')
        fer_data = np.loadtxt(f'resources//{plot_dict["dir"]}//fer.txt')

        ber = ber_data[:, 1]
        ber_range = ber_data[:, 0]

        fer = fer_data[:, 1]
        fer_range = fer_data[:, 0]

        ax1.semilogy(fer_range, fer, linewidth=width, marker=markers[i], color=colors[i], fillstyle=fill,
                     markersize=marker_size, label=plot_dict['label'])
        ax2.semilogy(ber_range, ber, linewidth=width, marker=markers[i], color=colors[i], fillstyle=fill,
                     markersize=marker_size, label=plot_dict['label'])

        ax1.grid(True, which='minor', linestyle=gridline)
        ax1.grid(True, which='major', linestyle=gridline)
        ax2.grid(True, which='minor', linestyle=gridline)
        ax2.grid(True, which='major', linestyle=gridline)

        if rotate_ylabel:
            h = ax1.set_ylabel('FER')
            h.set_rotation(0)
            ax1.yaxis.set_label_coords(-0.05, 1.02)

            h = ax2.set_ylabel('BER')
            h.set_rotation(0)
            ax2.yaxis.set_label_coords(-0.05, 1.02)

        else:
            ax1.set_ylabel('FER')
            ax2.set_ylabel('BER')

        ax1.set_xlabel(xlabel, fontsize=14)
        ax2.set_xlabel(xlabel, fontsize=14)


# Common setup
fig.subplots_adjust(wspace=0.4)

if plot_type in ['ber', 'fer']:
    handles, labels = ax.get_legend_handles_labels()

else:
    handles, labels = ax1.get_legend_handles_labels()

if not labels:
    fig.legend(handles, labels, loc='upper center', fancybox=False, edgecolor='k', bbox_to_anchor=(0.5, 0.13))
    fig.subplots_adjust(wspace=0.4, bottom=0.23)

else:
    fig.set_figwidth(5.4)
    fig.set_figheight(4.8)
    fig.tight_layout()

plt.show()
