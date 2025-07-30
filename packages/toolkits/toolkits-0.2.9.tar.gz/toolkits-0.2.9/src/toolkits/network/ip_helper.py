import socket
import struct

import sys
from log4python.Log4python import log
import importlib
importlib.reload(sys)
logger = log("IpHelper")


def map_strip(str):
    tmp = str.lstrip("0")
    if tmp == "":
        tmp = "0"
    return tmp


def ip2long(ipstr):
    split_str = ipstr.split(".")
    split_str_map = list(map(map_strip, split_str))
    ip = ".".join(split_str_map)
    final_ip = 0
    try:
        final_ip = struct.unpack("!I", socket.inet_aton(ip))[0]
    except:
        logger.error("ErrIP: [%s]" % ipstr)
    return final_ip


def long2ip(ip):
    ip = int(ip)
    return socket.inet_ntoa(struct.pack("!I", ip))
