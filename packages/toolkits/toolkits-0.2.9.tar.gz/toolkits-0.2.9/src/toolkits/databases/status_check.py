# -*- coding: utf-8 -*-
import json
import sys
import fire
from log4python.Log4python import log
from toolkits.databases.database_client_util import DatabaseClientUtil
from toolkits.databases.sqlalchemy_helper import SqlAlchemyHelper
import importlib
importlib.reload(sys)
logger = log("StatusCheck")


class StatusCheck:
    def __init__(self,
                 database_config,
                 task_info_table="etl_tasks",
                 field_task_name="task_name",
                 field_id_name="task_id",
                 field_status_name="task_status",
                 status_on_value="1",
                 status_off_value="0",
                 redis_keys_prefix="TasksScheduleCheck_",
                 redis_db_num=1
                 ):
        self.tasks_add_list = []
        self.tasks_edit_list = []
        self.tasks_delete_list = []
        self.__tasks_list_redis = {}
        self.__tasks_list_db = []

        self.__status_on_value = status_on_value
        self.__status_off_value = status_off_value

        self.__task_info_table = task_info_table
        self.__task_name = field_task_name
        self.__task_id_name = field_id_name
        self.__tasks_keys_prefix = redis_keys_prefix
        self.__fetch_tasks_sql = "select * from %s where `%s` = '%s' " % (self.__task_info_table,
                                                                          field_status_name,
                                                                          self.__status_on_value
                                                                          )

        self.__tasks_keys_pattern = "%s*" % self.__tasks_keys_prefix
        self.__database_init = DatabaseClientUtil(database_config)
        self.__mysql_conn = self.__database_init.get_mysql_client()
        self.__redis_cli = self.__database_init.get_redis_client(db_num=redis_db_num)
        self.__sql_helper = SqlAlchemyHelper()

        self.__check_status()

    def get_tasks_list(self):
        return self.__get_tasks_list_from_db()

    def __add_redis_task(self, task_info):
        key_id = "%s%s" % (self.__tasks_keys_prefix, task_info[self.__task_id_name])
        self.__redis_cli.set(key_id, json.dumps(task_info, ensure_ascii=False))

    def __del_redis_task(self, task_info):
        key_id = "%s%s" % (self.__tasks_keys_prefix, task_info[self.__task_id_name])
        self.__redis_cli.delete(key_id)

    def __get_tasks_list_from_redis(self):
        tasks_dict = {}
        keys = self.__redis_cli.keys(self.__tasks_keys_pattern)

        keys_final = keys
        if type(keys) is str:
            keys_final = [keys]

        if type(keys_final) is list:
            for key_item in keys_final:
                task_data = self.__redis_cli.get(key_item)
                task_info = json.loads(task_data)
                tasks_dict[task_info[self.__task_id_name]] = task_info
        else:
            logger.error("Error:Keys type was wrong [%s]" % str(keys))

        return tasks_dict

    def __get_tasks_list_from_db(self):
        ret = self.__mysql_conn.execute(self.__fetch_tasks_sql)
        tasks_list = self.__sql_helper.rows2list(ret)
        return tasks_list

    def get_task_info_by_task_id(self, task_id=None):
        if task_id:
            sql = "%s and %s='%s'" % (self.__fetch_tasks_sql, self.__task_id_name, task_id)
        else:
            sql = self.__fetch_tasks_sql
        logger.debug("SqlQuery:[%s]" % sql)
        ret = self.__mysql_conn.execute(sql)

        rows_data = []
        if ret:
            rows_data = self.__sql_helper.rows2list(ret)
        task_info = {}
        if len(rows_data) >= 1:
            task_info = rows_data[0]
        return task_info

    def __change_task_status(self, tasks_add_list, tasks_edit_list, tasks_delete_list):
        for item in tasks_add_list:
            logger.debug("AddTask:[%s]" % json.dumps(item, ensure_ascii=False))
            self.__add_redis_task(item)

        for item_edit in tasks_edit_list:
            self.__add_redis_task(item_edit)
            logger.debug("EditTask:[%s]" % json.dumps(item_edit, ensure_ascii=False))

        for task_item in tasks_delete_list:
            self.__del_redis_task(task_item)
            logger.debug("DeleteTask:[%s]" % json.dumps(task_item, ensure_ascii=False))

    def __check_tasks_status_change(self):
        tasks_add_list = []
        tasks_edit_list = []
        tasks_delete_list = []
        task_id_list = []

        for item_task in self.__tasks_list_db:
            task_id = item_task[self.__task_id_name]
            task_id_list.append(task_id)

            if task_id in self.__tasks_list_redis:
                tasks_edit_list.append(item_task)
            else:
                tasks_add_list.append(item_task)

        deleted_id_list = list(set(self.__tasks_list_redis.keys()) - set(task_id_list))
        for delete_id in deleted_id_list:
            tasks_delete_list.append(self.__tasks_list_redis[delete_id])

        return tasks_add_list, tasks_edit_list, tasks_delete_list

    def __check_status(self):
        self.__tasks_list_redis = self.__get_tasks_list_from_redis()
        self.__tasks_list_db = self.__get_tasks_list_from_db()

        self.tasks_add_list, self.tasks_edit_list, self.tasks_delete_list = self.__check_tasks_status_change()
        self.__change_task_status(self.tasks_add_list, self.tasks_edit_list, self.tasks_delete_list)

    def check_tasks_status_change(self, task_field_name):
        tasks_change_list = []
        for item_task in self.tasks_edit_list:
            task_id = item_task[self.__task_id_name]

            if task_field_name in item_task:
                task_field_val = item_task[task_field_name]

                if task_id in self.__tasks_list_redis and task_field_name in self.__tasks_list_redis[task_id]:
                    if task_field_val != self.__tasks_list_redis[task_id][task_field_name]:
                        tasks_change_list.append(item_task)
                else:
                    logger.error("Error:task_field_name-[%s]" % task_field_name)
            else:
                logger.error("Error: field_name:[%s], task_info [%s]" % (task_field_name, json.dumps(item_task)))
        return tasks_change_list


if __name__ == '__main__':
    fire.Fire(StatusCheck)
    exit()
