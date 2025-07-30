# -*- coding: utf-8 -*-
import argparse
import sys
from log4python.Log4python import log
import traceback
import importlib
importlib.reload(sys)
logger = log("MisUserActionEtl")


def set_dict_val(dst_dict, key_list, val):
    if len(key_list) > 0:
        key = key_list[0]
        del key_list[0]
        dst_dict[key] = set_dict_val(dst_dict[key], key_list, val)
        return dst_dict
    else:
        return val


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print((args.logFile))
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())