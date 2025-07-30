# -*- coding: utf-8 -*-
import argparse
import os
import sys
import redis
from log4python.Log4python import log
import traceback
from sqlalchemy import create_engine
import importlib

path_cur = os.path.dirname(os.path.realpath(__file__))
path_parent = "%s/../" % path_cur
sys.path.append(path_parent)

from .hive_helper import HiveHelper
from .hive_client import HiveClient
importlib.reload(sys)
logger = log("DatabaseClientUtil")


class DatabaseClientUtil:
    def __init__(self, database_config):
        """
database_config:
hive_config = {
    "ip": "192.168.100.36",
    "port": "1627",
    "username": "test_01",
    "password": "",
    "database": "test_db"
}

mysql_info_online_alarm = {
    'user': 'db_user',
    'pwd': 'password!@#',
    'host': "192.168.100.36",
    'port': 3306,
    'db_name': "db_name"
}

redis_info = {
    'password': 'xxxpassword',
    'host': '192.168.100.36',
    'port': 9027,
    'db': 1
}

database_config = {
    "hive": hive_config,
    "mysql": mysql_info_online_alarm,
    "redis": redis_info,
}
    """
        self.base_path = self.__get_script_dir()
        self.sql_file = "%s/config/driver_query.sql" % self.base_path
        self.redis_client = None
        self.conn_mysql = None
        self.hive_client = None
        self.hive_config = None
        self.mysql_config = None
        self.redis_config = None
        self.init_database(database_config)

    def init_database(self, config):
        if config:
            self.hive_config = config['hive']
            self.mysql_config = config['mysql']
            self.redis_config = config['redis']

    def get_hive_client(self, database=None, config_user=None, hive_mode="jdbc",
                        work_path_base=None, yarn_queue="root.db.default", db_name='db_info'):
        if config_user:
            config_init = config_user
        else:
            config_init = self.hive_config

        if hive_mode != "jdbc":
            hive_client = HiveHelper(work_path_base=work_path_base, yarn_queue=yarn_queue, db_name=db_name)
        else:
            config_database_name = config_init['database']
            if database:
                config_database_name = database
            hive_client = HiveClient(config_init['ip'], config_init['username'], config_init['password'],
                                     config_database_name, config_init['port'])
        return hive_client

    def get_mysql_client(self, config_user=None):
        '''
        mysql_db = 'mysql://root:***@10.89.189.48:8027/log_etl'
        '''
        if config_user:
            config_init = config_user
        else:
            config_init = self.mysql_config
        mysql_db = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (config_init['user'],
                                                            config_init['pwd'],
                                                            config_init['host'],
                                                            config_init['port'],
                                                            config_init['db_name']
                                                            )
        engine = create_engine(mysql_db, echo=False, pool_recycle=3600, pool_pre_ping=True)
        return engine

    def get_redis_client(self, db_num=8, redis_config=None):
        if redis_config:
            config_init = redis_config
        else:
            config_init = self.redis_config
        redis_client = redis.StrictRedis(host=config_init['host'], port=config_init['port'],
                                         password=config_init['password'], db=db_num)
        return redis_client

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

    def worker(self):
        pass


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("action", type=str, help="specify the action [start]")
        args = parser.parse_args()

        if args.action == "start":
            app = DatabaseClientUtil()
            app.worker()
        else:
            print("Please Check the parameter!!")
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())
