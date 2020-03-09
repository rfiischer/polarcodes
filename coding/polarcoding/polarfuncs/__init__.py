"""


Created on 06/03/2020 17:35

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import logging

try:
    from coding.polarcoding.polarfuncs.polarfuncs_compiled import alpha_left, alpha_right, betas, fr, fl, compute_node

except ImportError:
    from coding.polarcoding.polarfuncs.polarfuncs import alpha_left, alpha_right, betas, fr, fl, compute_node
    logging.warning("Using pure Python implementation. To use Pythran, run the compile script.")
