# -*- coding: utf-8 -*-
import re
from os.path import basename
from log4python.Log4python import log
from unipath import Path
logger = log("DirFileSearch")


def read_content(file_path):
    fp = open(file_path)
    content = fp.readlines()
    fp.close()
    return content


class DirFileSearch:
    """:cvar
    file_search = DirFileSearch(".*_1021.log")
    file_compress_list = file_search.loop_filter_files(target_path)
    """
    def __init__(self, search_pattern):
        self.__search_pattern = search_pattern

    def __filter_by_name(self, file_path):
        handle_path = Path(file_path)

        if handle_path.isdir():
            return file_path

        if handle_path.isfile():
            file_name = basename(file_path)
            if re.findall(self.__search_pattern, file_name):
                return file_path

    def loop_filter_files(self, file_path):
        file_list = []
        handle_path = Path(file_path)

        if handle_path.isdir():
            search_path = file_path
            loop_next_file_list = Path(search_path).listdir(filter=self.__filter_by_name)
            for item in loop_next_file_list:
                tmp_handle_path = Path(item)
                if tmp_handle_path.isdir():
                    tmp_file_list = self.loop_filter_files(item)
                    file_list.extend(tmp_file_list)
                else:
                    file_list.append(item)

        if handle_path.isfile():
            file_list.append(file_path)
        return file_list
