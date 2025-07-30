# -*- coding: utf-8 -*-
import os
import pprint
import sys
import fire
from log4python.Log4python import log
import traceback
import importlib

path_cur = os.path.dirname(os.path.realpath(__file__))
path_parent = "%s/../../" % path_cur
sys.path.append(path_parent)

from system.priority_tasks import PriorityTasks
from databases.database_client_util import DatabaseClientUtil
from .tasks_controller import TasksController
importlib.reload(sys)
logger = log("TasksMultiprocessing")


queue_name = None
queue_switch = None
func_task = None
redis_info = None


def exec_redis_tasks(task_item):
    if not queue_name or not queue_switch or not redis_info or not func_task:
        logger.error("Err: parameters is Wrong")
        return None

    try:
        task = PriorityTasks(redis_info, queue_name, work_status_queue_name=queue_switch)
        task.worker(func_task)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())


class TasksMultiprocessing:
    def __init__(self, tasks_queue_name, tasks_switch, process_num=10):
        global queue_name, queue_switch
        queue_name = tasks_queue_name
        queue_switch = tasks_switch
        self.__base_path = self.__get_script_dir()
        self.__database_init = None
        self.__redis_cli = None
        self.__db_info = None
        self.__process_num = process_num

    def init_db(self, database_info, process_num=10):
        """
        :param database_info:
        :param process_num:
        :return:
        """
        self.__db_info = database_info
        self.__database_init = DatabaseClientUtil(database_info)
        self.__redis_cli = self.__database_init.get_redis_client(db_num=database_info['redis']['db'])
        self.__process_num = process_num
        self.start_tasks()

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

    def get_tasks_queue_info(self):
        global queue_name, queue_switch
        queue_info = {
            "tasks_redis": {
                "host": self.__db_info['redis']['host'],
                "port": self.__db_info['redis']['port'],
                "db_num": self.__db_info['redis']['db']
            },
            "tasks_queue": ["%s_high" % queue_name,
                            "%s_mid" % queue_name,
                            "%s_low" % queue_name],
            "tasks_switch": queue_switch
        }
        pprint.pprint(queue_info)

    def start_tasks(self):
        global queue_switch
        self.__redis_cli.set(queue_switch, "on")
        logger.debug("Set switch ON [%s]" % queue_switch)

    def __wait_process_stop(self):
        pass

    def __kill_process(self):
        pass

    def set_worker(self, func_process):
        global func_task, redis_info
        func_task = func_process
        redis_info = self.__db_info['redis']

    def stop_tasks(self):
        global queue_switch
        self.__redis_cli.set(queue_switch, "off")
        logger.debug("Set switch OFF [%s]" % queue_switch)
        self.__wait_process_stop()
        self.__kill_process()

    def daemon_start(self, action):
        """
        action = start
        :param action:
        :return:
        """
        if action == "start":
            task_controller = TasksController(self.__process_num)
            task_controller.run_redis_tasks(exec_redis_tasks)
        else:
            print("Please Check the parameter!!")


if __name__ == '__main__':
    try:
        # import pydevd
        # pydevd.settrace('127.0.0.1', port=6868, stdoutToServer=True, stderrToServer=True)
        fire.Fire(TasksMultiprocessing)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
