# -*- coding: utf-8 -*-
import importlib
import sys
from log4python.Log4python import log

importlib.reload(sys)
logger = log("ListHelper")


class ListHelper:
    def __init__(self):
        pass

    @staticmethod
    def list_split_by_length(data_list, length_interval):
        list_final = []
        data_len = len(data_list)
        times = data_len / length_interval
        for index in range(0, times+1):
            begin = index * length_interval
            end = begin + length_interval
            if end > data_len:
                end = data_len
            if len(data_list[begin:end]) > 0:
                list_final.append(data_list[begin:end])
        return list_final
