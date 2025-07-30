# -*- coding: utf-8 -*-
import traceback

import fire
from log4python.Log4python import log
from toolkits.system.basic_utils import get_script_directory

from toolkits.config_parser.env_prepare import EnvPrepare
from toolkits.databases.mysql_helper import MysqlHelper

logger = log("DbQueryDemo")


class DbQueryDemo:
    def __init__(self, config_path=None):
        self.__base_path = get_script_directory()
        self.__config_path = config_path
        if config_path is None:
            if tookitsApp.config_file_path is None:
                self.__env = EnvPrepare(tookitsApp.app_name)
                self.__env.check_env()
                self.__config_path = self.__env.get_config_path("config.py")
                self.__env.check_config_ready(self.__config_path, "请先初始化配置文件、在数据库创建相应的数据表")
            else:
                self.__config_path = tookitsApp.config_file_path

        self.__env = EnvPrepare(tookitsApp.app_name, self.__config_path)
        self.__mysql_config = self.__env.get_config('mysql_info_online_alarm')
        self.sql_helper = MysqlHelper(self.__mysql_config)

    def query_sql(self, query_where) -> list:
        list_api = self.sql_helper.query("SELECT x.* FROM sec_admin.api_sec_output_send x WHERE bot_process in (%s)" % query_where)
        # logger.debug("Result:[%s]" % json.dumps(list_api))
        logger.debug("Len: %s" % str(len(list_api)))
        return list_api

    @staticmethod
    def __read_all_data(file_path):
        fp = open(file_path)
        data_list = fp.readlines()
        fp.close()
        ns_list = []
        for item in data_list:
            ns_list.append(str(item).strip())
        return ns_list

    def worker(self, file_path, batch_size=10):
        data_list = self.__read_all_data(file_path)
        final_list = []
        for i in range(0, len(data_list), batch_size):
            # 获取当前批次的数据
            batch_data = data_list[i:i + batch_size]
            sql_where = "'%s'" % "', '".join(batch_data)

            kylin_list = self.query_sql(sql_where)
            final_list.extend(kylin_list)

        fp = open("%s.csv" % file_path, "w+")
        fp.write("source,host,name_space")
        for item in list(set(final_list)):
            fp.write("%s,%s,%s\r\n" % (item['source'], item['host'], item['name_space']))
        fp.close()


if __name__ == '__main__':
    try:
        fire.Fire(DbQueryDemo)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())

