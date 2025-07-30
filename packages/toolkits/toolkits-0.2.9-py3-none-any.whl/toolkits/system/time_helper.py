# -*- coding: utf-8 -*-
import argparse
import re
import sys
import arrow
from log4python.Log4python import log
import traceback
import importlib
importlib.reload(sys)
logger = log("timeHelper")


class TimeCheck:
    def __init__(self):
        self.time_begin = 0
        self.time_end = 0

    def time_audit_begin(self):
        self.time_begin = arrow.now().timestamp

    def time_audit_end(self):
        self.time_end = arrow.now().timestamp
        return self.time_end - self.time_begin


def get_arrow_time(time_str):
    ret_time = None
    try:
        ret = re.search("([0-9]{4})([0-9]{2})([0-9]{2})", time_str, re.MULTILINE)
        if not ret:
            ret = arrow.get(time_str)
            if ret:
                ret_time = ret.timestamp
        else:
            ret_time = arrow.get("%s-%s-%s 00:00:00" % (ret.group(1), ret.group(2), ret.group(3))).timestamp
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
    finally:
        return ret_time


def get_month_end(timestamp):
    arr = arrow.get(timestamp)
    return arrow.get(arr.shift(months=1).format("YYYY-MM-01 00:00:00")).timestamp


def get_local_timestamp(datetime_str, time_zone="Asia/Shanghai"):
    """
    :param datetime_str: "2018-08-17 00:00:00"
    :param time_zone: ""Asia/Shanghai"
    :return:  unix timestamp
    """
    return arrow.get(datetime_str).replace(tzinfo=time_zone).timestamp


def get_time_range_interval(time_begin, time_end, interval="1d", month_split=False):
    """ usage:
        time_day_begin = arrow.get(ret["time_begin"]).format('YYYY-MM-DD')
        time_day_end = arrow.get(ret["time_end"]).format('YYYY-MM-DD')
        :param month_split:  split time by month, default is False
        :param interval:
        :param time_end:
        :param time_begin: """
    ts_begin = get_arrow_time(time_begin)
    ts_end = get_arrow_time(time_end)
    ts_query_end = ts_begin

    time_range = []
    unit = interval[-1:]
    number = interval[:-1]
    secs_unit = {
                    "h": 60 * 60,
                    "m": 60,
                    "d": 60 * 60 * 24
                    }
    time_interval = 1

    if unit in list(secs_unit.keys()):
        time_interval = secs_unit[unit] * int(number)
    else:
        logger.error("Err: interval format error[%s]!!" % interval)
        exit(-1)
    if ts_begin is None or ts_end is None:
        logger.error("time format error..")
        exit(-1)
    if ts_begin > ts_end:
        logger.error("Err: time_begin bigger than time_end!!")
        exit(-1)
    if ((ts_end - ts_begin) < time_interval) and (ts_end != ts_begin):
        logger.error("Err: 'interval' is smaller than the gap of between time_begin and time_end !!")
        exit(-1)

    while True:
        ts_query_begin = ts_query_end
        ts_query_end = ts_query_begin + time_interval
        ts_month_end = get_month_end(ts_query_begin)

        if month_split:
            if ts_query_end > ts_month_end:
                if ts_query_end > ts_end:
                    ts_query_end = ts_end
                else:
                    ts_query_end = ts_month_end
            else:
                if ts_query_end > ts_end:
                    ts_query_end = ts_end
        else:
            if ts_query_end > ts_end:
                ts_query_end = ts_end

        time_range.append({
            "time_begin": ts_query_begin,
            "time_end": ts_query_end
        })

        if ts_query_end >= ts_end:
            break
    return time_range


def get_time_range(time_begin, time_end, days_interval):
    ts_begin = get_arrow_time(time_begin)
    ts_end = get_arrow_time(time_end)
    time_range = []

    if ts_begin is None or ts_end is None:
        print("time format error..")
        exit(-1)
    ts_query_begin = ts_begin
    day_secs = 60 * 60 * 24
    ts_query_end = ts_query_begin - day_secs * 1

    while True:
        if ts_query_end >= ts_end:
            break

        time_interval = day_secs * 1
        if (ts_end - ts_begin) > (day_secs * days_interval):
            time_interval = day_secs * days_interval
        ts_query_begin = ts_query_end + day_secs * 1
        ts_query_end = ts_query_begin + time_interval
        ts_month_end = get_month_end(ts_query_begin)

        if ts_query_end > ts_month_end:
            if ts_query_end > ts_end:
                ts_query_end = ts_end
            else:
                ts_query_end = ts_month_end
        else:
            if ts_query_end > ts_end:
                ts_query_end = ts_end

        time_day_begin = arrow.get(ts_query_begin).format('YYYY-MM-DD')
        time_day_end = arrow.get(ts_query_end).format('YYYY-MM-DD')

        time_range.append({
            "time_begin": ts_query_begin,
            "time_end": ts_query_end
        })

    return time_range


if __name__ == '__main__':
    try:
        # parser = argparse.ArgumentParser()
        # parser.add_argument("logFile", type=str, help="specify the log file's path")
        # args = parser.parse_args()
        time_range = get_time_range_interval("2018-01-02 00:00:00", "2018-01-02 03:00:00", "1h")
        for time_item in time_range:
            print(("TimeRange:%s-%s" % (arrow.get(time_item['time_begin']).format('YYYY-MM-DD HH:mm:ss'), arrow.get(time_item['time_end']).format('YYYY-MM-DD HH:mm:ss'))))
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())
