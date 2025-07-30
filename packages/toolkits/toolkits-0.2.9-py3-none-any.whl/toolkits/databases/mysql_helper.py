# -*- coding: utf-8 -*-
import importlib
import sys
import traceback
try:
    from urllib import parse
except Exception as ex:
    import urllib as parse

from log4python.Log4python import log
from sqlalchemy import Engine
from sqlalchemy import create_engine
from sqlalchemy.sql import text

importlib.reload(sys)
logger = log("MysqlHelper")
import pymysql

pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()


class MysqlHelper:
    def __init__(self, database_config=None):
        self.mysql_config = database_config
        self.__engine = None

    def get_mysql_client(self, config_user=None) -> Engine:
        '''
        mysql_db = 'mysql://root:***@10.89.189.48:8027/log_etl'
        '''
        engine = None
        try:
            if self.__engine is None:
                if config_user:
                    config_init = config_user
                else:
                    config_init = self.mysql_config
                mysql_db = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (config_init['user_name'],
                                                                    parse.quote_plus(config_init['password']),
                                                                    config_init['host'],
                                                                    config_init['port'],
                                                                    config_init['db_name']
                                                                    )
                engine = create_engine(mysql_db, echo=False, pool_recycle=3600, pool_pre_ping=True)
                self.__engine = engine
            else:
                engine = self.__engine
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error('deal_msg error: %s' % ex)
        return engine

    def execute(self, sql):
        try:
            # 创建数据库引擎
            engine = self.get_mysql_client()
            # 定义SQL查询语句
            execute_stmt = text(sql)
            with engine.connect() as connection:
                try:
                    result = connection.execute(execute_stmt)
                    connection.commit()
                except Exception as e:
                    logger.error(traceback.format_exc())
                    logger.error('deal_msg error: %s' % e)
                    connection.rollback()
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error('deal_msg error: %s' % ex)

    def query(self, sql) -> list[dict]:
        try:
            # 创建数据库引擎
            engine = self.get_mysql_client()

            # 定义SQL查询语句
            select_stmt = text(sql)

            # 使用连接执行查询
            result_list = []
            with engine.connect() as connection:
                result = connection.execute(select_stmt)

                # 将查询结果转换为字典列表
                # 使用fetchall()获取所有结果行，每行是一个元组
                # 使用namedtuple来获取列名和数据的对应关系
                columns = result.keys()
                result_list = [dict(zip(columns, row)) for row in result]
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error('deal_msg error: %s' % ex)
        return result_list

    @staticmethod
    def get_insert_schema(filed_names_list):
        schema_final = ""
        val_data = ""
        for item in filed_names_list:
            schema_final = schema_final + "%s, " % item.strip()
            val_data = val_data + ":%s, " % item.strip()
        schema_final = schema_final.strip(" ,")
        val_data = val_data.strip(" ,")
        return schema_final, val_data

    def bulk_insert(self, table_name: str, columns: list, data_list: list, batch_size=20000, columns_on_duplicate=[]):
        """
        执行分批批量插入操作的通用函数。

        :param columns_on_duplicate: 唯一键冲突时覆盖
        :param table_name: 要插入数据的表名
        :param columns: 表的列名列表
        :param data_list: 要插入的数据列表，其中每个元素是一个包含列值的元组
        :param batch_size: 每批插入的数据量
        """
        # 创建数据库引擎
        engine = self.get_mysql_client()

        on_duplicate_sql = ""
        if columns_on_duplicate:
            tmp_list = []
            for item in columns_on_duplicate:
                tmp_list.append("%s=VALUES(%s)" % (item, item))
            if tmp_list:
                on_duplicate_sql = "ON DUPLICATE KEY UPDATE %s" % ", ".join(tmp_list)

        # 准备批量插入的SQL语句模板
        schema_final, placeholders = self.get_insert_schema(columns)
        insert_stmt = text(f"INSERT INTO {table_name} ({schema_final}) VALUES ({placeholders}) {on_duplicate_sql}")
        logger.info("BulkInsert:[%s]" % str(insert_stmt))

        try:
            # 使用连接执行分批批量插入
            with engine.connect() as connection:
                try:
                    for i in range(0, len(data_list), batch_size):
                        # 获取当前批次的数据
                        batch_data = data_list[i:i + batch_size]
                        # 执行批量插入
                        connection.execute(insert_stmt, batch_data)
                        logger.info(f"Batch inserted {len(batch_data)} records.")

                    connection.commit()
                    logger.debug(f"Successfully inserted all data into {table_name},inserted {len(batch_data)} records.")
                except Exception as e:
                    logger.error(traceback.format_exc())
                    logger.error('deal_msg error: %s' % e)
                    connection.rollback()
        except Exception as ex:
            logger.error(traceback.format_exc())
            logger.error('deal_msg error: %s' % ex)
