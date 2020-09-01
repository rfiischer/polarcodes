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
        alpha_left_custom,
        alpha_right_custom,
        betas_custom,
        encode,
        ssc_decode,
        fast_ssc_decode,
        sscl_spc_decode
    )


except ImportError:
    raise ImportError("The compiled module is not available. Please run the compile script.")
