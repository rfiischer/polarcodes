"""
Base functions for polar coding

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np


# pythran export fl(float64, float64)
# ythran export fr(float64, float64, uint8)
"""# ythran export alpha_right(float64[:], uint8 list)
# ythran export alpha_left(float64[:])
# ythran export phi(float64, float64, uint8)
# ythran export betas(uint8 list, uint8 list)
# thran export node_classifier(uint64, uint64[:], uint64[:])
# thran export child_list_maker(uint64)
# thran export resolve_node(float64[:], uint64, uint64, uint8[:], uint8[:, :], uint64 list list list)
# ythran export get_next_alpha(float64[:], uint8 list list list, bool list list, uint64, uint64)
# ythran export update_betas(uint64, uint8 list list list, bool list list)
# thran export beta_maker(uint64, uint8[:, :])
# thran export list_decode(uint64, uint64, float64[:], uint64[:], uint8 list list list list, bool list list)
# thran export encode(uint8[:], uint64)"""


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


def phi(a, b, u):
    if (np.sign(b) == 1 and u == 0) or (np.sign(b) == -1 and u == 1):
        out = a

    else:
        out = a + np.abs(b)

    return out


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

    rate_sheet = np.zeros((int(n + 1), int(2 ** n)), dtype=np.uint8)
    for i in range(n + 1):
        for j in range(2 ** i):
            children = {k for k in range(j * 2 ** (n - i), j * 2 ** (n - i) + 2 ** (n - i))}

            if children.issubset(iset):
                rate_sheet[int(n - i), j] = 1

            elif children.issubset(fset):
                rate_sheet[int(n - i), j] = 0

            else:
                rate_sheet[int(n - i), j] = 2

    return rate_sheet


def child_list_maker(n):
    n = int(n)
    output = [[] for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(2 ** i):
            output[n - i].append([k for k in range(j * 2 ** (n - i), j * 2 ** (n - i) + 2 ** (n - i))])

    return output


def resolve_node(alphas, level, counter, dec_bits, node_sheet, child_list):
    """
    Recursive computation of node metrics

    :param alphas: LLR's
    :param level: tree level
    :param counter: leaf counter
    :param dec_bits: decoded bits array
    :param node_sheet: if node is rate-0, rate-1 or neither
    :param child_list: given a level and a node, give a list of the child leaves
    :return: betas
    """

    # rate-0 node
    if node_sheet[level, counter] == 0:
        beta = [0] * 2 ** level

    # rate-1 node
    elif node_sheet[level, counter] == 1:
        beta = [0 if alpha > 0 else 1 for alpha in alphas]
        dec_bits[child_list[level][counter]] = encode(beta, level)

    # neither
    else:
        if node_sheet[level - 1, 2 * counter] == 0:
            beta_l = [0] * 2 ** (level - 1)

        elif node_sheet[level - 1, 2 * counter] == 1:
            alpha_l = alpha_left(alphas)
            beta_l = [0 if alpha > 0 else 1 for alpha in alpha_l]
            dec_bits[child_list[level - 1][2 * counter]] = encode(beta_l, level - 1)

        else:
            alpha_l = alpha_left(alphas)
            beta_l = resolve_node(alpha_l, level - 1, 2 * counter, dec_bits, node_sheet, child_list)

        if node_sheet[level - 1, 2 * counter + 1] == 0:
            beta_r = [0] * 2 ** (level - 1)

        elif node_sheet[level - 1, 2 * counter + 1] == 1:
            alpha_r = alpha_right(alphas, beta_l)
            beta_r = [0 if alpha > 0 else 1 for alpha in alpha_r]
            dec_bits[child_list[level - 1][2 * counter + 1]] = encode(beta_r, level - 1)

        else:
            alpha_r = alpha_right(alphas, beta_l)
            beta_r = resolve_node(alpha_r, level - 1, 2 * counter + 1, dec_bits, node_sheet, child_list)

        beta = betas(beta_l, beta_r)

    return beta


def get_next_alpha(alphas, beta_tree, beta_sheet, level, counter):
    if beta_sheet[level - 1][2 * counter]:
        alpha_r = alpha_right(alphas, beta_tree[level - 1][2 * counter])
        if level == 1:
            alpha = alpha_r

        else:
            alpha = get_next_alpha(alpha_r, beta_tree, beta_sheet, level - 1, 2 * counter + 1)

    else:
        alpha_l = alpha_left(alphas)
        if level == 1:
            alpha = alpha_l

        else:
            alpha = get_next_alpha(alpha_l, beta_tree, beta_sheet, level - 1, 2 * counter)

    return alpha


def update_betas(n, beta_tree, beta_sheet):
    n = int(n)
    for i in range(1, n + 1):
        for j in range(2 ** (n - i)):
            if beta_sheet[i - 1][2 * j] and beta_sheet[i - 1][2 * j + 1] and (not beta_sheet[i][j]):
                beta_tree[i][j] = betas(beta_tree[i - 1][2 * j], beta_tree[i - 1][2 * j + 1])
                beta_sheet[i][j] = True

    return beta_tree, beta_sheet


def beta_maker(n, node_sheet):
    n = int(n)
    beta_tree = [[] for _ in range(n + 1)]
    beta_sheet = [[] for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(2 ** i):
            beta_tree[n - i].append([0] * 2 ** (n - i))
            if node_sheet[n - i][j] == 0:
                beta_sheet[n - i].append(True)

            else:
                beta_sheet[n - i].append(False)

    return beta_tree, beta_sheet


def list_decode(n, list_size, alphas, information, beta_trees, beta_sheet):
    paths = [0]
    metrics = [0]

    for index in sorted(information):

        next_metrics = []

        for path in paths:
            alpha = get_next_alpha(alphas, beta_trees[path], beta_sheet, n, 0)
            pm0 = phi(metrics[path], alpha, 0)
            pm1 = phi(metrics[path], alpha, 1)

            next_metrics.extend([[0, path, pm0], [1, path, pm1]])

        next_metrics_sorted = [item for item in sorted(next_metrics, key=lambda item: item[2])]

        num_final_paths = len(next_metrics_sorted) if len(next_metrics_sorted) <= list_size else list_size
        final_paths = next_metrics_sorted[:num_final_paths]

        metrics = []
        new_beta_trees = []
        old_beta_sheet = beta_sheet
        beta_sheet[0][index] = True
        for path in final_paths:
            new_beta_tree = [[[item for item in items] for items in parent] for parent in beta_trees[path[1]]]
            new_beta_tree[0][index] = [path[0]]

            new_beta_tree, beta_sheet = update_betas(n, new_beta_tree, old_beta_sheet)

            new_beta_trees.append(new_beta_tree)
            metrics.append(path[2])

        beta_trees = new_beta_trees

        paths = [i for i in range(num_final_paths)]

    decoded_bits = np.array([bit[0] for bit in beta_trees[0][0]], dtype=np.uint8)

    return decoded_bits


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
