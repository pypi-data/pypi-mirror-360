# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys
import time
from os.path import dirname
from log4python.Log4python import log
import traceback
from unipath import Path

from toolkits.system.shell_helper import exec_shell_with_pipe, file_is_used
import importlib

path_cur = os.path.dirname(os.path.realpath(__file__))
path_parent = "%s/../" % path_cur
sys.path.append(path_parent)
# from system.shellHelper import exec_shell_with_pipe, file_is_used

from threading import Timer
import _thread
importlib.reload(sys)
logger = log("HiveCmd")


class HiveCmd:
    def __init__(self, file_name, sql, db_name, yarn_queue, work_path=None):
        self.file_name = str(file_name).replace(":", "")
        if not work_path:
            self.work_path = dirname(self.file_name)
        else:
            self.work_path = work_path
        self.sql = sql
        self.hive_hql_file = "%s.hql" % self.file_name
        self.hive_err_file = "%s.err" % self.file_name
        self.hive_info = "use %s;\nset mapred.job.queue.name=%s; \n" % (db_name, yarn_queue)
        logger.debug("HiveCmd:filename[%s]; sql[%s]" % (self.file_name, self.sql))

        path_to_check = dirname(self.file_name)
        if not Path(path_to_check).exists():
            Path(path_to_check).mkdir(True)

    def query(self):
        hql_content = self.hive_info + "%s"
        hql_cmd = "hive -f %s"
        Path(self.hive_hql_file).write_file(hql_content % self.sql)
        cmd = hql_cmd % self.hive_hql_file
        return exec_shell(cmd, stdout=self.file_name, stderr=self.hive_err_file, work_path=self.work_path)

    def query_is_finished(self):
        return file_is_used(self.file_name)


def run_with_timeout(timeout, default, f, *args, **kwargs):
    if not timeout:
        return f(*args, **kwargs)
    timeout_timer = Timer(timeout, _thread.interrupt_main)
    try:
        timeout_timer.start()
        result = f(*args, **kwargs)
        return result
    except KeyboardInterrupt:
        return default
    finally:
        timeout_timer.cancel()


def exec_shell(cmd, timeout=0, work_path="", stdout=None, stderr=None):
    """exeShellWithPipe("grep 'processor' /proc/cpuinfo | sort -u | wc -l")
    :param stderr:
    :param stdout:
    :param work_path:
    :param timeout:
    :param cmd:  exec command
    """
    if cmd == "" or cmd is None:
        return "No Cmd Input"

    fp_out = subprocess.PIPE
    fp_err = subprocess.PIPE
    if stdout:
        fp_out = open(stdout, "w+")
    if stderr:
        fp_err = open(stderr, "w+")

    if work_path == "":
        scan_process = subprocess.Popen(cmd, shell=True, stdout=fp_out, stderr=fp_err)
    else:
        scan_process = subprocess.Popen(cmd, shell=True, stdout=fp_out, stderr=fp_err, cwd=work_path)

    return_code = None
    while True:
        return_code = scan_process.poll()
        if return_code is None:
            time.sleep(1)
        else:
            break
    return return_code


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("fileName", type=str, help="specify the sql output file's path")
        parser.add_argument("sql", type=str, help="specify the sql to query")
        args = parser.parse_args()

        hive_cmd = HiveCmd(args.fileName, args.sql, "db_name", "root.db.default")
        ret_code = hive_cmd.query()
        print(("RetCode:[%s]" % str(ret_code)))
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
