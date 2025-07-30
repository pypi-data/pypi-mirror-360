# -*- coding: utf-8 -*-
import imp
import os
import sys
import traceback
import uuid
from log4python.Log4python import log
import importlib
importlib.reload(sys)
logger = log("LoadModule")


class LoadModule(object):
    def __init__(self):
        pass

    @staticmethod
    def load_from_file(file_path):
        mod_name, file_ext = os.path.splitext(os.path.split(file_path)[-1])
        py_mod = None
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, file_path)
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, file_path)

        return py_mod

    @staticmethod
    def __write_tmp_py(file_path, content):
        fp = open(file_path, "w+")
        fp.write(content)
        fp.close()

    def load_from_string(self, func_string, module_name=None):
        modules = None
        try:
            str_random = str(uuid.uuid4()).replace("-", "")
            if module_name:
                file_path = "/tmp/dynamic_%s_%s.py" % (module_name, str_random)
            else:
                file_path = "/tmp/dynamic_%s.py" % str_random
            self.__write_tmp_py(file_path, func_string)
            modules = self.load_from_file(file_path)
        except Exception as ex:
            logger.debug("Error: %s" % ex)
            logger.debug(traceback.format_exc())
        return modules
