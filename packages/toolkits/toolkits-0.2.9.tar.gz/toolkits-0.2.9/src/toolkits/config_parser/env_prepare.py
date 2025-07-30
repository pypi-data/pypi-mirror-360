# -*- coding: utf-8 -*-
import os
import platform
import sys
import traceback

import fire
import jmespath
from log4python.Log4python import log
from toolkits.system.basic_utils import get_script_directory
from toolkits.system.shell_helper import exec_shell
from unipath import Path

from .config_helper import ConfigHelpers
from toolkits.databases.mysql_helper import MysqlHelper

logger = log("EnvPrepare")


class EnvPrepare:
    config_file_path = None

    def __init__(self, app_name, config_full_path=None, config_global_name="config_global"):
        self.__base_path = get_script_directory()
        self.__config_global_name = config_global_name
        self.__user_home_path = os.path.expanduser("~/.config")
        self.__app_name = app_name
        self.__config_full_path = None
        self.__config_path = "%s/%s/" % (self.__get_workdir(), self.__app_name)
        if config_full_path:
            if Path(config_full_path).exists():
                self.__config_full_path = config_full_path
            else:
                logger.error("Config was not exist:[%s]" % config_full_path)

        self.__tip_message = "Initialized: finished, please change the default's config to " \
                             "adapt your environment! "
        self.__default_path_tip = "Default config path: %s" % self.__config_path
        self.__dict_config = {}

    def __get_workdir(self):
        app_data = self.__user_home_path
        if platform.system().lower() == 'windows':  # print("windows")
            app_data = "%s\\.config" % os.getenv("APPDATA")
        elif platform.system().lower() == 'linux':  # print("linux")
            app_data = self.__user_home_path
        return app_data

    def check_env(self):
        # check env-config
        if not Path(self.__config_path).exists():
            Path(self.__config_path).mkdir(parents=True)
            src_path = "%s/../config/" % self.__base_path
            self.init_default_config("directory", src_path, self.__config_path)
            print("%s\n%s" % (self.__tip_message, self.__default_path_tip))
            logger.error("%s\n%s" % (self.__tip_message, self.__default_path_tip))

    def check_config_ready(self, config_path, error_message):
        if not Path(config_path).exists():
            msg = error_message + "\n" + self.__default_path_tip
            print(msg)
            logger.error(msg)
            # raise Exception(msg)
            exit(-1)

    def get_config_path(self, config_file_name):
        return "%s/%s" % (self.__config_path, config_file_name)

    def get_config_from_file(self, config_path: str, config_key: str, force_reload: bool = False) -> dict:
        if config_path not in self.__dict_config or force_reload is True:
            config_data = ConfigHelpers.load_config(config_path)
            self.__dict_config[config_path] = config_data
        else:
            config_data = self.__dict_config[config_path]

        return ConfigHelpers.get_config_by_name(config_data, config_key)

    def __get_default_config_file(self):
        running_app = os.path.split(os.path.realpath(sys.argv[0]))[1]
        if running_app[-3:] == ".py" or running_app[-4:] == ".pyc":
            path_working = os.path.split(os.path.realpath(sys.argv[0]))[0]
        else:
            path_working = os.getcwd()

        config_path_working = "%s/config.py" % path_working
        if not Path(config_path_working).exists():
            config_path_working = "%s/%s/config.py" % (self.__user_home_path, self.__app_name)
        return config_path_working

    def get_default_config(self, config_key: str, force_reload: bool = False) -> dict:
        if EnvPrepare.config_file_path:
            config_path_working = EnvPrepare.config_file_path
        else:
            config_path_working = self.__get_default_config_file()
        logger.debug("config_path_working: %s", config_path_working)
        config_data = None
        if Path(config_path_working).exists():
            config_data = self.get_config_from_file(config_path_working, config_key, force_reload)
        return config_data

    def get_config(self, config_key: str, force_reload: bool = False):
        if self.__config_full_path:
            config_data = self.get_config_from_file(self.__config_full_path, self.__config_global_name, force_reload)
        else:
            config_data = self.get_default_config(self.__config_global_name, force_reload)
        return jmespath.search(config_key, config_data)

    @staticmethod
    def init_default_config(init_type, src_path, dest_path):
        init_status = False
        if init_type == 'file':
            if platform.system().lower() == 'windows':
                cmd_copy = "XCOPY /S /-Y %s %s " % (str(src_path).replace("/", "\\"), str(dest_path).replace("/", "\\"))
            elif platform.system().lower() == 'linux':
                cmd_copy = "cp -arf %s %s " % (src_path, dest_path)
        elif init_type == 'directory':
            if platform.system().lower() == 'windows':
                cmd_copy = "xcopy /S /-Y %s %s " % (str(src_path).replace("/", "\\"), str(dest_path).replace("/", "\\"))
            elif platform.system().lower() == 'linux':
                cmd_copy = "cp -arf %s/* %s/ " % (src_path, dest_path)
        else:
            return init_status

        logger.info("CopyCMD: %s" % cmd_copy)
        ret = exec_shell(cmd_copy)
        if str(ret['exit_code']) == "0":
            init_status = True
        return init_status

    @staticmethod
    def init_db(database_config, sql_execute):
        try:
            mysql_conn = MysqlHelper(database_config)
            mysql_conn.execute(sql_execute)
        except Exception as ex:
            logger.error("Error: %s" % ex)
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    try:
        fire.Fire(EnvPrepare)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
