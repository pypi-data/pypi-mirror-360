# -*- coding: utf-8 -*-
import argparse
import os
import pprint
import sys
from log4python.Log4python import log
import traceback
import importlib
importlib.reload(sys)
logger = log("SqlAlchemyHelper")


class SqlAlchemyHelper:
    def __init__(self):
        self.base_path = self.__get_script_dir()
        self.sql_file = "%s/config/driver_query.sql" % self.base_path

    @staticmethod
    def __get_run_dir():
        script_path = sys.argv[0]
        if script_path[0] != "/":
            full_path = "%s/%s" % (os.getcwd(), script_path)
        else:
            full_path = script_path
        return os.path.dirname(full_path)

    @staticmethod
    def __get_script_dir():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def __row2dict(row):
        d = {}
        for column in list(row.keys()):
            # a.encode('utf-8').strip()
            content = ""
            try:
                content = str(row[column]).encode('utf-8')
            except Exception as ex:
                logger.debug("ColumnName:[%s]; ColumnContent:[%s]" % (column, pprint.pformat(row[column])))
                logger.error("Error: %s" % ex)
                logger.error(traceback.format_exc())
            finally:
                d[column] = content
        return d

    def rows2list(self, result):
        rows = []
        for item in result:
            rows.append(self.__row2dict(item))
        return rows

    def worker(self):
        pass


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("action", type=str, help="specify the action [start]")
        args = parser.parse_args()

        if args.action == "start":
            app = SqlAlchemyHelper()
            app.worker()
        else:
            print("Please Check the parameter!!")
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())

