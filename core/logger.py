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
    root_logger.setLevel(logging.NOTSET)

    if default_log_file:
        handler = logging.FileHandler(filename=default_log_file, encoding='utf8', mode='w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not log_debug:
        handler.addFilter(Filter(logging.DEBUG))
    root_logger.handlers = []
    root_logger.addHandler(handler)
