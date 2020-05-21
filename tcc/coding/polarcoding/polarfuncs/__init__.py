"""


Created on 06/03/2020 17:35

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

# import logging
#
# try:
#     from tcc.coding.polarcoding.polarfuncs.polarfuncs_compiled import fl, fr, address_list_factory, node_classifier, \
#                                                                       alpha_left, alpha_right, betas, encode, sc_decode
#
#     from tcc.coding.polarcoding.polarfuncs.polarfuncs import sc_scheduler
#
# except ImportError:
from tcc.coding.polarcoding.polarfuncs.polarfuncs import fl, fr, address_list_factory, node_classifier, \
                                                         sc_scheduler, alpha_left, alpha_right, betas, encode, \
                                                         sc_decode
# logging.warning("Using pure Python implementation. To use Pythran, run the compile script.")
