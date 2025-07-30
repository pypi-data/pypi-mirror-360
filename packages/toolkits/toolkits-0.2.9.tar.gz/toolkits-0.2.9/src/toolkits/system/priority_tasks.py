# -*- coding: utf-8 -*-
import argparse
import pprint
import sys
import time
from copy import deepcopy

import arrow
import redis
import json

from arrow import Arrow
from log4python.Log4python import log
import traceback
import importlib

importlib.reload(sys)
logger = log("PriorityTasks")


class PriorityTasks:
    '''
    ServerDemo:
        def init_worker(task):
            pass  # process task
        if __name__ == '__main__':
            task = PriorityTasks("Test")
            task.worker(init_worker)
    ClientDemo:
        # priority in ["high", "mid", "low"]
        PriorityTasks("Test").send_task(priority, task_params_json)
    '''
    def __init__(self, redis_conn_info, queue_key=None, work_status_queue_name="txt_redis_working_flag"):
        self.redis_conn_info = redis_conn_info
        self.queue_key = queue_key
        self.work_status_queue_name = work_status_queue_name
        self.key_file_tasks = self.queue_key+"_%s"
        logger.info("PriorityTasksKey:[%s]" % self.queue_key)
        self.keys_file_tasks = [self.queue_key+"_high", self.queue_key+"_mid", self.queue_key+"_low"]
        self.redisCli = redis.StrictRedis(host=redis_conn_info['host'],
                                          port=redis_conn_info['port'], password=redis_conn_info['password'],
                                          db=redis_conn_info['db'], decode_responses=True)

    def get_tasks_by_priority(self):
        task = None
        for key_task in self.keys_file_tasks:
            # logger.debug("FetchKey:[%s]" % key_task)
            line = self.redisCli.lpop(key_task)
            if line:
                logger.debug("Key:[%s]; line:[%s]" % (key_task, line))
                task = line
                break
        return task

    def get_tasks_stat(self):
        for priority in ["high", "mid", "low"]:
            key_process_priority = self.key_file_tasks % priority
            print(("TaskQueue-%s-Number: [%s]" % (priority.capitalize(), str(self.redisCli.llen(key_process_priority)))))

    @staticmethod
    def get_worker_process():
        print("No implement, Wait ...")

    def stop_tasks(self):
        self.redisCli.set(self.work_status_queue_name, "off")

    def start_tasks(self):
        self.redisCli.set(self.work_status_queue_name, "on")

    def __send_task(self, priority, task_params):
        if not self.queue_key:
            tip = "The QueueKey is None, Nothing to Do."
            logger.error(tip)
            print(tip)
            return None

        queue_key = self.get_priority_queue(priority)
        conn_info = deepcopy(self.redis_conn_info)
        conn_info['password'] = "******"
        logger.info("RedisInfo:[%s]; QueueKey:[%s]" % (json.dumps(conn_info, ensure_ascii=False), queue_key))
        self.redisCli.rpush(queue_key, task_params)

    def send_high_task(self, task_params):
        self.__send_task("high", task_params)

    def send_mid_task(self, task_params):
        self.__send_task("mid", task_params)

    def send_low_task(self, task_params):
        self.__send_task("low", task_params)

    def get_priority_queue(self, priority):
        key_process_priority = self.key_file_tasks % "high"
        if priority in ["high", "mid", "low"]:
            key_process_priority = self.key_file_tasks % priority
        else:
            logger.error("Log priority Level Not Found [%s]" % priority)
        return key_process_priority

    def worker(self, task_func, func_records_check=None, records_count=1, time_out=30):
        if not self.queue_key:
            tip = "The QueueKey is None, Nothing to Do."
            logger.error(tip)
            print(tip)
            return None

        work_status = False
        work_flag = self.redisCli.get(self.work_status_queue_name)
        conn_info = deepcopy(self.redis_conn_info)
        conn_info['password'] = "******"
        logger.info("TasksRedisInfo:[%s]" % json.dumps(conn_info, ensure_ascii=False))
        if str(work_flag).lower() == "on":
            work_status = True
            logger.info("CurrentTaskSwitchKey:[%s]; InitWork: Status is ON!!! " % self.work_status_queue_name)
        else:
            work_status = False
            logger.info("CurrentTaskSwitchKey:[%s]; InitWork: Status is OFF!!!  Nothing to do...." %
                        self.work_status_queue_name)

        record_list = []
        flag_fetch_data = False
        time_idle_begin = 0
        flag_start_to_wait_restart = "%s_pid_%s_status" % (self.work_status_queue_name, str(1))
        while True:
            work_flag = self.redisCli.get(self.work_status_queue_name)
            if str(work_flag).lower() != "on":
                if work_status:
                    logger.info("Work Status Change to OFF!!! ")
                    time_stop = arrow.now().format('YYYY-MM-DD HH:mm:ss')
                    self.redisCli.set(flag_start_to_wait_restart, "wait_to_restart:[%s]" % time_stop)
                work_status = False
                time.sleep(1)
                continue
            else:
                if work_status is False:
                    logger.info("Work Status Change to ON!!! ")
                    self.redisCli.set(flag_start_to_wait_restart, "ok_now_to_start_process_task", 0.5)
                work_status = True

            task = self.get_tasks_by_priority()
            if task is None:
                if flag_fetch_data is True:
                    flag_fetch_data = False
                    time_idle_begin = Arrow.now().timestamp
                else:
                    if len(record_list) > 0:
                        time_cur = Arrow.now().timestamp
                        time_used = time_cur - time_idle_begin
                        if time_used >= time_out:
                            task_func(record_list)
                            record_list = []
                time.sleep(1)
                continue
            else:
                flag_fetch_data = True

            if records_count == 1:
                task_func(task)
            else:
                if func_records_check is not None:
                    ret_data = func_records_check(task)
                    if isinstance(ret_data, list):
                        record_list.extend(ret_data)
                    else:
                        record_list.append(ret_data)
                else:
                    record_list.append(task)

                if len(record_list) >= records_count:
                    record_list = self.process_data(task_func, record_list, records_count)

    @staticmethod
    def process_data(func_process, arr, count):
        unprocess_list = []
        len_arr = len(arr)
        len_range = len_arr / count

        for item in range(len_range + 1):
            index_begin = item * count
            index_end = index_begin + count
            if index_end > len_arr:
                index_end = len_arr
                unprocess_list = arr[index_begin: index_end]
                break
            else:
                func_process(arr[index_begin: index_end])

        return unprocess_list


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print((args.logFile))
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
