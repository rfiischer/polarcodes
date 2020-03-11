"""


Created on 10/03/2020 20:14

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import logging
import sys

from coding.polarcoding.construction.bhattacharyya import bhattacharyya

logger = logging.getLogger(__name__)


def construction(method, n, design_snr):
    if method == "bhattacharyya":
        rel_idx = bhattacharyya(n)

    else:
        logger.error("Construction method not implemented {}".format(method))
        sys.exit(1)

    return rel_idx
