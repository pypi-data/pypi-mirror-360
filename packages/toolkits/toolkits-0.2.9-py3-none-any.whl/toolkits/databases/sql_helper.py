# -*- coding: utf-8 -*-
import argparse
import pprint
import re
import sys

import sqlparse
from log4python.Log4python import log
from sqlparse.sql import Where, Comparison, Parenthesis, Identifier, Token, Function
import traceback

from sqlparse.tokens import DML
import importlib

importlib.reload(sys)
logger = log("SqlHelper")


class SqlWhere:
    def __init__(self, sql_dml):
        self.sql_dml = sql_dml
        self.where_tokens = None
        self.condition_data = {
            "condition": {
                "key": "",
                "op": "",
                "val": []
            },
            "or_list": [],
            "and_list": []
        }
        self.where_conditions = None

    @staticmethod
    def split_or(where_tokens):
        or_list = []
        or_item = []
        found_flag = False

        for item in where_tokens:
            if item.is_keyword and item.value.upper() == 'WHERE':
                continue

            if item.is_keyword and item.value.upper() == 'OR':
                found_flag = True
                # or_item_tmp = copy.deepcopy(or_item)
                or_list.append(or_item)
                or_item = []
            else:
                or_item.append(item)

        if found_flag:
            or_list.append(or_item)

        return or_list

    @staticmethod
    def split_and(where_tokens):
        and_list = []
        and_item = []
        found_flag = False
        between_flag = False

        for item in where_tokens:
            if item.is_keyword and item.value.upper() == 'WHERE':
                continue

            if item.is_keyword and item.value.upper() == 'BETWEEN':
                between_flag = True

            if item.is_keyword and item.value.upper() == 'AND' and not between_flag:
                found_flag = True
                and_list.append(and_item)
                and_item = []
            else:
                if item.is_keyword and item.value.upper() == 'AND' and between_flag:
                    between_flag = False
                and_item.append(item)

        if found_flag:
            and_list.append(and_item)

        return and_list

    @staticmethod
    def get_condition(tokens):
        key_found_flag = False
        val = []
        key = ""
        op = []

        for token in tokens:
            if token.is_whitespace:
                continue

            if token.is_keyword and token.value.upper() == 'WHERE':
                continue

            if isinstance(token, Comparison):
                key = token.left.value
                op = ["eq"]
                val = token.right.value
                break

            if token.is_keyword:
                if key_found_flag:
                    op.append(token.value)
            else:
                if not key_found_flag:
                    key = token.value
                    key_found_flag = True
                else:
                    if isinstance(token, Parenthesis):
                        tmp_val = token.value.strip("() ").split(",")
                        val_strip = [item.strip("\"") for item in tmp_val]
                        val.extend(val_strip)
                    else:
                        val.append(token.value)
                        # val += token.value
        condition_tmp = {
            "key": key,
            "op": "-".join(op).upper(),
            "val": val
        }

        return condition_tmp

    def check_sub_conditions(self, where_tokens):
        sub_tokens = []
        for token in where_tokens:
            if isinstance(token, Parenthesis) and (self.split_or(token.tokens) or self.split_and(token.tokens)):
                # sub_tokens.append(token.tokens)
                sub_tokens = token.tokens
        return sub_tokens

    def parse_where_tokens(self, where_tokens):
        where_group_tmp = {
            "condition": None,
            "sub_condition": None,
            "or_list": [],
            "and_list": [],
        }
        or_list = self.split_or(where_tokens)
        if or_list:
            for or_item in or_list:
                where_group_tmp['or_list'].append(self.parse_where_tokens(or_item))
        else:
            and_list = self.split_and(where_tokens)
            if and_list:
                for and_item in and_list:
                    where_group_tmp['and_list'].append(self.parse_where_tokens(and_item))
            else:
                sub_tokens = self.check_sub_conditions(where_tokens)
                if sub_tokens:
                    where_group_tmp['sub_condition'] = self.parse_where_tokens(sub_tokens)
                else:
                    where_group_tmp['condition'] = self.get_condition(where_tokens)

        return where_group_tmp

    def print_where(self):
        pprint.pprint(self.where_conditions)

    def get_column_condition(self, where_condition):
        column_condition = []
        if where_condition['condition']:
            column_condition.append(where_condition['condition'])

        if where_condition['sub_condition']:
            column_condition.extend(self.get_column_condition(where_condition['sub_condition']))

        if where_condition['or_list']:
            for item in where_condition['or_list']:
                column_condition.extend(self.get_column_condition(item))

        if where_condition['and_list']:
            for item in where_condition['and_list']:
                column_condition.extend(self.get_column_condition(item))

        return column_condition

    def get_where_conditions(self):
        where_tokens_list = self.get_sql_where()

        column_condition_list = []
        for where in where_tokens_list:
            tmp_where_tokens = self.parse_where_tokens(where)
            tmp_list = self.get_column_condition(tmp_where_tokens)
            column_condition_list.extend(tmp_list)

        return column_condition_list

    def has_dml(self, obj_check, level):
        sql_dml = None
        try:
            if level == 0:
                return sql_dml
            else:
                level -= 1
                found_dml = False
                if not isinstance(obj_check, Token):
                    for token_item in obj_check.tokens:
                        if token_item.ttype is DML:
                            found_dml = True
                            break
                if found_dml:
                    sql_dml = obj_check
                else:
                    if not isinstance(obj_check, Token):
                        for token_item in obj_check.tokens:
                            ret = self.has_dml(token_item, level)
                            if ret:
                                sql_dml = token_item
                                break
        except Exception as ex:
            sql_dml = None
            logger.debug("Error: %s" % ex)
            logger.debug(traceback.format_exc())
        finally:
            return sql_dml

    def get_where_tokens(self, tokens):
        tokens_where = []
        sql_dml = False
        for token_item in tokens:
            if token_item.ttype is DML:
                sql_dml = True
                break

        if not sql_dml:
            return tokens_where

        for token_item in tokens:
            if isinstance(token_item, Where):
                tokens_where.append(token_item)
            if isinstance(token_item, Identifier):
                token_check = self.has_dml(token_item, 2)
                if token_check:
                    sql_where = self.get_where_tokens(token_check.tokens)
                    if sql_where:
                        tokens_where.extend(sql_where)

        return tokens_where

    def search_columns(self, where_list, columns_list):
        for where_item in where_list:
            for token in where_item.tokens:
                for column in columns_list:
                    if token.is_group:
                        pass
                    elif token.is_keyword:
                        pass
                    elif token.is_whitespace:
                        pass
                    if isinstance(token, Identifier):
                        pass
                    if isinstance(token, Comparison):
                        pass
                    if isinstance(token, Function):
                        pass

    def get_sql_where(self):
        '''
        xx = "select * from test01 where id=1 or (id=2 and id=4) and id=5 or id = 6 and id not in (4,5,6)"
        xx = "select * from test01 where id=1 or (id=2 and id=4)"
        '''
        sql_query = str(re.sub("--.*?;", " ", self.sql_dml)).replace(";", " ")
        sql_list = sqlparse.parse(sql_query)
        where_tokens_list = []

        for sql in sql_list:
            where_list = re.findall("where", sql.value)
            where_num = len(where_list)
            if where_num == 0:
                print("NO found where.")
                break
            where_tokens = self.get_where_tokens(sql.tokens)
            where_tokens_list.extend(where_tokens)

        return where_tokens_list


if __name__ == '__main__':
    try:
        xx = "select * from test01 where id=1 or (id=2 and id=4)"
        sql_where = SqlWhere(xx)
        conditions_list = sql_where.get_where_conditions()
        pprint.pprint(conditions_list)
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())