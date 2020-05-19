"""


Created on 06/03/2020 17:35

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

# import logging
#
# try:
#     from tcc.coding.polarcoding.polarfuncs.polarfuncs_compiled import alpha_left, alpha_right, betas, fr, fl, \
#                                                                       resolve_node, encode, node_classifier, \
#                                                                       child_list_maker, list_decode, beta_maker
#
# except ImportError:
#     from tcc.coding.polarcoding.polarfuncs.polarfuncs import alpha_left, alpha_right, betas, fr, fl, resolve_node, \
#                                                              encode, node_classifier, child_list_maker, list_decode, \
#                                                              beta_maker
#     logging.warning("Using pure Python implementation. To use Pythran, run the compile script.")

from .polarfuncs import sc_decode, encode, address_list_factory, node_classifier, sc_scheduler
