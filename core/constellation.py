"""
Implement DVB-RCS2 constellations
"""

from abc import ABC, abstractmethod
import numpy as np


class Constellation(ABC):

    def __init__(self):
        self.mod_schemes = {2: self.bpsk,
                            4: self.qpsk,
                            8: self.psk_8,
                            16: self.psk_16}

        self.phase_func = {2: None,
                           4: None,
                           8: None,
                           16: None}

    @abstractmethod
    def bpsk(self):
        pass

    @abstractmethod
    def qpsk(self):
        pass

    @abstractmethod
    def psk_8(self):
        pass

    @abstractmethod
    def psk_16(self):
        pass

    @staticmethod
    def psk(radius, order, phi0):
        """Generates a generic PSK modulation.

        :radius: radius of the constellation
        :order: number of constellation points, separated uniformly
        :phi0: angle offset with respect to x axis
        :returns: numpy.ndarray
        """

        # Empty list of points to be returned
        constellation_points = []

        # Add points uniformly spaced with a phase offset of phi0
        for angle in np.linspace(0, 2 * np.pi, order, endpoint=False):
            constellation_points.append(radius * np.exp(1j * (angle + phi0)))

        # Return the numpy array
        return np.array(constellation_points)


class PolarConstellation(Constellation):

    def __init__(self):
        super().__init__()

    def bpsk(self):
        """Returns the pi/2-BPSK constellation specified in [2]."""

        pi_2_bpsk = np.array([1, -1])

        return pi_2_bpsk

    def qpsk(self):
        """Returns the QPSK constellation according to [1]."""

        # Basic QPSK in the natural counterclockwise order
        constellation_points = self.psk(1, 4, np.pi / 4)

        # Permute points in order to satisfy the Gray coding proposed in [1]
        constellation_points = constellation_points[[0, 3, 1, 2]]

        return np.array(constellation_points)

    def psk_8(self):
        """Returns the standard 8PSK constellation according to [1]."""

        # Basic 8PSK in the natural counterclockwise order
        constellation_points = self.psk(1, 8, np.pi / 8)

        # Permute points in order to satisfy the Gray coding proposed in [1]
        constellation_points = constellation_points[[0, 1, 7, 6, 3, 2, 4, 5]]

        return np.array(constellation_points)

    def psk_16(self):
        """Returns the specified 16QSK constellation according to [1].
        """
        constellation_points = np.zeros((4, 4), dtype=complex)
        r0 = 1 / np.sqrt(10) * np.array([-1, -3, 1, 3])

        for k in range(len(r0)):
            for m in range(len(r0)):
                constellation_points[k][m] = complex(r0[m], r0[k])
        # Join points to assemble the constellation in [1]
        return constellation_points.flatten()


# Plots the constellations implemented
if __name__ == '__main__':
    """Plots examples of constellations generated using this module."""
    import matplotlib.pyplot as plt

    # Given a function defined above and a title, plots the resulting constellation
    def const_plotter(const_func, bits_p_point, title, *mod_args):
        # Prepare plot
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.set_ylim([-1.4, 1.4])
        ax.set_xlim([-1.4, 1.4])
        ax.set_xlabel('I')
        ax.set_ylabel('Q')
        ax.set_title(title)

        # Plot points
        ax.scatter(const_func(*mod_args).real, const_func(*mod_args).imag)

        # Plot text annotations with symbol in code in decimal base
        for txt, point in enumerate(const_func(*mod_args).flatten()):
            ax.annotate(bin(txt)[2:].zfill(bits_p_point), (point.real + 0.025, point.imag + 0.025))

    const = PolarConstellation()
    const_plotter(const.bpsk, 1, r'$\pi/2$-BPSK RCS2')
    const_plotter(const.qpsk, 2, 'QPSK RCS2')
    const_plotter(const.psk_8, 3, '8PSK RCS2')
    const_plotter(const.psk_16, 4, '16QPSK')
    plt.show()
