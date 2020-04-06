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
# pythran export node_classifier(uint64, uint64[:], uint64[:])
# pythran export resolve_node(float64[:], uint64, uint64, uint8[:], uint64[:, :])
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


def node_classifier(n, information, frozen):
    iset = set(information)
    fset = set(frozen)

    rate_sheet = np.zeros((n + 1, 2 ** n), dtype=np.uint8)
    for i in range(n, -1, -1):
        for j in range(2 ** i):
            children = {k for k in range(j * 2 ** (n - i), j * 2 ** (n - i) + 2 ** (n - i))}

            if children.issubset(iset):
                rate_sheet[n - i, j] = 1

            elif children.issubset(fset):
                rate_sheet[n - i, j] = 0

            else:
                rate_sheet[n - i, j] = 2

    return rate_sheet


def resolve_node(alphas, level, counter, dec_bits, node_sheet):
    """
    Recursive computation of node metrics

    :param alphas: LLR's
    :param level: tree level
    :param counter: leaf counter
    :param dec_bits: decoded bits array
    :param node_sheet: if node is rate-0, rate-1 or neither
    :return: betas
    """

    # rate-0 node
    if node_sheet[level, counter] == 0:
        beta = [0] * 2 ** level

    # rate-1 node
    elif node_sheet[level, counter] == 1:
        beta = [0 if alpha > 0 else 1 for alpha in alphas]
        children = [k for k in range(counter * 2 ** level, (counter + 1) * 2 ** level)]
        dec_bits[children] = encode(beta, level)

    # neither
    else:
        if node_sheet[level - 1, 2 * counter] == 0:
            beta_l = [0] * 2 ** (level - 1)

        elif node_sheet[level - 1, 2 * counter] == 1:
            alpha_l = alpha_left(alphas)
            beta_l = [0 if alpha > 0 else 1 for alpha in alpha_l]
            children = [k for k in range(2 * counter * 2 ** (level - 1), (2 * counter + 1) * 2 ** (level - 1))]
            dec_bits[children] = encode(beta_l, level - 1)

        else:
            alpha_l = alpha_left(alphas)
            beta_l = resolve_node(alpha_l, level - 1, 2 * counter, dec_bits, node_sheet)

        if node_sheet[level - 1, 2 * counter + 1] == 0:
            beta_r = [0] * 2 ** (level - 1)

        elif node_sheet[level - 1, 2 * counter + 1] == 1:
            alpha_r = alpha_right(alphas, beta_l)
            beta_r = [0 if alpha > 0 else 1 for alpha in alpha_r]
            children = [k for k in range((2 * counter + 1) * 2 ** (level - 1), 2 * (counter + 1) * 2 ** (level - 1))]
            dec_bits[children] = encode(beta_r, level - 1)

        else:
            alpha_r = alpha_right(alphas, beta_l)
            beta_r = resolve_node(alpha_r, level - 1, 2 * counter + 1, dec_bits, node_sheet)

        beta = betas(beta_l, beta_r)

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
