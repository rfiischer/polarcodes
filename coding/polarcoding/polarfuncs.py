"""
Base functions for polar coding

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import numba as nb


__all__ = ['_fl', '_fr', '_alpha_right', '_alpha_left', '_betas']


@nb.njit("float64(float64, float64)")
def _fl(a, b):
    return np.log((1 + np.exp(a + b)) / (np.exp(a) + np.exp(b)))


@nb.njit("float64(float64, float64, float64)")
def _fr(a, b, c):
    return b + (1 - 2 * c) * a


@nb.njit("float64[:](float64[:], uint8[:])")
def _alpha_right(alphas, betas):
    out_size = alphas.size // 2
    alphas_out = np.zeros(out_size)
    for i in nb.prange(0, out_size):
        alphas_out[i] = _fr(alphas[i], alphas[i + out_size], betas[i])

    return alphas_out


@nb.njit("float64[:](float64[:])")
def _alpha_left(alphas):
    out_size = alphas.size // 2
    alphas_out = np.zeros(out_size)
    for i in range(0, out_size):
        alphas_out[i] = _fl(alphas[i], alphas[i + out_size])

    return alphas_out


@nb.njit("uint8[:](uint8[:], uint8[:])")
def _betas(betas_left, betas_right):
    betas_size = betas_left.size
    out_size = 2 * betas_size
    betas_out = np.zeros(out_size, dtype=np.uint8)
    for i in nb.prange(0, betas_size):
        betas_out[i] = betas_left[i] ^ betas_right[i]
        betas_out[i + betas_size] = betas_right[i]

    return betas_out
