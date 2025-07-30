# -*- coding: utf-8 -*-
import json
import os
import pprint
import sys
import arrow
import fire
from log4python.Log4python import log
import traceback
import importlib

path_cur = os.path.dirname(os.path.realpath(__file__))
path_parent = "%s/../../" % path_cur
sys.path.append(path_parent)

from system.priority_tasks import PriorityTasks
from system.tasks_deamon.tasks_controller import TasksController
from system.tasks_deamon.tasks_multiprocessing import TasksMultiprocessing
from system.time_helper import get_time_range_interval

importlib.reload(sys)
logger = log("TasksProcess")
worker_func = None


def load_json(task_data):
    task_obj = None
    try:
        if type(task_data) is str:
            task_obj = json.loads(task_data)
        else:
            logger.error("Error: wrong parameters[%s]" % pprint.pformat(task_data))
    except Exception as ex:
        logger.error("Task[%s] Process Error" % pprint.pformat(task_data))
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
    return task_obj


def install_worker(exec_func):
    def tasks_worker(task_data):
        global worker_func
        worker_func = exec_func
        task_obj = load_json(task_data)
        if task_obj:
            time_begin = task_obj['time_begin']
            time_end = task_obj['time_end']
            logger.debug("Before ExecTimeRange:[%s]" % json.dumps(task_obj, ensure_ascii=False))
            # do some work
            worker_func(time_begin, time_end)
            logger.debug("After ExecTimeRange:[%s]" % json.dumps(task_obj, ensure_ascii=False))
    return tasks_worker


class TasksRework(TasksMultiprocessing):
    def __init__(self, tasks_queue_name, tasks_switch):
        TasksMultiprocessing.__init__(self, tasks_queue_name, tasks_switch)
        self.__task_queue_name = tasks_queue_name
        self.__tasks_switch = tasks_switch
        self.__date_white_list = None
        self.__database_config = None
        self.__task_worker = None
        self.__init_tasks_flag = None

    def init_tasks(self, database_config, tasks_worker_func, task_worker_number=10):
        """do not resort the order of below method call !!!
        :param task_worker_number:
        :param database_config:
        :param tasks_worker_func:
        """
        self.__database_config = database_config
        self.__task_worker = tasks_worker_func
        self.init_db(database_config, task_worker_number)
        self.set_worker(tasks_worker_func)
        self.__init_tasks_flag = True

    def set_date_white_list(self, date_list):
        self.__date_white_list = date_list

    def __get_process_white_list(self):
        date_list = []
        if not self.__date_white_list:
            date_list = self.__date_white_list
        return date_list

    def tasks_send(self, time_begin, time_end):
        if not self.__init_tasks_flag:
            msg = "Please first call init_tasks function!!!"
            logger.debug(msg)
            raise Exception(msg)

        task = PriorityTasks(self.__database_config['redis'],
                             self.__task_queue_name,
                             work_status_queue_name=self.__tasks_switch)
        time_range_list = get_time_range_interval(time_begin, time_end, "1d")
        date_white_process_list = self.__get_process_white_list()

        for time_range in time_range_list:
            ts_begin = arrow.get(time_range['time_begin']).format('YYYY-MM-DD HH:mm:ss')
            ts_end = arrow.get(time_range['time_end']).format('YYYY-MM-DD HH:mm:ss')

            if date_white_process_list and arrow.get(time_range['time_begin']).format('YYYY-MM-DD') in date_white_process_list:
                continue

            task_info = {
                "time_begin": ts_begin,
                "time_end": ts_end
            }

            print((json.dumps(task_info, ensure_ascii=False)))
            task.send_high_task(json.dumps(task_info, ensure_ascii=False))


class TasksProcess:
    def __init__(self, db_config, task_queue_name, task_switch_name):
        self.__database_config = db_config
        self.__task_controller = TasksController()
        self.__task_rework = TasksRework(task_queue_name, task_switch_name)

    def worker_schedule(self, worker_exec, time_daily="06:33"):
        self.__task_controller.run_schedule(worker_exec, time_daily)

    def worker_redo(self, exec_func, time_begin, time_end):
        self.__task_rework.init_tasks(self.__database_config, exec_func)
        self.__task_rework.tasks_send(time_begin, time_end)

    def worker_daemon(self, exec_func, task_worker_number=5):
        self.__task_rework.init_tasks(self.__database_config, exec_func, task_worker_number=task_worker_number)
        self.__task_rework.daemon_start("start")


if __name__ == '__main__':
    try:
        fire.Fire(TasksProcess)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
