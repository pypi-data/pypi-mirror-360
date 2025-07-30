# -*- coding: utf-8 -*-
import argparse
import json
import sys
from log4python.Log4python import log
from elasticsearch import Elasticsearch
import traceback
import importlib
importlib.reload(sys)
logger = log("AgssQuery")


class EsClient:
    def __init__(self, es_url):
        self.es_url = es_url  #
        self.scroll = "1m"
        self.es = self.es_connect()

    def es_connect(self):
        es = Elasticsearch(
                [
                    self.es_url
                ],
                verify_certs=False,
                timeout=60*60
        )
        return es

    def es_search(self, index_name, body_query):
        res = self.es.search(index=index_name, body=body_query)
        return res

    def es_search_scroll(self, index_name, body_query):
        result = []
        page = self.es.search(index=index_name, body=body_query, scroll=self.scroll)
        sid = page['_scroll_id']
        scroll_size = page['hits']['total']
        result.append(page)

        # Start scrolling
        while scroll_size > 0:
            logger.debug("Scrolling...")
            page = self.es.scroll(scroll_id=sid, scroll=self.scroll)
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            logger.debug("scroll size: " + str(scroll_size))
            result.append(page)
        return result


class AgssQuery:
    def __init__(self, config, es_url):
        self.es_client = EsClient(es_url)
        self.config_audit = config

    @staticmethod
    def construct_query(config_sys):
        sys_name = config_sys['desc']
        rule = config_sys['rule']

        index = rule['es_index']
        json_search = rule['search']['json']
        action = rule['action']

        return sys_name, index, json_search, action

    def main_query(self):
        (sys_name, es_index_name, json_search, action) = self.construct_query(self.config_audit)
        # query
        logger.debug("SYS:[%s]; QueryJSON:%s" % (sys_name, json.dumps(json_search, ensure_ascii=False, default=lambda x: x.__dict__)))
        response = self.es_client.es_search(es_index_name, json_search)
        logger.debug("SYS:[%s]; Result:%s" % (sys_name, json.dumps(response, ensure_ascii=False, default=lambda x: x.__dict__)))
        # process
        ret_process = action(self.config_audit, response)

        return ret_process

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print((args.logFile))
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())