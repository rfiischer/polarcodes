"""


Created on 10/03/2020 19:03

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import json
import configparser
import logging
import sys
import os


class ParameterHandler:
    def __init__(self, config_path=None):
        self.parser = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        self.log_file = None
        self.log_debug = False

        golden_file_path = os.path.join(os.path.dirname(__file__), "params.json")
        with open(golden_file_path, 'r', encoding='utf-8') as def_file:
            self.json_default = json.load(def_file)

        self.defaults = self._assemble_def_dict(self.json_default)

        self.parser.read_dict(self.defaults)

        if config_path is not None:
            with open(config_path, 'r', encoding='utf-8') as config_file:
                self.parser.read_file(config_file)

        self._load_params()
        self._check_params()

    def _load_params(self):
        for section in self.parser:
            for option in self.parser[section]:
                setattr(self, option, json.loads(self.parser[section][option]))

    def _check_params(self):
        for param_section in self.parser:
            if param_section not in self.defaults.keys() and param_section != 'DEFAULT':
                self.logger.warning("Parameter section not defined on the defaults: {}".format(param_section))

            for param_name, param_val in self.parser.items(param_section):
                if param_name not in self.defaults[param_section].keys():
                    self.logger.warning("Parameter '{}' not defined on default section {}".format(param_name,
                                                                                                  param_section))

                # Check if the parameter is valid
                param_options = self.json_default[param_section][param_name]['param_options']
                param_val = json.loads(param_val)
                if param_options is not None and param_val not in param_options:
                    self.logger.error("Parameter value {} not in default options {}".format(param_val,
                                                                                            param_options))

                    sys.exit(1)

    @staticmethod
    def _assemble_def_dict(json_def):
        default_dict = dict()
        for section in json_def.keys():
            default_dict[section] = dict()
            for parameter in json_def[section].keys():
                default_dict[section][parameter] = json.dumps(json_def[section][parameter]['default_value'])

        return default_dict
