# -*- coding: utf-8 -*-
import argparse
import json
import sys
import redis
from log4python.Log4python import log
import traceback
import importlib

importlib.reload(sys)
logger = log("RedisMgmt")

host_ip = '192.168.100.110'
redis_info = {
    'password': 'password',
    'host': host_ip,
    'port': 6307
}


class RedisMgmt:
    def __init__(self, redis_db=8):
        self.redisCli = redis.StrictRedis(host=redis_info['host'], port=redis_info['port'],
                                          password=redis_info['password'], db=int(redis_db))

    def dump_queue(self, store_type, key_source, key_destination):
        data_list = []
        while True:
            data = self.redisCli.lpop(key_source)
            if data:
                data_list.append(data)
            else:
                break

        if store_type == "redis":
            for data_item in data_list:
                self.redisCli.rpush(key_destination, data_item)
        else:
            fp = open(key_destination, "a+")
            content = "\n".join(data_list)
            fp.write(content)
            fp.close()

        logger.debug("Dumps Success data number; [%s]" % str(len(data_list)))

    def load_to_redis(self, store_type, key_source, key_destination):
        data_list = []
        if store_type == "redis":
            while True:
                data = self.redisCli.lpop(key_source)
                if data:
                    data_list.append(data)
                else:
                    break
        else:
            fp = open(key_source, "r")
            data = fp.readlines()
            if data:
                if isinstance(data, list):
                    data_list.extend(data)
                else:
                    data_list.append(data)
            fp.close()

        for data_item in data_list:
            self.redisCli.rpush(key_destination, data_item.strip())
        logger.debug("Loads Success data number; [%s]; Data:[%s]" % (str(len(data_list)),
                                                                     json.dumps(data_list, ensure_ascii=False)))


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("redis_db", type=str, help="specify the redis_db")
        parser.add_argument("store_type", type=str, help="specify the store type [file|redis]")
        parser.add_argument("action_type", type=str, help="specify the action type [load|dump]")
        parser.add_argument("source", type=str, help="specify the queue_source or file")
        parser.add_argument("destination", type=str, help="specify the queue_destination or file")
        args = parser.parse_args()

        redis_mgmt = RedisMgmt(args.redis_db)
        if args.store_type not in ("file", "redis"):
            logger.debug("Store Type Error! not in [file, redis]")

        if args.action_type not in ("dump", "load"):
            logger.debug("Store Type Error! not in [dump, load]")

        if args.action_type == "dump":
            redis_mgmt.dump_queue(args.store_type, args.source, args.destination)
        else:
            redis_mgmt.load_to_redis(args.store_type, args.source, args.destination)

    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
