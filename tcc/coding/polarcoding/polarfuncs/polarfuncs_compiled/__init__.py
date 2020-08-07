"""

Created on 07/08/2020 09:41

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

try:

    import numpy as np

    from .polarfuncs_compiled import (
        fl,
        fr,
        address_list_factory,
        ssc_node_classifier,
        fast_ssc_node_classifier,
        alpha_left,
        alpha_right,
        betas,
        encode,
        ssc_decode,
        fast_ssc_decode,
        sscl_spc_decode,
        rate_1,
        rate_0,
        rep,
        spc
    )


    def sscl_spc_decode_hybrid(n, list_size, alphas, tasks, address_list):
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
                num_paths = rate_1(list_size, num_paths, alpha_array, beta_array, metrics, task[0], address_list)

            elif task[1] == 2:

                num_paths = rep(list_size, num_paths, alpha_array, beta_array, metrics, task[0], address_list)

            elif task[1] == 3:

                num_paths = spc(list_size, num_paths, alpha_array, beta_array, metrics, task[0], address_list)

            elif task[1] == 4:

                rate_0(num_paths, alpha_array, metrics, task[0], address_list)

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


except ImportError:
    raise ImportError("The compiled module is not available. Please run the compile script.")
