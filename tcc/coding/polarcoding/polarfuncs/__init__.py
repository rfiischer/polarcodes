"""


Created on 06/03/2020 17:35

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import logging

# TODO: change this design pattern
try:
    from tcc.coding.polarcoding.polarfuncs.polarfuncs_compiled import fl, fr, phi, address_list_factory, \
                                                                      ssc_node_classifier, fast_ssc_node_classifier, \
                                                                      alpha_left, alpha_right, betas, encode, \
                                                                      ssc_decode, fast_ssc_decode, sscl_spc_decode

    from tcc.coding.polarcoding.polarfuncs.polarfuncs import ssc_scheduler, fast_ssc_scheduler, sscl_spc_scheduler

except ImportError:
    from tcc.coding.polarcoding.polarfuncs.polarfuncs import fl, fr, address_list_factory, ssc_node_classifier, \
                                                             fast_ssc_node_classifier, ssc_scheduler, \
                                                             fast_ssc_scheduler, sscl_spc_scheduler, alpha_left, \
                                                             alpha_right, betas, encode, ssc_decode, fast_ssc_decode, \
                                                             sscl_spc_decode

    logging.warning("Using pure Python implementation. To use Pythran, run the compile script.")
