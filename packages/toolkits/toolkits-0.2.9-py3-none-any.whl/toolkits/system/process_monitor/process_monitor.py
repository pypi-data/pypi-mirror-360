# -*- coding: utf-8 -*-
import importlib
import json
import os
import sys

import fire
from log4python.Log4python import log
from unipath import Path

from toolkits.databases.database_client_util import DatabaseClientUtil
from toolkits.system.priority_tasks import PriorityTasks
from toolkits.system.shell_helper import exec_shell

importlib.reload(sys)
logger = log("ProcessMonitor")


class ProcessMonitor:
    """
config_monitor = {
    "circus_config_path": "/circus/circus.conf",
    "monitor_queue_name": "process_monitor",
    "monitor_queue_switch": "process_monitor_switch",
    "redis_info": {
        "password": "just_your_redis_password",
        "host": "your_redis_ip",
        "port": 8081,
        "db": 6
    }
}

task_monitor_config =
{
  "name": "TmpMonitor",
  "cmd": "python",
  "args": "tmp_monitor.py",
  "working_dir": ".",
  "copy_env": "true",
  "numprocesses": "1",
  "stdout_stream.class": "FileStream",
  "stdout_stream.filename": "tmp_monitor.log",
  "stdout_stream.max_bytes": "1073741824",
  "stdout_stream.backup_count": "5"
}

        :param config_file_path:
        :param monitor_config_filename:
        """

    def __init__(self, config_file_path, monitor_config_filename="monitor.json"):
        self.__base_path = self.__get_script_dir()
        self.__work_path = self.__get_run_dir()
        self.__monitor_config_filename = monitor_config_filename
        self.__config_file_path = config_file_path
        self.__config_path = None
        self.__redis_info = None
        self.__monitor_queue_switch = None
        self.__monitor_queue_name = None
        self.__task_name = ""
        self.__task_config = ""
        self.__task_queue_client = None
        self.__init_global_config()

    def __init_global_config(self):
        if Path(self.__config_file_path).exists():
            file_path_final = self.__config_file_path
        else:
            relative_path = "%s/%s" % (self.__work_path, self.__config_file_path)

            if Path(relative_path).exists():
                file_path_final = relative_path
            else:
                msg = "global config file was not Found!!!"
                print(msg)
                raise Exception(msg)

        logger.debug("GlobalConfigPath:[%s]" % file_path_final)
        fp = open(file_path_final)
        lines = fp.readlines()
        fp.close()

        config_monitor = json.loads("".join(lines))
        self.__config_path = config_monitor['circus_config_path']
        self.__redis_info = config_monitor['redis_info']
        self.__monitor_queue_switch = config_monitor['monitor_queue_switch']
        self.__monitor_queue_name = config_monitor['monitor_queue_name']

    @staticmethod
    def __get_run_dir():
        script_path = sys.argv[0]
        process_id = os.getpid()
        link_path = "/proc/%s/cwd" % process_id
        read_link_path = "ls -la %s|awk -F'->' '{print $2}'" % link_path
        ret = exec_shell(read_link_path)
        if str(ret['exit_code']) == "0":
            full_path = str(ret['stdout'][0]).strip()
        else:
            if script_path[0] != "/":
                path_tmp = "%s/%s" % (os.getcwd(), script_path)
            else:
                path_tmp = script_path
            full_path = os.path.dirname(path_tmp)
        return full_path

    @staticmethod
    def __get_script_dir():
        return os.path.dirname(os.path.realpath(__file__))

    def __get_monitor_config(self):
        file_path = "%s/%s" % (self.__work_path, self.__monitor_config_filename)
        config_info = None
        if Path(file_path).exists():
            fp = open(file_path)
            lines = fp.readlines()
            config_info = "".join(lines)
        return config_info

    def __prepare_config(self):
        name_tasks = None
        config_task = []
        config_info = self.__get_monitor_config()
        log_info = ['cmd', 'args', 'working_dir', 'copy_env',
                    'numprocesses', 'stdout_stream.class',
                    'stdout_stream.filename',
                    'stdout_stream.max_bytes',
                    'stdout_stream.backup_count']

        if config_info:
            config_obj = json.loads(config_info)
            name_tasks = config_obj['name']
            config_task = ["[watcher:%s]" % name_tasks]

            work_path = self.__get_run_dir()
            logs_path = "%s/logs/" % work_path
            if not Path(logs_path).exists():
                Path(logs_path).mkdir(parents=True)

            for item in log_info:
                if item in config_obj:
                    if ("working_dir" == item and item in config_obj) \
                            and (config_obj['working_dir'] == "." or config_obj['working_dir'] == ""):
                        config_task.append("%s = %s" % (item, work_path))
                        continue

                    if "stdout_stream.filename" == item and item in config_obj:
                        file_name = config_obj['stdout_stream.filename']
                        if file_name != "":
                            logs_file_path = file_name
                            if file_name.find("\\") < 0 and file_name.find("/") < 0:
                                logs_file_path = "%s/%s" % (logs_path, file_name)
                            config_task.append("%s = %s" % (item, logs_file_path))
                        else:
                            logs_file_path = "%s/%s" % (logs_path, "%s.log" % name_tasks)
                            config_task.append("%s = %s" % (item, logs_file_path))
                        continue

                    config_task.append("%s = %s" % (item, config_obj[item]))

            for item in config_obj:
                if item not in log_info:
                    if item == "name":
                        continue
                    dict_val = config_obj[item]
                    if config_obj[item] is None:
                        dict_val = ""
                    config_task.append("%s = %s" % (item, dict_val))
        else:
            msg_err = "No config be found!!!!"
            print(msg_err)
            logger.debug(msg_err)
            raise Exception(msg_err)

        return name_tasks, config_task

    def __init_env(self):
        self.__task_name, self.__task_config = self.__prepare_config()
        self.__task_queue_client = self.__init_tasks_queue_client(self.__redis_info, self.__monitor_queue_name)
        cmd = {
            'type': 'start',  # install, start, restart, stop, remove
            'name': self.__task_name,
            'config': "\n".join(self.__task_config),
        }
        return cmd

    def __switch_process(self, status):
        database_init = DatabaseClientUtil(None)
        redis_client = database_init.get_redis_client(self.__redis_info['db'], self.__redis_info)
        redis_client.set(self.__monitor_queue_switch, status)

    def switch_tasks_queue_on(self):
        self.__switch_process("on")

    def switch_tasks_queue_off(self):
        self.__switch_process("off")

    def get_switch_tasks_status(self):
        database_init = DatabaseClientUtil(None)
        redis_client = database_init.get_redis_client(self.__redis_info['db'], self.__redis_info)
        return redis_client.get(self.__monitor_queue_switch)

    def start_daemon_server(self):
        """
        CMD:
        circusd --daemon --pidfile /home/vagrant/dev/circus/circus.pid --log-level debug --log-output /home/vagrant/dev/circus/circus.log /home/vagrant/dev/circus/circus.conf
        :return:
        """
        self.switch_tasks_queue_on()
        self.__init_tasks_queue_server(self.__redis_info, self.__exec_cmd_list,
                                       self.__monitor_queue_switch,
                                       self.__monitor_queue_name)

    def get_task_status(self, task_name):
        """
        error| stopped| active
        :param task_name:
        :return:
        """
        cmd_exec = "circusctl status %s" % task_name
        ret = exec_shell(cmd_exec)
        status = "error"
        if str(ret['exit_code']) == "0":
            status = str(ret['stdout'][0]).strip()
        return status

    def __write_monitor_config(self, task_config):
        fp = open(self.__config_path, "a+")
        fp.write("\n")
        fp.write(task_config)
        fp.close()

    def __process_install(self, task_name, task_config):
        status = self.get_task_status(task_name)
        if status in ["active", "stopped"]:
            msg = "Task[%s] was exists!! please check the configure info" % task_name
            logger.error(msg)
            print(msg)
        elif status == "error":
            self.__write_monitor_config(task_config)
            cmd_exec = "circusctl reloadconfig | circusctl start %s" % task_name
            ret = exec_shell(cmd_exec)
            if ret['exit_code'] == 0:
                logger.debug("Task[%s] was ready!!" % task_name)
            else:
                logger.error("Task[%s] was execute wrong!!" % task_name)
        else:
            msg = "Task[%s] status was wrong!!!! please check the configure info" % task_name
            logger.error(msg)

    def __process_uninstall(self, task_name):
        self.__process_cmd(task_name, "stop")

    @staticmethod
    def __process_cmd(task_name, cmd_type):
        cmd_exec = "circusctl %s %s" % (cmd_type, task_name)
        logger.debug("CMD:[%s]" % cmd_exec)
        ret = exec_shell(cmd_exec)
        if str(ret['exit_code']) != "0":
            logger.error("Error:[%s]" % "\n".join(ret['stderr']))

    def __exec_cmd(self, cmd_obj):
        logger.debug("CMD_INFO:[%s]" % json.dumps(cmd_obj, ensure_ascii=False))
        status = self.get_task_status(cmd_obj['name'])
        logger.debug("Task[%s] current status:[%s]" % (cmd_obj['name'], status))

        if cmd_obj['type'] == "install":
            self.__process_install(cmd_obj['name'], cmd_obj['config'])
        elif cmd_obj['type'] == "uninstall":
            self.__process_uninstall(cmd_obj['name'])
        else:
            if status != "error":
                self.__process_cmd(cmd_obj['name'], cmd_obj['type'])
            else:
                msg = "Task[%s] status is unknown!!!" % cmd_obj['name']
                logger.error(msg)
                print(msg)

    def __exec_cmd_list(self, cmd_info):
        """
        redis_info['db'] = 8
        cmd_info = {
        'type': 'start',  # install, start, restart, stop, remove
        'name': 'task_name',
        'config': 'task_config',
        }
        :return:
        """
        entity_list = []
        if isinstance(cmd_info, str):
            entity_list.append(json.loads(cmd_info))
        elif isinstance(cmd_info, list):
            for item in cmd_info:
                entity_list.append(json.loads(item))
        else:
            logger.debug("Error:[%s]" % json.dumps(cmd_info, ensure_ascii=False))

        for item_cmd in entity_list:
            self.__exec_cmd(item_cmd)

    @staticmethod
    def __send_tasks(task_client, cmd_data, level="high"):
        if level == "high":
            task_client.send_high_task(cmd_data)

    @staticmethod
    def __init_tasks_queue_server(redis_conn_info, task_process_worker,
                                  task_switch_name, tasks_queue_name="process_monitor"):
        task = PriorityTasks(redis_conn_info, tasks_queue_name, work_status_queue_name=task_switch_name)
        task.worker(task_process_worker, records_count=100, time_out=10)

    @staticmethod
    def __init_tasks_queue_client(redis_conn_info, tasks_queue_name="process_monitor"):
        task_client = PriorityTasks(redis_conn_info, tasks_queue_name)
        return task_client

    def __process_cmd_info(self, cmd_type):
        cmd = self.__init_env()
        cmd['type'] = cmd_type
        self.__send_tasks(self.__task_queue_client, json.dumps(cmd, ensure_ascii=False))

    def get_task_name(self):
        self.__init_env()
        return self.__task_name

    def get_task_config(self):
        self.__init_env()
        return self.__task_config

    def monitor_start(self):
        self.__process_cmd_info("start")

    def monitor_restart(self):
        self.__process_cmd_info("restart")

    def monitor_stop(self):
        self.__process_cmd_info("stop")

    def monitor_install(self):
        self.__process_cmd_info("install")

    def monitor_uninstall(self):
        self.__process_cmd_info("uninstall")

    def __worker(self):
        pass


if __name__ == '__main__':
    fire.Fire(ProcessMonitor)
