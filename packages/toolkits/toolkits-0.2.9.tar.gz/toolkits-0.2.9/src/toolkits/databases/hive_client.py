#!/usr/bin/env python
# -*- coding: utf-8 -*-
# hive util with hive server2

import xlwt as xlwt
from log4python.Log4python import log
import sys
import importlib

logger = log("HiveClient")

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    importlib.reload(sys)
    sys.setdefaultencoding(default_encoding)


class HiveClient:
    def __init__(self, db_host, user, password, database, port=10000, authMechanism="PLAIN"):
        """
        create connection to hive server2
        """
        import pyhs2
        import xlwt
        config = {"mapreduce.job.queuename": "xx.queue.default"}
        self.conn = pyhs2.connect(host=db_host,
                                  port=port,
                                  authMechanism=authMechanism,
                                  user=user,
                                  password=password,
                                  database=database,
                                  configuration=config
                                  )

    def query(self, sql):

        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetch()

    def execute(self, sql):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
        except Exception as ex:
            print(ex)

    def close(self):
        """
        close connection
        """
        self.conn.close()


def writeXlwt(filename,result):
    book=xlwt.Workbook() #打开一个工作薄
    sheet1=book.add_sheet('sheel1')#添加一个sheet页
    for i in range(len(result)+1):
        if i ==0:
            sheet1.row(i).write(0, '日期')
            sheet1.row(i).write(1, '小时')
            sheet1.row(i).write(2, '楼层')
            sheet1.row(i).write(3, '店铺号')
            sheet1.row(i).write(4, '店铺名称')
            sheet1.row(i).write(5, '人数')
        else:
            for a in range(len(result[i-1])):
                sheet1.row(i).write(a,result[i-1][a])
    book.save(filename)
