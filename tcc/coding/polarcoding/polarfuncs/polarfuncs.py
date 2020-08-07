"""
Base functions for polar coding.

Note:
    Maximum n for polar coding is 27, resulting on a block sized 134,217,728‬. This is a consequence of the linear
    memory addressing used with 32 bit node addresses.

    All the 2 ** (n + 1) - 1 nodes from the binary tree are represented in a linear data structure where starting
    from node n = 0 the left and right childs are, respectively, 2n + 1 and 2n + 2.

    The tree's alphas and betas are stored also on a linear fashion. The first node contains 2 ** n alphas and 2 ** n
    betas, and the tree leaves contain only 1 alpha and 1 beta. The number of nodes doubles when lowering a tree level,
    and each node alphas array size halvens. Therefore, the number of alphas per level is constant, and the total amount
    of alphas on the tree is (n + 1) * 2 ** n. This number provides a way of finding the maximum n with 32 bit
    addresses.

Created on 06/03/2020 16:52

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np

# pythran export fl(float64, float64)
# pythran export fr(float64, float64, uint8)

# pythran export address_list_factory(uint8)
# pythran export ssc_node_classifier(uint8, uint32[:], uint32[:])
# pythran export fast_ssc_node_classifier(uint8, uint32[:], uint32[:])
# not able to export ssc_scheduler(uint8, uint8[:])
# not able to export fast_ssc_scheduler(uint8, uint8[:])
# not able to export sscl_spc_scheduler(uint8, uint8[:])

# pythran export alpha_left(float64[:], uint32[:, :], uint32)
# pythran export alpha_right(float64[:], uint8[:], uint32[:, :], uint32)
# pythran export betas(uint8[:], uint32[:, :], uint32)

# pythran export encode(uint8[:], uint8)

# pythran export ssc_decode(uint8, float64[:], uint32 list list, uint32[:, :])
# pythran export fast_ssc_decode(uint8, float64[:], uint32 list list, uint32[:, :])
# pythran export sscl_spc_decode(uint8, uint8, float64[:], uint32 list list, uint32[:, :])

# pythran export rate_1(uint8, uint8, float64[:, :], uint8[:, :], float64[:], uint32, uint32[:, :])
# pythran export rep(uint8, uint8, float64[:, :], uint8[:, :], float64[:], uint32, uint32[:, :])
# pythran export spc(uint8, uint8, float64[:, :], uint8[:, :], float64[:], uint32, uint32[:, :])
# pythran export rate_0(uint8, float64[:, :], float64[:], uint32, uint32[:, :])


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

    On the return, each row is a node address (from 0 to 2 ** (n + 1) - 1) and each column represents
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


def ssc_node_classifier(n, information, frozen):
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
            # This case should never be reached
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


def fast_ssc_node_classifier(n, information, frozen):
    """
    Classify each node.

    - 0: rate-0
    - 1: rate-1
    - 2: REP
    - 3: SPC
    - 4: neither

    :param n: tree depth
    :param information: list containing information indexes
    :param frozen: list containing frozen indexes
    :return: linear array containing the node information
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
            # This case should never be reached
            rate_sheet[i] = 4

    for j in range(n):
        for i in range(2 ** (n - j - 1) - 1, 2 ** (n - j) - 1):
            if rate_sheet[2 * i + 1] == 1 and rate_sheet[2 * i + 2] == 1:
                rate_sheet[i] = 1

            elif rate_sheet[2 * i + 1] == 0 and rate_sheet[2 * i + 2] == 0:
                rate_sheet[i] = 0

            elif rate_sheet[2 * i + 1] == 0 and rate_sheet[2 * i + 2] == 2:
                rate_sheet[i] = 2

            elif j == 0 and rate_sheet[2 * i + 1] == 0 and rate_sheet[2 * i + 2] == 1:
                rate_sheet[i] = 2

            elif j == 1 and rate_sheet[2 * i + 1] == 2 and rate_sheet[2 * i + 2] == 1:
                rate_sheet[i] = 3

            elif j > 1 and rate_sheet[2 * i + 1] == 3 and rate_sheet[2 * i + 2] == 1:
                rate_sheet[i] = 3

            else:
                rate_sheet[i] = 4

    return rate_sheet


def ssc_scheduler(n, node_sheet):
    """
    Define the decoding steps for the sublinear SC decoder. Each tuple represents (node_address, task).
    The schedule ends when the root node betas are obtainded.

    Tasks
        - 0: do nothing
        - 1: compute betas from alphas at rate-1 node
        - 2: compute node betas from child betas
        - 3: compute alphas left
        - 4: compute alpha right

    :param n: tree depth
    :param node_sheet: array containing the node classification, obtained by the node classifiers
    :return: 2d array, where the first column is the node address and the second column is the operation code
    """

    # Flag that states whether the node is completely decoded or not
    node_flags = np.zeros(2 ** (n + 1) - 1, dtype=np.uint8)

    # Initialize rate-0 nodes
    for i in range(2 ** (n + 1) - 1):
        if node_sheet[i] == 0:
            node_flags[i] = 1

    # Tasks
    tasks = []

    # Start task scheduling
    if node_sheet[0] == 0:
        tasks.append([0, 0])

    elif node_sheet[0] == 1:
        tasks.append([0, 1])

    else:
        nptr = 0
        stop = False
        while not stop:

            left_child = 2 * nptr + 1
            right_child = 2 * nptr + 2
            parent = (nptr - 1) // 2

            if node_sheet[nptr] == 1:
                tasks.append([nptr, 1])
                node_flags[nptr] = 1
                nptr = parent

            else:
                if node_flags[left_child] == 1 and node_flags[right_child] == 1:
                    tasks.append([nptr, 2])
                    node_flags[nptr] = 1
                    nptr = parent
                    if nptr < 0:
                        stop = True

                elif node_flags[left_child] == 0:
                    tasks.append([nptr, 3])
                    nptr = left_child

                else:
                    tasks.append([nptr, 4])
                    nptr = right_child

    return tasks


def fast_ssc_scheduler(n, node_sheet):
    """
    Define the decoding steps for the Fast-SSC. Each tuple represents (node_address, task).
    Suitable for systematic encoding, since the schedule ends with the betas at the root node.

    Tasks
        - 0: do nothing
        - 1: compute betas from alphas at rate-1 node
        - 2: compute betas from alphas at REP node
        - 3: compute betas from alphas at SPC node
        - 4: compute node betas from child betas
        - 5: compute alphas left
        - 6: compute alpha right

    :param n: tree depth
    :param node_sheet: array containing the node classification, obtained by the node classifiers
    :return: 2d array, where the first column is the node address and the second column is the operation code
    """

    # Flag that states whether the node is completely decoded or not
    node_flags = np.zeros(2 ** (n + 1) - 1, dtype=np.uint8)

    # Initialize rate-0 nodes
    for i in range(2 ** (n + 1) - 1):
        if node_sheet[i] == 0:
            node_flags[i] = 1

    # Tasks
    tasks = []

    # Start task scheduling
    if node_sheet[0] != 4:
        tasks.append([0, node_sheet[0]])

    else:
        nptr = 0
        stop = False
        while not stop:

            left_child = 2 * nptr + 1
            right_child = 2 * nptr + 2
            parent = (nptr - 1) // 2

            if node_sheet[nptr] == 1:
                tasks.append([nptr, 1])
                node_flags[nptr] = 1
                nptr = parent

            elif node_sheet[nptr] == 2:
                tasks.append([nptr, 2])
                node_flags[nptr] = 1
                nptr = parent

            elif node_sheet[nptr] == 3:
                tasks.append([nptr, 3])
                node_flags[nptr] = 1
                nptr = parent

            else:
                if node_flags[left_child] == 1 and node_flags[right_child] == 1:
                    tasks.append([nptr, 4])
                    node_flags[nptr] = 1
                    nptr = parent
                    if nptr < 0:
                        stop = True

                elif node_flags[left_child] == 0:
                    tasks.append([nptr, 5])
                    nptr = left_child

                else:
                    tasks.append([nptr, 6])
                    nptr = right_child

    return tasks


def sscl_spc_scheduler(n, node_sheet):
    """
    Define the decoding steps for the SSCL-SPC decoding. Each tuple represents (node_address, task).
    Suitable for systematic encoding, since the schedule ends with the betas at the root node.

    Tasks
        - 0: do nothing
        - 1: compute betas from alphas at rate-1 node
        - 2: compute betas from alphas at REP node
        - 3: compute betas from alphas at SPC node
        - 4: update path metrics at rate-0 node
        - 5: compute node betas from child betas
        - 6: compute alphas left
        - 7: compute alpha right

    :param n: tree depth
    :param node_sheet: array containing the node classification, obtained by the node classifiers
    :return: 2d array, where the first column is the node address and the second column is the operation code
    """

    # Flag that states whether the node is completely decoded or not
    node_flags = np.zeros(2 ** (n + 1) - 1, dtype=np.uint8)

    # Tasks
    tasks = []

    # Start task scheduling
    if node_sheet[0] != 4:
        tasks.append([0, node_sheet[0]])

    else:
        nptr = 0
        stop = False
        while not stop:

            left_child = 2 * nptr + 1
            right_child = 2 * nptr + 2
            parent = (nptr - 1) // 2

            if node_sheet[nptr] == 0:
                tasks.append([nptr, 4])
                node_flags[nptr] = 1
                nptr = parent

            elif node_sheet[nptr] == 1:
                tasks.append([nptr, 1])
                node_flags[nptr] = 1
                nptr = parent

            elif node_sheet[nptr] == 2:
                tasks.append([nptr, 2])
                node_flags[nptr] = 1
                nptr = parent

            elif node_sheet[nptr] == 3:
                tasks.append([nptr, 3])
                node_flags[nptr] = 1
                nptr = parent

            else:
                if node_flags[left_child] == 1 and node_flags[right_child] == 1:
                    tasks.append([nptr, 5])
                    node_flags[nptr] = 1
                    nptr = parent
                    if nptr < 0:
                        stop = True

                elif node_flags[left_child] == 0:
                    tasks.append([nptr, 6])
                    nptr = left_child

                else:
                    tasks.append([nptr, 7])
                    nptr = right_child

    return tasks


# Decoding functions
def alpha_left(alpha_array, address_list, node_id):
    """
    Compute the left alphas.

    :param alpha_array: linear array containing the alphas
    :param address_list: helper address list
    :param node_id: base node address
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

    :param alpha_array: linear array containing the alphas
    :param beta_array: linear array containing the betas
    :param address_list: helper address list
    :param node_id: base node address
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

    :param beta_array: linear array containing the betas
    :param address_list: helper address list
    :param node_id: base node address
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

    :param bits: bits to encode
    :param n: tree depth
    :return: encoded bits
    """
    stage_input = np.copy(bits)
    for i in range(n):
        for j in range(2 ** i):
            for k in range(2 ** (n - i - 1)):
                stage_input[j * 2 ** (n - i) + k] = stage_input[j * 2 ** (n - i) + k] ^ \
                                                     stage_input[(2 * j + 1) * 2 ** (n - i - 1) + k]

    return stage_input


# Decoding functions
def ssc_decode(n, alphas, tasks, address_list):
    """
    Perform the SSC polar decoding.

    Considers that systematic encoding is used.

    :param n: tree depth
    :param alphas: channel alphas
    :param tasks: tasks from task scheduler
    :param address_list: helper address list
    :return: decoded bits
    """

    size = (n + 1) * 2 ** n
    alpha_array = np.zeros(size, dtype=np.float64)
    alpha_array[:2 ** n] = alphas
    beta_array = np.zeros(size, dtype=np.uint8)

    for task in tasks:

        if task[1] == 1:
            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]
            node_betas = np.array([0 if alpha > 0 else 1 for alpha in alpha_array[start_h: start_h + size]],
                                  dtype=np.uint8)

            beta_array[start_h: start_h + size] = node_betas

        elif task[1] == 2:
            betas(beta_array, address_list, task[0])

        elif task[1] == 3:
            alpha_left(alpha_array, address_list, task[0])

        elif task[1] == 4:
            alpha_right(alpha_array, beta_array, address_list, task[0])

    return beta_array[:2 ** n]


def fast_ssc_decode(n, alphas, tasks, address_list):
    """
    Perform the Fast-SSC polar decoding.

    Suitable for systematic encoding.

    :param n: tree depth
    :param alphas: channel alphas
    :param tasks: tasks from task scheduler
    :param address_list: helper address list
    :return: decoded bits
    """

    size = (n + 1) * 2 ** n
    alpha_array = np.zeros(size, dtype=np.float64)
    alpha_array[:2 ** n] = alphas
    beta_array = np.zeros(size, dtype=np.uint8)

    for task in tasks:

        if task[1] == 1:
            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]
            node_betas = np.array([0 if alpha > 0 else 1 for alpha in alpha_array[start_h: start_h + size]],
                                  dtype=np.uint8)

            beta_array[start_h: start_h + size] = node_betas

        elif task[1] == 2:
            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]

            decision_llr = np.sum(alpha_array[start_h: start_h + size])
            decision_bit = 0 if decision_llr > 0 else 1

            beta_array[start_h: start_h + size] = decision_bit * np.ones(size, dtype=np.uint8)

        elif task[1] == 3:
            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]
            node_betas = np.array([0 if alpha > 0 else 1 for alpha in alpha_array[start_h: start_h + size]],
                                  dtype=np.uint8)

            parity = np.sum(node_betas) % 2

            min_idx = np.argmin(np.abs(alpha_array[start_h: start_h + size]))

            node_betas[min_idx] = (node_betas[min_idx] + parity) % 2

            beta_array[start_h: start_h + size] = node_betas

        elif task[1] == 4:
            betas(beta_array, address_list, task[0])

        elif task[1] == 5:
            alpha_left(alpha_array, address_list, task[0])

        elif task[1] == 6:
            alpha_right(alpha_array, beta_array, address_list, task[0])

    return beta_array[:2 ** n]


def sscl_spc_decode(n, list_size, alphas, tasks, address_list):
    """
    Perform systematic list decoding.

    :param n: tree depth
    :param list_size: maximum list size
    :param alphas: channel alphas
    :param tasks: tasks from task scheduler
    :param address_list: helper address list
    :return: decoded bits
    """

    size = (n + 1) * 2 ** n
    alpha_array = np.zeros((list_size, size), dtype=np.float64)
    alpha_array[0, :2 ** n] = alphas
    beta_array = np.zeros((list_size, size), dtype=np.uint8)

    metrics = np.zeros(list_size, dtype=np.float64)
    num_paths = 1

    for task in tasks:
        if task[1] == 1:

            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]

            for i in range(size):

                num_final_paths = min(2 * num_paths, list_size)
                next_metrics = np.zeros((2 * num_paths, 3), dtype=np.float64)

                for idx in range(num_paths):
                    alpha = alpha_array[idx, start_h + i]
                    metric = metrics[idx]

                    pm0 = metric + 1 / 2 * (abs(alpha) - alpha)
                    pm1 = metric + 1 / 2 * (abs(alpha) + alpha)

                    next_metrics[2 * idx, :] = [idx, 0.0, pm0]
                    next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1]

                metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
                final_paths = next_metrics[metrics_order]

                old_alpha_array = np.copy(alpha_array)
                old_beta_array = np.copy(beta_array)
                for idx, path in enumerate(final_paths):
                    old_idx = int(path[0])
                    value = np.uint8(path[1])
                    metric = path[2]

                    alpha_array[idx, :] = old_alpha_array[old_idx, :]

                    beta_array[idx, :] = old_beta_array[old_idx, :]
                    beta_array[idx, int(start_h) + i] = value

                    metrics[idx] = metric

                num_paths = num_final_paths

        elif task[1] == 2:

            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]

            num_final_paths = min(2 * num_paths, list_size)
            next_metrics = np.zeros((2 * num_paths, 3), dtype=np.float64)

            for idx in range(num_paths):
                alphas = alpha_array[idx, start_h:start_h + size]
                metric = metrics[idx]

                pm0 = metric + 1 / 2 * np.sum(np.abs(alphas) - alphas)
                pm1 = metric + 1 / 2 * np.sum(np.abs(alphas) + alphas)

                next_metrics[2 * idx, :] = [idx, 0.0, pm0]
                next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1]

            metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
            final_paths = next_metrics[metrics_order]

            old_alpha_array = np.copy(alpha_array)
            old_beta_array = np.copy(beta_array)
            for idx, path in enumerate(final_paths):
                old_idx = int(path[0])
                value = np.uint8(path[1])
                metric = path[2]

                alpha_array[idx, :] = old_alpha_array[old_idx, :]

                beta_array[idx, :] = old_beta_array[old_idx, :]
                beta_array[idx, start_h:start_h + size] = value * np.ones(size, dtype=np.uint8)

                metrics[idx] = metric

            num_paths = num_final_paths

        elif task[1] == 3:

            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]

            node_alphas = alpha_array[:, start_h: start_h + size]

            idx_min = np.argmin(np.abs(node_alphas), axis=-1).flatten()
            parity_array = np.ones(node_alphas.shape, dtype=np.uint8)
            parity_array[node_alphas >= 0] = 0
            parity = np.sum(parity_array, axis=-1) % 2
            min_alphas = np.min(np.abs(node_alphas), axis=-1)
            acc_parity = np.zeros(idx_min.shape, dtype=np.uint8)

            for idx in range(num_paths):
                metrics[idx] = metrics[idx] + min_alphas[idx] if parity[idx] else metrics[idx]

            for i in range(size - 1):

                num_final_paths = min(2 * num_paths, list_size)
                next_metrics = np.zeros((2 * num_paths, 4), dtype=np.float64)

                for idx in range(num_paths):
                    if idx_min[idx] <= i:
                        i_bit = i + 1

                    else:
                        i_bit = i

                    alpha = alpha_array[idx, start_h + i_bit]
                    metric = metrics[idx]

                    pm0 = metric + abs(alpha) + (1 - 2 * parity[idx]) * min_alphas[idx] \
                        if alpha < 0 else metric
                    pm1 = metric + abs(alpha) + (1 - 2 * parity[idx]) * min_alphas[idx] \
                        if alpha >= 0 else metric

                    next_metrics[2 * idx, :] = [idx, 0.0, pm0, i_bit]
                    next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1, i_bit]

                metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
                final_paths = next_metrics[metrics_order]

                old_alpha_array = np.copy(alpha_array)
                old_beta_array = np.copy(beta_array)
                for idx, path in enumerate(final_paths):
                    old_idx = int(path[0])
                    value = np.uint8(path[1])
                    metric = path[2]
                    i_bit = int(path[3])

                    idx_min[idx] = idx_min[old_idx]
                    parity[idx] = parity[old_idx]
                    min_alphas[idx] = min_alphas[old_idx]
                    acc_parity[idx] = acc_parity[old_idx] + value

                    alpha_array[idx, :] = old_alpha_array[old_idx, :]

                    beta_array[idx, :] = old_beta_array[old_idx, :]
                    beta_array[idx, int(start_h) + i_bit] = value

                    metrics[idx] = metric

                num_paths = num_final_paths

            for idx, parity in enumerate(acc_parity[:num_paths]):
                beta_array[idx, int(start_h) + idx_min[idx]] = parity % 2

        elif task[1] == 4:

            start_h = address_list[task[0], 0]
            size = address_list[task[0], 5]

            for idx in range(num_paths):
                alphas = alpha_array[idx, start_h:start_h + size]
                metrics[idx] += 1 / 2 * np.sum(np.abs(alphas) - alphas)

        elif task[1] == 5:
            for i in range(num_paths):
                betas(beta_array[i, :], address_list, task[0])

        elif task[1] == 6:
            for i in range(num_paths):
                alpha_left(alpha_array[i, :], address_list, task[0])

        elif task[1] == 7:
            for i in range(num_paths):
                alpha_right(alpha_array[i, :], beta_array[i, :], address_list, task[0])

    # Outputting the whole array enables the use of CRC list decoding
    return beta_array


def rate_1(list_size, num_paths, alpha_array, beta_array, metrics, address, address_list):

    start_h = address_list[address, 0]
    size = address_list[address, 5]

    for i in range(size):

        num_final_paths = min(2 * num_paths, list_size)
        next_metrics = np.zeros((2 * num_paths, 3), dtype=np.float64)

        for idx in range(num_paths):
            alpha = alpha_array[idx, start_h + i]
            metric = metrics[idx]

            pm0 = metric + 1 / 2 * (abs(alpha) - alpha)
            pm1 = metric + 1 / 2 * (abs(alpha) + alpha)

            next_metrics[2 * idx, :] = [idx, 0.0, pm0]
            next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1]

        metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
        final_paths = next_metrics[metrics_order]

        old_alpha_array = np.copy(alpha_array)
        old_beta_array = np.copy(beta_array)
        for idx, path in enumerate(final_paths):
            old_idx = int(path[0])
            value = np.uint8(path[1])
            metric = path[2]

            alpha_array[idx, :] = old_alpha_array[old_idx, :]

            beta_array[idx, :] = old_beta_array[old_idx, :]
            beta_array[idx, int(start_h) + i] = value

            metrics[idx] = metric

        num_paths = num_final_paths

    return num_paths


def rep(list_size, num_paths, alpha_array, beta_array, metrics, address, address_list):
    start_h = address_list[address, 0]
    size = address_list[address, 5]

    num_final_paths = min(2 * num_paths, list_size)
    next_metrics = np.zeros((2 * num_paths, 3), dtype=np.float64)

    for idx in range(num_paths):
        alphas = alpha_array[idx, start_h:start_h + size]
        metric = metrics[idx]

        pm0 = metric + 1 / 2 * np.sum(np.abs(alphas) - alphas)
        pm1 = metric + 1 / 2 * np.sum(np.abs(alphas) + alphas)

        next_metrics[2 * idx, :] = [idx, 0.0, pm0]
        next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1]

    metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
    final_paths = next_metrics[metrics_order]

    old_alpha_array = np.copy(alpha_array)
    old_beta_array = np.copy(beta_array)
    for idx, path in enumerate(final_paths):
        old_idx = int(path[0])
        value = np.uint8(path[1])
        metric = path[2]

        alpha_array[idx, :] = old_alpha_array[old_idx, :]

        beta_array[idx, :] = old_beta_array[old_idx, :]
        beta_array[idx, start_h:start_h + size] = value * np.ones(size, dtype=np.uint8)

        metrics[idx] = metric

    num_paths = num_final_paths

    return num_paths


def spc(list_size, num_paths, alpha_array, beta_array, metrics, address, address_list):

    start_h = address_list[address, 0]
    size = address_list[address, 5]

    node_alphas = alpha_array[:, start_h: start_h + size]

    idx_min = np.argmin(np.abs(node_alphas), axis=-1).flatten()
    parity_array = np.ones(node_alphas.shape, dtype=np.uint8)
    parity_array[node_alphas >= 0] = 0
    parity = np.sum(parity_array, axis=-1) % 2
    min_alphas = np.min(np.abs(node_alphas), axis=-1)
    acc_parity = np.zeros(idx_min.shape, dtype=np.uint8)

    for idx in range(num_paths):
        metrics[idx] = metrics[idx] + min_alphas[idx] if parity[idx] else metrics[idx]

    for i in range(size - 1):

        num_final_paths = min(2 * num_paths, list_size)
        next_metrics = np.zeros((2 * num_paths, 4), dtype=np.float64)

        for idx in range(num_paths):
            if idx_min[idx] <= i:
                i_bit = i + 1

            else:
                i_bit = i

            alpha = alpha_array[idx, start_h + i_bit]
            metric = metrics[idx]

            pm0 = metric + abs(alpha) + (1 - 2 * parity[idx]) * min_alphas[idx] \
                if alpha < 0 else metric
            pm1 = metric + abs(alpha) + (1 - 2 * parity[idx]) * min_alphas[idx] \
                if alpha >= 0 else metric

            next_metrics[2 * idx, :] = [idx, 0.0, pm0, i_bit]
            next_metrics[2 * idx + 1, :] = [idx, 1.0, pm1, i_bit]

        metrics_order = np.argsort(next_metrics[:, 2])[:num_final_paths]
        final_paths = next_metrics[metrics_order]

        old_alpha_array = np.copy(alpha_array)
        old_beta_array = np.copy(beta_array)
        for idx, path in enumerate(final_paths):
            old_idx = int(path[0])
            value = np.uint8(path[1])
            metric = path[2]
            i_bit = int(path[3])

            idx_min[idx] = idx_min[old_idx]
            parity[idx] = parity[old_idx]
            min_alphas[idx] = min_alphas[old_idx]
            acc_parity[idx] = acc_parity[old_idx] + value

            alpha_array[idx, :] = old_alpha_array[old_idx, :]

            beta_array[idx, :] = old_beta_array[old_idx, :]
            beta_array[idx, int(start_h) + i_bit] = value

            metrics[idx] = metric

        num_paths = num_final_paths

    for idx, parity in enumerate(acc_parity[:num_paths]):
        beta_array[idx, int(start_h) + idx_min[idx]] = parity % 2

    return num_paths


def rate_0(num_paths, alpha_array, metrics, address, address_list):
    start_h = address_list[address, 0]
    size = address_list[address, 5]

    for idx in range(num_paths):
        alphas = alpha_array[idx, start_h:start_h + size]
        metrics[idx] += 1 / 2 * np.sum(np.abs(alphas) - alphas)
