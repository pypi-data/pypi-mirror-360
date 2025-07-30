# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys

import time
import uuid
from os.path import dirname

import arrow
from log4python.Log4python import log
import traceback

from toolkits.databases.hive_cmd import HiveCmd
from toolkits.system.excel_helper import ExcelHelper
from toolkits.system.shell_helper import exec_shell_with_pipe
from unipath import Path
import importlib

importlib.reload(sys)
logger = log("HiveHelper")


class HiveHelper:
    def __init__(self, work_path_base=None, yarn_queue="root.db.default", db_name="db_info"):
        if not work_path_base:
            self.base_path = self.get_run_dir()
        else:
            self.base_path = work_path_base
        self.log_path = "%s/logs" % self.base_path
        self.yarn_queue = yarn_queue
        self.db_name = db_name
        self.sql_file = "%s/config/driver_query.sql" % self.base_path

    @staticmethod
    def get_run_dir():
        script_path = sys.argv[0]
        if script_path[0] != "/":
            full_path = "%s/%s" % (os.getcwd(), script_path)
        else:
            full_path = script_path
        return os.path.dirname(full_path)

    def get_table_schema(self, tmp_table_name, target_table_name, table_info, time_range, data_file):
        '''
        :param table_info:
        {"fields_schema" :'', "partition_type": 'day|hour'}
        :param target_table_name:
        :param tmp_table_name:
        :param time_range:
        :param data_file:
        :return: dict_sql = {
            "header": content_header,
            "insert": sql_insert,
            "delete": sql_delete_tmp_table
        }:
        '''
        partition_time = time_range['time_begin']
        year = arrow.get(partition_time).format('YYYY')
        month = arrow.get(partition_time).format('MM')
        day = arrow.get(partition_time).format('DD')
        hour = arrow.get(partition_time).format('HH')

        header = '''set mapred.job.queue.name=%s;\nuse %s;\n''' % (self.yarn_queue, self.db_name)
        sql_create_tmp_table = '''CREATE TABLE %s(
%s
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\\t'
STORED AS TEXTFILE;\n'''
        sql_delete_tmp_table = 'drop table %s;\n'
        sql_load_data = '''LOAD DATA LOCAL INPATH '%s' INTO TABLE %s;\n'''

        if table_info['partition_type'] == "hour":
            sql_insert = '''INSERT INTO TABLE %s PARTITION (year='%s', month='%s', day='%s', hour='%s') select * from %s;\n''' % (target_table_name, year, month, day, hour, tmp_table_name)
        else:
            sql_insert = '''INSERT INTO TABLE %s PARTITION (year='%s', month='%s', day='%s') select * from %s;\n''' % (target_table_name, year, month, day, tmp_table_name)

        content_header = "%s\n%s\n%s\n" % (
            header,
            sql_create_tmp_table % (tmp_table_name, table_info['fields_schema']),
            sql_load_data % (data_file, tmp_table_name)
        )

        dict_sql = {
            "header": content_header,
            "insert": sql_insert,
            "tmp_table_delete": sql_delete_tmp_table % tmp_table_name
        }
        return dict_sql

    def get_file_path(self, time_range):
        '''
        :param time_range:
        :return:
        ret_dict = {
            "table_name": table_name,
            "file_sql": hive_sql,
            "file_err": hive_err,
            "file_out": hive_out,
            "file_data": data_file
        }
        '''
        begin = arrow.get(time_range['time_begin']).format('YYYYMMDD_HHmmss')
        table_create_time = arrow.now().format('YYYYMMDDHH')
        end = arrow.get(time_range['time_end']).format('YYYYMMDD_HHmmss')
        month_str = arrow.get(time_range['time_end']).format('YYYYMM')

        random_str = str(uuid.uuid4()).replace("-", "")
        name_post_fix = "%s_%s_%s" % (begin, end, random_str)
        month_dir = "%s/%s" % (self.log_path, month_str)
        if not Path(month_dir).exists():
            Path(month_dir).mkdir(True)
        data_file = "%s/data_%s.dat" % (month_dir, name_post_fix)
        table_name = "tmp_%s_%s" % (table_create_time, random_str)
        hive_sql = "%s/audit_%s.hql" % (month_dir, name_post_fix)
        hive_err = "%s/audit_%s.err" % (month_dir, name_post_fix)
        hive_out = "%s/audit_%s.dat" % (month_dir, name_post_fix)

        ret_dict = {
            "table_name": table_name,
            "file_sql": hive_sql,
            "file_err": hive_err,
            "file_out": hive_out,
            "file_data": data_file
        }
        return ret_dict

    def hive_execute(self, dict_path, content, values):
        self.write_file(dict_path['file_sql'], content, "w")
        self.write_file(dict_path['file_data'], values, "w")

        cmd = "hive -f %s 2> %s > %s " % (dict_path['file_sql'], dict_path['file_err'], dict_path['file_out'])
        logger.debug("CMD:[%s]" % cmd)
        ret = exec_shell_with_pipe(cmd)
        logger.debug("CMD_RET:[%s]" % ";".join(ret))

    def hive_insert(self, table_info, data, time_range, action_type=True, event_table_name="empl_access"):
        rows_warn = []
        for item in data:
            rows_warn.append("\t".join(map(str, item)))

        if rows_warn:
            values = "\n".join(list(set(rows_warn)))
            dict_path = self.get_file_path(time_range)
            # logger.debug("FilePath:[%s]" % json.dumps(dict_path, ensure_ascii=False))
            dict_sql = self.get_table_schema(dict_path['table_name'], event_table_name, table_info,
                                             time_range, dict_path['file_data'])

            if action_type:
                content = "%s\n%s\n%s" % (
                    dict_sql['header'],
                    dict_sql['insert'],
                    dict_sql['tmp_table_delete']
                )
            else:
                content = dict_sql['header']
                logger.debug("Mode:Debug!! Just write data to Tmp table[%s]\n Delete Tmp Table[drop table %s]" %
                             (dict_path['table_name'], dict_path['table_name']))
            self.hive_execute(dict_path, content, values)
        else:
            logger.debug("input [rows_warn] is empty!! ")

    @staticmethod
    def write_file(file_path, content, mode="w"):
        fp = open(file_path, mode)
        fp.write(content)
        fp.close()

    def hive_query(self, sql_query, file_name=""):
        random_str = str(uuid.uuid4()).replace("-", "")
        query_data_file = "%s/hive_query/hive_query_%s_%s.log" % (self.base_path, file_name, random_str)
        dir_path = dirname(query_data_file)
        if not Path(dir_path).exists():
            try:
                Path(dir_path).mkdir(parents=True)
            except Exception as ex:
                logger.error("Error: %s" % ex)
                logger.error(traceback.format_exc())

        hive_cmd = HiveCmd(query_data_file, sql_query, self.db_name, self.yarn_queue)
        logger.debug("Query:[%s]; ResultFile:[%s]" % (sql_query, query_data_file))
        hive_cmd.query()
        while True:
            if hive_cmd.query_is_finished():
                time.sleep(1)
                break
        return query_data_file

    def query(self, sql_query):
        file_name_time = arrow.now().format('YYYY-MM-DDTHHmmss')
        result_file = self.hive_query(sql_query, file_name_time)
        phone_list = []

        if Path(result_file).exists():
            excel = ExcelHelper(result_file, column_split="\t")
            phone_list = excel.data
        return phone_list

    def worker(self):
        pass


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("action", type=str, help="specify the action [start]")
        args = parser.parse_args()

        if args.action == "start":
            app = HiveHelper()
            app.worker()
        else:
            print("Please Check the parameter!!")
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())


