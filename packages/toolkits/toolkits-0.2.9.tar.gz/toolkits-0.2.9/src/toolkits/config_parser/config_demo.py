# -*- coding: utf-8 -*-

config_global = {
    "db_list": {
        'dev_ops': {
            'desc': "Home 数据库",
            'db_name': "dev_ops",
            'user_name': 'root',
            'password': '4tKTiDYr81YM',
            'host': "192.168.100.155",
            'port': 6606
        },
        'online_alarm':  {
            'desc': "16.15 数据库",
            'user_name': 'db_admin',
            'password': '123QWEas!@#',
            'host': "10.83.16.15",
            'port': 8012,
            'db_name': "sec_admin"
        }
    },
    "kafka_list": {
        "home": {
            'host': "192.168.100.155",
            'port': 9092
        }
    },
    "redis_list": {
        "home": {
            'password': 's1hKcWqRj9Se',
            'host': '192.168.100.155',
            'port': 9379,
            'db': 1
        }
    },
    "zookeeper_list": {
        "home": {
            "bin_path": "/usr/local/dev/kafka/kafka_2.12-2.3.0",
            "ip": "192.168.100.155",
            "port": "2184"
        }
    }
}
