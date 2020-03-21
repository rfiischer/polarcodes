# -*- coding: utf-8 -*-
"""
Logging setup and initialization

Created on Jan 29 15:11 2019

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import sys
import logging
import logging.config


class Filter(object):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno != self.level


def setup_logging(default_log_file=None, log_debug=False):

    root_logger = logging.getLogger()

    if not log_debug:
        root_logger.setLevel(logging.INFO)

    else:
        root_logger.setLevel(logging.DEBUG)

    if default_log_file:
        handler = logging.FileHandler(filename=default_log_file, encoding='utf8', mode='w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler_sys = logging.StreamHandler(sys.stdout)
    handler_sys.setLevel(logging.WARNING)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler.setFormatter(formatter)
    handler_sys.setFormatter(formatter)

    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.addHandler(handler_sys)
