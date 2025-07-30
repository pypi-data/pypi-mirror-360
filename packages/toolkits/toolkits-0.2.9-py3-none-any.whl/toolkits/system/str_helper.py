# -*- coding: utf-8 -*-
import hashlib
import os
import pprint
import re
import sys
import uuid
from log4python.Log4python import log
import importlib
importlib.reload(sys)
logger = log("strHelper")
import esm


class StrHelper:
    def __init__(self):
        self.__base_path = self.__get_script_dir()
        self.__sql_file = "%s/config/driver_query.sql" % self.__base_path

    @staticmethod
    def __element_count(arr, target):
        return arr.count(target)

    @staticmethod
    def is_string(obj):
        try:
            obj.lower() + obj.title() + obj + ""
        except Exception as ex:
            return False
        else:
            return True

    @staticmethod
    def __reg_find_data(reg_pattern, search_data):
        data_search = []
        m = re.finditer(reg_pattern, search_data)
        try:
            while True:
                data_match = m.next().group()
                if data_match:
                    data_search.append(data_match)
        except Exception as ex:
            pass
        return data_search

    @staticmethod
    def multi_search(search_string, search_list):
        """
        多模匹配搜索字符串

search_string:
    search_str = u"哎呀，今天在楼下看到了宝马，我老家倒是有养马的，以前的邻居有个奔驰，不对是保时捷，大爷的，都是马"
search_words:
    search_words = [u"宝马", u"马", u"奔驰", u"保时捷"]
result::

    [((33, 39), u'\\u5b9d\\u9a6c'),
    (36, 39), u'\\u9a6c'),
    (63, 66), u'\\u9a6c'),
    (93, 99), u'\\u5954\\u9a70'),
    (111, 120), u'\\u4fdd\\u65f6\\u6377'),
    (141, 144), u'\\u9a6c')]

end-code

        :param search_string:
        :param search_list:
        :return:
        """
        index = esm.Index()
        for item in search_list:
            index.enter(item)
        index.fix()
        ret = index.query(search_string)
        return ret

    def __element_repeat_stat(self, data_array):
        if not data_array:
            return []

        uniq_data = list(set(data_array))
        data_list = []
        for item in uniq_data:
            count_num = self.__element_count(data_array, item)
            val_stat = {
                'emlement': item,
                'count': count_num
            }
            data_list.append(val_stat)
        return data_list

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

    @staticmethod
    def md5_str(str_input):
        from md5 import md5
        return md5(str_input).hexdigest().upper()

    @staticmethod
    def md5_file(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def random_str():
        return str(uuid.uuid4()).replace("-", "")

    def match_phone_info(self, search_data, match_pattern):
        """
match phone info

search_data:
    test_str = ' 175****3754 158****5552 158****5552 13412337575 15812311265 user_id-1334321093 '
match_pattern:
        match_pattern = [
            {
                "name": "phone",
                "reg": r'((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|190|192|19[6-9]|(147))\d{8}'
            },
            {
                "name": "phone_mask",
                "reg": r'[0-9]{3}\*{4}[0-9]{4}'
            },
            {
                "name": "user_id",
                "reg": r'user_id-([0-9]+)'
            }]

return-val:
    {
        "phone": [
            {
                "count": 1,
                "emlement": "13412337575"
            },
            {
                "count": 1,
                "emlement": "15812311265"
            }
        ],
        "user_id": [
            {
                "count": 1,
                "emlement": "user_id-1334321093"
            }
        ],
        "phone_mask": [
            {
                "count": 2,
                "emlement": "158****5552"
            },
            {
                "count": 1,
                "emlement": "175****3754"
            }
        ]
    }

end-code

        :param search_data:
        :param match_pattern:
        :return:
        """
        match_info = {}
        for item_pattern in match_pattern:
            phone_reg = item_pattern['reg']
            pattern_name = item_pattern['name']
            data_match = self.__reg_find_data(phone_reg, search_data)
            data_check = self.__element_repeat_stat(data_match)
            match_info[pattern_name] = data_check

        return match_info
