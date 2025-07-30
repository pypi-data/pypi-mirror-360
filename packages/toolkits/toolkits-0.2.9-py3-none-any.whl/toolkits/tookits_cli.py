# -*- coding: utf-8 -*-
import traceback

import fire
from log4python.Log4python import log
from toolkits.system.basic_utils import get_script_directory

from toolkits.config_parser.env_prepare import EnvPrepare
from tookits_app import tookitsApp
from libs_core.process_admin import ProcessAdmin
from db_query_demo import DbQueryDemo

logger = log("tookits")


class tookits:
    def __init__(self, config_path=None):
        self.__base_path = get_script_directory()
        if config_path is None:
            self.__env = EnvPrepare(tookitsApp.app_name)
            self.__env.check_env()
            self.__config_path = self.__env.get_config_path("config.py")
            self.__env.check_config_ready(self.__config_path, "请先初始化配置文件、在数据库创建相应的数据表")
        else:
            tookitsApp.config_file_path = config_path
        self.db_query = DbQueryDemo
        self.__db_list = self.__env.get_config("db_list")
        # self.auto_stat_stock = AutoStatStock(self.__db_list['dev_ops'])
        self.__configChatGroups = ConfigGroupsHelper(self.__env.get_config('db_list'), 'dict')
        self.__process_admin = ProcessAdmin()

    def show_db_list(self):
        """
        列表查看数据库信息
        :return:
        """
        self.__configChatGroups.list_config_groups("RDS-连接")

    def init_config(self, path_target):
        src_path = "%s/config/" % self.__base_path
        self.__env.init_default_config("directory", src_path, path_target)

    def init_database(self):
        ddl_sql_list = self.__get_db_ddl_list("policy_status_monitor")
        for ddl_sql in ddl_sql_list:
            database_config = self.__env.get_config(self.__config_path, "database_config")
            self.__env.init_db(database_config['mysql'], ddl_sql)

    def __schedule_tasks(self):
        self.__process_admin.loop_check_exit()
        # self.auto_stat_stock.schedule_start()

    def __recall_tasks(self):
        self.__process_admin.loop_check_exit()
        logger.info("DBinfo: %s", json.dumps(self.__db_list['dev_ops'], ensure_ascii=True))
        # app = StrategyRecall(mysql_conn_info=self.__db_list['dev_ops'])
        # app.process_buy_sale_data("stock_buy_sale_data", "group_test_01")

    def start_all_tasks(self):
        tasks_list = [
            self.__schedule_tasks,
            self.__recall_tasks
        ]
        self.__process_admin.processes_start(tasks_list)

    @staticmethod
    def __get_db_ddl_list(table_name):
        ddl_sql = ["""CREATE TABLE `%s` (
  `task_id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `task_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `task_status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '0：关闭，1：启用，8：暂停',
  `desc` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `task_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `task_params` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `task_crontab` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_params` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_id` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `check_condition` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `db_config` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `extra_data` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""" % table_name,
                   """INSERT INTO """ + table_name + """
(task_id, task_name, task_status, `desc`, task_type, task_params, task_crontab, action_type, action_params, event_id, check_condition, db_config, extra_data)
VALUES('00065df8eb99442db2808ee19592000x', 'task_50031_dlp_dchat', '0', '策略产出监控-DLP-Dchat安装状态监控', 'sql', 'select mc_rule as event_id, FROM_UNIXTIME(occur_ts/1000,''%%Y-%%m-%%d'') as event_time, count(*) as event_value, "" as event_detail 
from online_alarm oa 
where occur_ts >= unix_timestamp(concat(CURDATE(), " 00:00:00")) * 1000 
and occur_ts < unix_timestamp(concat(ADDDATE(CURDATE(), 1), " 00:00:00")) * 1000 
and mc_rule = ''20071''
group by FROM_UNIXTIME(occur_ts/1000,''%%Y-%%m-%%d''),mc_rule
 limit 1', '15 20 * * *', 'email', '{
  "event_id": "50031",
  "event_action": {
    "ding_talk": {
      "group_info": {
        "name": "long_term_query_talk",
        "desc": "长期查询监控群",
        "web_hook": "https://oapi.dingtalk.com/robot/send?access_token=69b8e2bae810c9f392b197072699a8241e0a25552291789128cbe5c805cfd5da"
      },
      "group_target": "long_term_query_talk"
    }
  }
}', '50031', 'event_value < 5000', '{
    "user": "db_admin",
    "pwd": "gYrmHFNOpkIb/UNM5zCuiDScMdCPwsneOoV38RbEYOs=",
    "host": "10.83.16.15",
    "port": 8012,
    "db_name": "sec_admin"
}', NULL);
;"""
                   ]
        return ddl_sql


def main():
    try:
        fire.Fire(tookits)
    except Exception as ex:
        logger.error("Error: %s" % ex)
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
