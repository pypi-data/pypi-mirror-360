# -*- coding: utf-8 -*-
import argparse
import sys

import unicodecsv
from log4python.Log4python import log
import traceback
import importlib
importlib.reload(sys)
logger = log("ExcelHelper")


def write_cvs(column_names, rows, csv_file):
    try:
        with open(csv_file, 'wb') as f:
            # w = unicodecsv.writer(f, encoding='utf-8-sig')
            w = unicodecsv.writer(f, encoding='utf-8')
            w.writerow(column_names)
            w.writerows(rows)
        logger.debug("CsvFile:%s" % csv_file)
        ret = True
    except Exception as ex:
        ret = False
        logger.error(traceback.format_exc())
        logger.error('deal_msg error: %s' % ex)
    return ret


class ExcelHelper:
    def __init__(self, file_path, column_split=","):
        self.file_path = file_path
        self.column_split = column_split
        self.data = self.load_data()
        self.cloumns_names = []

    def load_data(self):
        fp = open(self.file_path)
        lines = fp.readlines()
        if len(lines) == 0:
            return []

        self.cloumns_names = lines[0].strip("\n\r").split(self.column_split)
        del lines[0]  # delete the title

        data = []
        for item in lines:
            try:
                columns_val = item.strip().split(self.column_split)
                tmp_row = {}
                for item_index in range(0, len(self.cloumns_names)):
                    if item_index >= len(columns_val):
                        val = ""
                    else:
                        val = columns_val[item_index]
                    tmp_row[self.cloumns_names[item_index]] = val
                data.append(tmp_row)
            except Exception as ex:
                logger.debug("Item:[%s]" % item)
                logger.error(traceback.format_exc())
                logger.error('deal_msg error: %s' % ex)
        return data

    def get_column_data(self, column_name):
        return self.fetch_column_data(self.data, column_name)

    @staticmethod
    def fetch_column_data(data, column_name):
        column_data = []
        for item in data:
            column_data.append(item[column_name])
        return column_data

    @staticmethod
    def fetch_dict_data(data, key_column_name, val_columns_name):
        data_dict = {}
        for item in data:
            tmp_val = {}
            for val_name in val_columns_name:
                tmp_val[val_name] = item[val_name]

            key_name = str(item[key_column_name])
            if key_name in dict(data_dict):
                data_dict[key_name].append(tmp_val)
            else:
                tmp_list = [tmp_val]
                data_dict[key_name] = tmp_list

        return data_dict

    def get_dict_data(self, key_column_name, val_columns_name):
        return self.fetch_dict_data(self.data, key_column_name, val_columns_name)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("excelFile", type=str, help="specify the excel file's path")
        args = parser.parse_args()
        csv = ExcelHelper(args.excelFile)
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())