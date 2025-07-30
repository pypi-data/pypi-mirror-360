# -*- coding: utf-8 -*-
import multiprocessing
import sys
import time

from multiprocessing import Pool
import schedule
from log4python.Log4python import log
import traceback
from toolkits.system.time_helper import get_time_range_interval
import importlib

importlib.reload(sys)
logger = log("TasksController")


class TasksController:
    def __init__(self, process_num=10):
        self.process_num = process_num
        self.pool_process = None

    @staticmethod
    def run_schedule(exec_worker, exec_time="3:00"):
        """
        # schedule.every().minutes.do(self_phone_task)
        # schedule.every().minutes.do(quick_region_monitor_week_task)
        # schedule.every().monday.at("5:00").do(quick_region_monitor_week_task)
        # schedule.every().friday.at("17:32").do(self_phone_task)
        :return:
        """
        schedule.every().day.at(exec_time).do(exec_worker)
        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def func(msg):
        print(multiprocessing.current_process().name + '-' + msg)

    def run_redis_tasks(self, exec_worker):
        self.pool_process = Pool(self.process_num)
        results = []
        for range_item in range(0, self.process_num):
            result = self.pool_process.apply_async(exec_worker, (range_item,), callback=None)
            results.append(result)

        # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
        self.pool_process.close()
        self.pool_process.join()

    def run_time_range(self, exec_worker, time_begin, time_end, time_interval="1d"):
        self.pool_process = Pool(self.process_num)
        time_range_list = get_time_range_interval(time_begin, time_end, time_interval)

        results = []
        for range_item in time_range_list:
            result = self.pool_process.apply_async(exec_worker, (range_item,), callback=None)
            results.append(result)

        # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
        self.pool_process.close()
        self.pool_process.join()


if __name__ == '__main__':
    try:
        app = TasksController()
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
