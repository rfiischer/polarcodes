"""
Base functions for polar coding

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

# pythran export fl(float64, float64)
# pythran export fr(float64, float64, uint8)
# pythran export address_list_factory(uint8)
# pythran export node_classifier(uint8, uint32[:], uint32[:])
# not able to export sc_scheduler(uint8, uint8[:])
# pythran export alpha_left(float64[:], uint32[:, :], uint32)
# pythran export alpha_right(float64[:], uint8[:], uint32[:, :], uint32)
# pythran export betas(uint8[:], uint32[:, :], uint32)
# pythran export encode(uint8[:], uint8)
# pythran export sc_decode(float64[:], uint8[:], uint8 list list, uint32[:, :])

# Maximum n for polar coding is 27, resulting on a block sized 134,217,728‬
# This is a consequence of the linear memory addressing used with 32 bit addresses

# All the 2 ** (n + 1) - 1 nodes from the binary tree are represented in a linear data structure where starting
# from node n = 0 the left and right childs are, respectively, 2n + 1 and 2n + 2

# The tree's alphas and betas are stored also on a linear fashion. The first node contains 2 ** n alphas and 2 ** n
# betas, and the tree leaves contain only 1 alpha and 1 beta. The number of nodes doubles when lowering a tree level,
# and each node alphas array size halvens. Therefore, the number of alphas per level is constant, and the total amount
# of alphas on the tree is (n + 1) * 2 ** n. This number provides a way of finding the maximum n with 32 bit
# addresses.


# Base functions
def fl(a, b):
    """
    The left node operation.
    """
    return np.sign(a) * np.sign(b) * min(abs(a), abs(b))


def fr(a, b, c):
    """
    The right node operation. Depends on the node bit.
    """
    return b + (1 - 2 * c) * a


# Factory functions
def address_list_factory(n):
    """
    Build helping array containing relevant data about the tree structure.

    On the retur, each row is a node address (from 0 to 2 ** (n + 1) - 1) and each column represents
        - 0: parent starting addres of alpha or beta array
        - 1: left chlid starting addres of alpha or beta array
        - 2: right child starting addres of alpha or beta array
        - 3: child alpha or beta array size
        - 4: leftmost leaf child start address
        - 5: number of leaf children
        - 6: node level at the tree

    :param n: tree depth
    :return: 2d ndarray
    """
    array_start_list = np.zeros((2 ** (n + 1) - 1, 2), dtype=np.uint32)
    child_array_start_list = np.zeros((2 ** (n + 1) - 1, 7), dtype=np.uint32)

    for i in range(1, n + 1):
        for j in range(2 ** i - 1, 2 * (2 ** i - 1) + 1):
            array_start_list[j, 0] = i * 2 ** n + (j - (2 ** i - 1)) * 2 ** (n - i)
            array_start_list[j, 1] = i

    for i in range(2 ** (n + 1) - 1):

        remaining_steps = (n - array_start_list[i, 1])

        child_array_start_list[i, 0] = array_start_list[i, 0]
        child_array_start_list[i, 4] = array_start_list[(i + 1) * 2 ** remaining_steps - 1, 0]
        child_array_start_list[i, 5] = 2 ** remaining_steps
        child_array_start_list[i, 6] = remaining_steps

        if i < 2 ** n - 1:
            child_array_start_list[i, 1] = array_start_list[2 * i + 1, 0]
            child_array_start_list[i, 2] = array_start_list[2 * (i + 1), 0]
            child_array_start_list[i, 3] = 2 ** (remaining_steps - 1)

    return child_array_start_list


def node_classifier(n, information, frozen):
    """
    Classify each node. 0 means rate-0, 1 means rate-1 and 2 means neither.

    :param n: tree depth
    :param information: list containing information indexes
    :param frozen: list containing frozen indexes
    :return: linear array containing if the node is rate-0, rate-1 or neither
    """
    ilist = [i + 2 ** n - 1 for i in information]
    flist = [f + 2 ** n - 1 for f in frozen]

    rate_sheet = np.zeros(2 ** (n + 1) - 1, dtype=np.uint8)

    for i in range(2 ** n - 1, 2 ** (n + 1) - 1):
        if i in ilist:
            rate_sheet[i] = 1

        elif i in flist:
            rate_sheet[i] = 0

        else:
            rate_sheet[i] = 2

    for j in range(n):
        for i in range(2 ** (n - j - 1) - 1, 2 ** (n - j) - 1):
            if rate_sheet[2 * i + 1] == 1 and rate_sheet[2 * i + 2] == 1:
                rate_sheet[i] = 1

            elif rate_sheet[2 * i + 1] == 0 and rate_sheet[2 * i + 2] == 0:
                rate_sheet[i] = 0

            else:
                rate_sheet[i] = 2

    return rate_sheet


def sc_scheduler(n, node_sheet):
    """
    Define the decoding steps. Each tuple represents (node_address, task).

    Tasks
        - 0: do nothing
        - 1: compute betas from alphas at rate-1 node
        - 2: compute node betas from child betas
        - 3: compute alphas left
        - 4: compute alpha right
    """

    # First column is the alpha flag, second column is the beta flag
    node_flags = np.zeros((2 ** (n + 1) - 1, 2), dtype=np.uint8)

    # Initialize rate-0 nodes and root node
    # Also count the number of rate-1 nodes that need to be get into
    rate1 = 0
    for i in range(2 ** (n + 1) - 1):

        parent = (i - 1) // 2

        if node_sheet[i] == 0:
            node_flags[i, :] = [1, 1]

        if node_sheet[i] == 1 and node_sheet[parent] == 2:
            rate1 += 1

    node_flags[0, 0] = 1

    # Tasks
    tasks = []

    # Start task scheduling
    if node_sheet[0] == 0:
        tasks.append([0, 0])

    elif node_sheet[0] == 1:
        tasks.append([0, 1])

    else:
        nptr = 0
        while rate1 > 0:

            left_child = 2 * nptr + 1
            right_child = 2 * nptr + 2
            parent = (nptr - 1) // 2

            if node_sheet[nptr] == 1:
                tasks.append([nptr, 1])
                node_flags[nptr, 1] = 1
                nptr = parent
                rate1 -= 1

            else:
                if node_flags[left_child, 1] == 1 and node_flags[right_child, 1] == 1:
                    tasks.append([nptr, 2])
                    node_flags[nptr, 1] = 1
                    nptr = parent

                elif node_flags[left_child, 1] == 0:
                    tasks.append([nptr, 3])
                    node_flags[left_child, 0] = 1
                    nptr = left_child

                else:
                    tasks.append([nptr, 4])
                    node_flags[right_child, 0] = 1
                    nptr = right_child

    return tasks


# Decoding functions
def alpha_left(alpha_array, address_list, node_id):
    """
    Compute the left alphas.
    """
    start_h = address_list[node_id, 0]
    start_l = address_list[node_id, 1]
    step = address_list[node_id, 3]
    for i in range(0, step):
        alpha_array[start_l + i] = fl(alpha_array[start_h + i],
                                      alpha_array[start_h + i + step])


def alpha_right(alpha_array, beta_array, address_list, node_id):
    """
    Compute the right alphas.
    """
    start_h = address_list[node_id, 0]
    start_ll = address_list[node_id, 1]
    start_lr = address_list[node_id, 2]
    step = address_list[node_id, 3]
    for i in range(0, step):
        alpha_array[start_lr + i] = fr(alpha_array[start_h + i],
                                       alpha_array[start_h + i + step],
                                       beta_array[start_ll + i])


def betas(beta_array, address_list, node_id):
    """
    Compute the betas.
    """
    start_h = address_list[node_id, 0]
    start_ll = address_list[node_id, 1]
    start_lr = address_list[node_id, 2]
    step = address_list[node_id, 3]

    for i in range(0, step):
        beta_array[start_h + i] = beta_array[start_ll + i] ^ beta_array[start_lr + i]
        beta_array[start_h + i + step] = beta_array[start_lr + i]


# Encoding function
def encode(bits, n):
    """
    Perform efficient polar encoding.
    """
    stage_input = np.copy(bits)
    for i in range(n):
        for j in range(2 ** i):
            for k in range(2 ** (n - i - 1)):
                stage_input[j * 2 ** (n - i) + k] = stage_input[j * 2 ** (n - i) + k] ^ \
                                                     stage_input[(2 * j + 1) * 2 ** (n - i - 1) + k]

    return stage_input


# SC decoding function
def sc_decode(alpha_array, beta_array, tasks, address_list):
    """
    Perform the SC polar decoding.
    """

    for task in tasks:

        if task[1] == 1:
            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]
            level = address_list[task[0], 6]
            start_child = address_list[task[0], 4]
            node_betas = np.array([0 if alpha > 0 else 1 for alpha in alpha_array[start_h: start_h + size]],
                                  dtype=np.uint8)
            if size > 1:
                leaf_betas = encode(node_betas, level)

            else:
                leaf_betas = node_betas

            beta_array[start_child: start_child + size] = leaf_betas
            beta_array[start_h: start_h + size] = node_betas

        elif task[1] == 2:
            betas(beta_array, address_list, task[0])

        elif task[1] == 3:
            alpha_left(alpha_array, address_list, task[0])

        elif task[1] == 4:
            alpha_right(alpha_array, beta_array, address_list, task[0])

    return beta_array[address_list[0, 4]:]


# def phi(a, b, u):
#     if (np.sign(b) == 1 and u == 0) or (np.sign(b) == -1 and u == 1):
#         out = a
#
#     else:
#         out = a + np.abs(b)
#
#     return out
#
#
# def child_list_maker(n):
#     n = int(n)
#     output = [[] for _ in range(n + 1)]
#     for i in range(n + 1):
#         for j in range(2 ** i):
#             output[n - i].append([k for k in range(j * 2 ** (n - i), j * 2 ** (n - i) + 2 ** (n - i))])
#
#     return output
#
#
#
#
# def get_next_alpha(alphas, beta_tree, beta_sheet, level, counter):
#     if beta_sheet[level - 1][2 * counter]:
#         alpha_r = alpha_right(alphas, beta_tree[level - 1][2 * counter])
#         if level == 1:
#             alpha = alpha_r
#
#         else:
#             alpha = get_next_alpha(alpha_r, beta_tree, beta_sheet, level - 1, 2 * counter + 1)
#
#     else:
#         alpha_l = alpha_left(alphas)
#         if level == 1:
#             alpha = alpha_l
#
#         else:
#             alpha = get_next_alpha(alpha_l, beta_tree, beta_sheet, level - 1, 2 * counter)
#
#     return alpha
#
#
# def update_betas(n, beta_tree, beta_sheet):
#     n = int(n)
#     for i in range(1, n + 1):
#         for j in range(2 ** (n - i)):
#             if beta_sheet[i - 1][2 * j] and beta_sheet[i - 1][2 * j + 1] and (not beta_sheet[i][j]):
#                 beta_tree[i][j] = betas(beta_tree[i - 1][2 * j], beta_tree[i - 1][2 * j + 1])
#                 beta_sheet[i][j] = True
#
#     return beta_tree, beta_sheet
#
#
# def beta_maker(n, node_sheet):
#     n = int(n)
#     beta_tree = [[] for _ in range(n + 1)]
#     beta_sheet = [[] for _ in range(n + 1)]
#     for i in range(n + 1):
#         for j in range(2 ** i):
#             beta_tree[n - i].append([0] * 2 ** (n - i))
#             if node_sheet[n - i][j] == 0:
#                 beta_sheet[n - i].append(True)
#
#             else:
#                 beta_sheet[n - i].append(False)
#
#     return beta_tree, beta_sheet
#
#
# def list_decode(n, list_size, alphas, information, beta_trees, beta_sheet):
#     paths = [0]
#     metrics = [0]
#
#     for index in sorted(information):
#
#         next_metrics = []
#
#         for path in paths:
#             alpha = get_next_alpha(alphas, beta_trees[path], beta_sheet, n, 0)
#             pm0 = phi(metrics[path], alpha, 0)
#             pm1 = phi(metrics[path], alpha, 1)
#
#             next_metrics.extend([[0, path, pm0], [1, path, pm1]])
#
#         next_metrics_sorted = [item for item in sorted(next_metrics, key=lambda item: item[2])]
#
#         num_final_paths = len(next_metrics_sorted) if len(next_metrics_sorted) <= list_size else list_size
#         final_paths = next_metrics_sorted[:num_final_paths]
#
#         metrics = []
#         new_beta_trees = []
#         old_beta_sheet = beta_sheet
#         beta_sheet[0][index] = True
#         for path in final_paths:
#             new_beta_tree = [[[item for item in items] for items in parent] for parent in beta_trees[path[1]]]
#             new_beta_tree[0][index] = [path[0]]
#
#             new_beta_tree, beta_sheet = update_betas(n, new_beta_tree, old_beta_sheet)
#
#             new_beta_trees.append(new_beta_tree)
#             metrics.append(path[2])
#
#         beta_trees = new_beta_trees
#
#         paths = [i for i in range(num_final_paths)]
#
#     decoded_bits = np.array([bit[0] for bit in beta_trees[0][0]], dtype=np.uint8)
#
#     return decoded_bits
#
#
