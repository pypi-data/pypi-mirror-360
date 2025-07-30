# -*- coding: utf-8 -*-
from log4python.Log4python import log
from toolkits.system.basic_utils import get_script_directory, add_relative_search_path

logger = log("tookitsApp")


class tookitsApp:
    app_name = 'tookits'
    config_file_path = None

    def __init__(self):
        self.__base_path = get_script_directory()


if __name__ == '__main__':
    pass
