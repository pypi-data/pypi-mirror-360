# -*- coding: utf-8 -*-
from toolkits.libs_core.load_module import LoadModule


class ConfigHelpers:
    def __init__(self):
        pass

    @staticmethod
    def load_config(config_file):
        app = LoadModule()
        config_info = app.load_from_file(config_file)
        return config_info

    @staticmethod
    def get_config_by_name(config_data, config_name):
        config_info = None
        if config_data:
            config_info = config_data.__dict__[config_name]

        return config_info

