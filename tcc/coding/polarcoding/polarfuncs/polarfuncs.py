"""
Base functions for polar coding

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


# pythran export fl(float64, float64)
# pythran export fr(float64, float64, uint8)
# pythran export alpha_right(float64[:], uint8 list)
# pythran export alpha_left(float64[:])
# pythran export betas(uint8 list, uint8 list)
# pythran export compute_node(float64[:], uint64, uint64, uint64[:], uint8[:])
# pythran export encode(uint8[:], uint64)


def fl(a, b):
    return np.sign(a) * np.sign(b) * min(abs(a), abs(b))


def fr(a, b, c):
    return b + (1 - 2 * c) * a


def alpha_right(alphas, beta_arr):
    out_size = alphas.size // 2
    alphas_out = np.zeros(out_size, dtype=np.float64)
    for i in range(0, out_size):
        alphas_out[i] = fr(alphas[i], alphas[i + out_size], beta_arr[i])

    return alphas_out


def alpha_left(alphas):
    out_size = alphas.size // 2
    alphas_out = np.zeros(out_size, dtype=np.float64)
    for i in range(0, out_size):
        alphas_out[i] = fl(alphas[i], alphas[i + out_size])

    return alphas_out


def betas(betas_left, betas_right):
    betas_size = len(betas_left)
    out_size = 2 * betas_size
    betas_out = [0] * out_size
    for i in range(0, betas_size):
        betas_out[i] = betas_left[i] ^ betas_right[i]
        betas_out[i + betas_size] = betas_right[i]

    return betas_out


def compute_node(alphas, level, counter, information, dec_bits):
    """
    Recursive computation of node metrics

    :param alphas: LLR's
    :param level: tree level
    :param counter: leaf counter
    :param information: a list containing the information bit indexes
    :param dec_bits: decoded bits array
    :return: betas
    """

    if alphas.size > 1:
        alpha_l = alpha_left(alphas)
        beta_l = compute_node(alpha_l, level // 2, counter, information, dec_bits)
        alpha_r = alpha_right(alphas, beta_l)
        beta_r = compute_node(alpha_r, level // 2, counter + level // 2,
                              information, dec_bits)
        beta = betas(beta_l, beta_r)

    else:
        if counter in information:
            beta = [0] if alphas[0] > 0 else [1]
            dec_bits[counter] = beta[0]

        else:
            beta = [0]

    return beta


def encode(bits, n):
    stage_input = bits
    stage_output = np.zeros(2 ** n, dtype=np.uint8)
    for i in range(n):
        for j in range(2 ** i):
            stage_output[j * 2 ** (n - i):
                         (j + 1) * 2 ** (n - i)] = betas(stage_input[2 * j * 2 ** (n - 1 - i):
                                                                     (2 * j + 1) * 2 ** (n - 1 - i)],
                                                         stage_input[(2 * j + 1) * 2 ** (n - 1 - i):
                                                                     (2 * j + 2) * 2 ** (n - 1 - i)])

        stage_input = stage_output
        stage_output = np.zeros(2 ** n, dtype=np.uint8)

    return stage_input
