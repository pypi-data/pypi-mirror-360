# -*- coding: utf-8 -*-
import argparse
import json
import pprint
import sys
from os.path import dirname, basename
import xmltodict
from log4python.Log4python import log
import traceback
from unipath import Path
from xml.dom.minidom import parseString

from toolkits.system.dict2xml import dicttoxml
from toolkits.system.shell_helper import exec_shell_with_pipe
import importlib

importlib.reload(sys)
logger = log("PdiHelper")


class PdiHelper:
    def __init__(self, pdi_exec):
        self.pdi_exec_path = pdi_exec  # "/services/pdi/data-integration/pan.sh"

    # 定义xml转json的函数
    def xmltojson(self, xmlstr):
        # parse是的xml解析器
        xmlparse = xmltodict.parse(xmlstr)
        # json库dumps()是将dict转化成json格式，loads()是将json转化成dict格式。
        # dumps()方法的ident=1，格式化json
        jsonstr = json.dumps(xmlparse, indent=1)
        return jsonstr

    # json转xml函数
    def jsontoxml(self, jsonstr):
        # xmltodict库的unparse()json转xml
        xmlstr = xmltodict.unparse(jsonstr)
        return xmlstr

    def load_xml(self, xml_config_file):
        fp = open(xml_config_file)
        lines = fp.readlines()
        fp.close()

        config = ""
        for item in lines:
            config += item.strip()
        return config

    def write_xml(self, new_config_file, config_xml):
        fp_out = open(new_config_file, "w+")
        fp_out.write(config_xml)
        fp_out.close()

    def covert_xml(self, xml_config_file, config_set):
        str_xml = self.load_xml(xml_config_file)

        config_json = self.xmltojson(str_xml)
        obj_json = json.loads(config_json)
        print(obj_json)
        my_item_func = lambda x: x
        str_xml = dicttoxml(obj_json, attr_type=False, root=False,
                            item_func=my_item_func, expand_list_item_name_flag=False)

        dom = parseString(str_xml)
        str_xml = dom.toprettyxml()

        self.write_xml("%s_new" % xml_config_file, str_xml)

    def covert_config(self, xml_config_file, new_config_file, config_set):
        '''<?xml version="1.0" encoding="utf-8"?>
    <student>
    <course>
    <name>math</name>
    <score>90</score>
    </course><info>
    <name>name</name>
    <sex>male</sex>
    </info>
    <stid>10213</stid>
    <title>1</title>
    <title>2</title>
    <list>
    <hop>
    <a>a</a>
    </hop>
    <hop>
    <a>b</a>
    </hop>
    </list>
    </student>
        # {u'student': {u'info': {u'name': u'name', u'sex': u'male'}, u'course': {u'score': u'90', u'name': u'math'},
        #  u'stid': u'10213', u'list': {u'hop': [{u'a': u'a'}, {u'a': u'b'}]}, u'title': [u'1', u'2']}}
        '''
        ret = False
        str_xml = self.load_xml(xml_config_file)

        config_json = self.xmltojson(str_xml)
        obj_config = json.loads(config_json)
        if self.config_merge(obj_config, config_set):
            my_item_func = lambda x: x
            str_xml = dicttoxml(obj_config, attr_type=False, root=False,
                                item_func=my_item_func, expand_list_item_name_flag=False)
            dom = parseString(str_xml)
            str_xml = dom.toprettyxml()
            self.write_xml(new_config_file, str_xml.replace("&quot;", "\""))
            ret = True
        return ret

    def set_dict(self, dst_dict, key_list, val):
        if len(key_list) > 0:
            key = key_list[0]
            del key_list[0]
            # dst_dict[key] = set_dict_val(dst_dict[key], key_list, val)

            # logger.debug("Key:[%s]" % key)
            pos_key = key.find("[")
            if pos_key >= 0:
                key_search = key[:pos_key]
                if type(dst_dict) is list:
                    key_found = False
                    for item in dst_dict:
                        if item[key_search] == key[pos_key+1: -1]:
                            item = self.set_dict(item, key_list, val)
                            key_found = True
                    if not key_found:
                        logger.debug("Error:key_search[%s] Not Found!!" % key)
                else:
                    logger.debug("key_search:[%s]" % key_search)
                    raise
            else:
                if key in dict(dst_dict):
                    dst_dict[key] = self.set_dict(dst_dict[key], key_list, val)
                else:
                    logger.debug("Error:key[%s] not found." % key)
            return dst_dict
        else:
            return val

    def config_merge(self, config_template, config_list):
        ret = False
        obj_data = None
        try:
            for config_item in config_list:
                key_list = config_item['key'].split(".")
                val_set = config_item['val']
                obj_data = config_template
                config_template = self.set_dict(config_template, key_list, val_set)
            ret = True
        except Exception as ex:
            pprint.pprint(obj_data)
            logger.debug("Ojbect_Data:%s" % pprint.pformat(obj_data))
            logger.debug("Error: %s" % ex)
            logger.debug(traceback.format_exc())
        finally:
            return ret

    def fetch_data_from_es(self, pdi_config_file, url, query, data_output_path):
        log_path = "%s/log/" % dirname(data_output_path)
        tmp_config_path = "%s/config_tmp/" % dirname(data_output_path)
        log_file_name = "%s/output_%s.log" % (log_path, basename(data_output_path))
        if not Path(log_path).exists():
            Path(log_path).mkdir(True)

        if not Path(tmp_config_path).exists():
            Path(tmp_config_path).mkdir(True)

        cmd_ret = False
        try:
            # modify the config
            config_set = [
                {
                    'key': "transformation.step.name[url_query].fields.field.name[url].nullif",
                    'val': url
                },
                {
                    'key': "transformation.step.name[url_query].fields.field.name[req].nullif",
                    'val': query.replace("\n", "")
                },
                {
                    'key': "transformation.step.name[out_put].file.name",
                    'val': data_output_path
                }]

            final_kettle_config = "%s/%s_new" % (tmp_config_path, basename(pdi_config_file))
            if self.covert_config(pdi_config_file, final_kettle_config, config_set):
                # run process
                cmd = "%s -file %s -logfile %s" % (self.pdi_exec_path, final_kettle_config, log_file_name)
                logger.debug("CMD:[%s]" % cmd)
                exec_shell_with_pipe(cmd)
                cmd_ret = True
        except Exception as ex:
            logger.debug("Error: %s" % ex)
            logger.debug(traceback.format_exc())
        finally:
            return cmd_ret

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print((args.logFile))
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
