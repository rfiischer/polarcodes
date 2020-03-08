"""
Base functions for polar coding

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


# pythran export fl(float64, float64)
# pythran export fr(float64, float64, uint8)
# pythran export alpha_right(float64[:], uint8[:])
# pythran export alpha_left(float64[:])
# pythran export betas(uint8[:], uint8[:])
# pythran export compute_node(float64[:], uint64, uint64, uint64[:], uint8[:])


def fl(a, b):
    return np.log((1 + np.exp(a + b)) / (np.exp(a) + np.exp(b)))


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
    betas_size = betas_left.size
    out_size = 2 * betas_size
    betas_out = np.zeros(out_size, dtype=np.uint8)
    for i in range(0, betas_size):
        betas_out[i] = betas_left[i] ^ betas_right[i]
        betas_out[i + betas_size] = betas_right[i]

    print(np.float64(betas_out))
    return betas_out


def compute_node(alphas, level, counter, information, dec_bits):
    """

    :param alphas: LLR's
    :param level: tree level
    :param counter: leaf counter
    :param information: a list containing the information bit indexes
    :param dec_bits: decoded bits array
    :return: betas
    """

    if alphas.size > 1:
        alpha_l = alpha_left(alphas)
        beta_l = compute_node(alpha_l, np.uint64(level / 2), np.uint64(counter), information, dec_bits)
        alpha_r = alpha_right(alphas, beta_l)
        beta_r = compute_node(alpha_r, np.uint64(level / 2), np.uint64(counter + level / 2),
                              information, dec_bits)
        beta = betas(beta_l, beta_r)

        print('node')
        print(beta.size)
        print(np.float64(beta))

    else:
        if counter in information:
            beta = np.array([0], dtype=np.uint8) if alphas[0] > 0 else np.array([1], dtype=np.uint8)
            dec_bits[counter] = beta[0]

        else:
            beta = np.array([0], dtype=np.uint8)

        print('leaf')

    print(np.float64(beta))
    print('\n')
    return beta
