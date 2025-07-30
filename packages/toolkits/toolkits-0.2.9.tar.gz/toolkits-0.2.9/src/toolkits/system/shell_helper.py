# -*- coding: utf-8 -*-
import _thread
import argparse
import asyncio
import importlib
import os
import pprint
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from multiprocessing import Process
from threading import Timer

import arrow
from log4python.Log4python import log
from unipath import Path

from toolkits.system.file_helper import read_content

importlib.reload(sys)
logger = log("shellHelper")


def change_the_path_split(file_path):
    path_split_str_win = "\\"
    path_split_str_linux = "/"
    if str(sys.platform).find("win") >= 0:
        path_final = str(file_path).replace(path_split_str_linux, path_split_str_win)
    else:
        path_final = str(file_path).replace(path_split_str_win, path_split_str_linux)
    return path_final


def include_path(target_root_directory, relative_path_list):
    for item in relative_path_list:
        item = change_the_path_split(item)
        path_parent = "%s/%s" % (target_root_directory, item)
        sys.path.append(path_parent)


def get_relative_directory_levels(script_file_path, relative_levels):
    path_cur = os.path.dirname(os.path.realpath(script_file_path))
    directory_target = "/.." * relative_levels
    target_root_path = "%s%s" % (path_cur, directory_target)
    return change_the_path_split(target_root_path)


def run_with_timeout(timeout, default, f, *args, **kwargs):
    if not timeout:
        return f(*args, **kwargs)
    timeout_timer = Timer(timeout, _thread.interrupt_main)
    try:
        timeout_timer.start()
        result = f(*args, **kwargs)
        return result
    except KeyboardInterrupt:
        return default
    finally:
        timeout_timer.cancel()


def exec_cmd(cmd, work_path):
    exec_shell_with_pipe(cmd, work_path=work_path)


def worker(cmd, work_path):
    p = Process(target=exec_cmd, args=(cmd, work_path))
    p.start()
    os._exit(1)


def exec_external_cmd_background(cmd, work_path=""):
    p = Process(target=worker, args=(cmd, work_path))
    p.start()
    p.join()


def file_is_used(monitor_file):
    # fuser or lsof to check file's status
    cmd = "lsof %s" % monitor_file
    ret = exec_shell_with_pipe(cmd)
    if not ret:
        return True
    else:
        return False


def exec_shell_with_pipe(cmd, timeout=0, work_path=""):
    """exeShellWithPipe("grep 'processor' /proc/cpuinfo | sort -u | wc -l")

return-val
     output-lines-list  # line list ['output_01', 'output_02']

    :param work_path:
    :param timeout:
    :param cmd:  exec command
    """
    result = []
    none_num = 0
    if cmd == "" or cmd is None:
        return "No Cmd Input"
    if work_path == "":
        scan_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        scan_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work_path)
    while True:
        if none_num > 3:
            break
        if timeout != 0:
            ret = run_with_timeout(timeout, None, scan_process.stdout.readline)
        else:
            ret = scan_process.stdout.readline()
        if ret == "" or ret is None:
            none_num += 1
        else:
            result.append(ret.strip())
            none_num = 0
    return result


async def run_command_async(command, timeout=5, encoding="utf-8", shell=False, cwd=None, env=None):
    process = None
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=shell,
            cwd=cwd,
            env=env
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        ret = {
            "exit_code": process.returncode,
            "stdout": str(stdout.decode(encoding)).splitlines(False),
            "stderr": str(stderr.decode(encoding)).splitlines(False)
        }
        return ret
    except asyncio.TimeoutError:
        if process and process.returncode is None:
            process.terminate()
        ret = {
            "exit_code": -1,
            "stdout": None,
            "stderr": f"Command timed out after {timeout} seconds."
        }
        return ret


def get_loop_obj():
    try:
        # 尝试获取当前线程的事件循环（可能会失败）
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        # 如果报错 "There is no current event loop..."，则创建新的事件循环
        if "There is no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            # 其他 RuntimeError 直接抛出
            raise
    return loop


def exec_shell_async(command, timeout=60 * 10, encoding="utf-8", cwd=None, env=None):
    """
    异常执行命令，检测执行时间超时
    :param command:  要执行的命令
    :param timeout:  等待的超时时间，超时后，返回: exit_code=-1
    :param encoding: 解析命令行返回数据的编码格式，默认为：utf-8, 中文Windows环境可指定为：GBK
    :param env:
    :param cwd:
    :param shell:
    :return: {'exit_code': 0, 'stdout': '\r\n正在 Ping 127.0.0.1 具有 32 字节的数据:\r\n来自 127.0.0.1 的回复: 字节=32 时间<1ms TTL=128\r\n\r\n', 'stderr': ''}
    """
    if command == "" or command is None:
        ret = {
            "exit_code": -1,
            "stdout": "",
            "stderr": "No cmd was found"
        }
        return ret

    # asyncio.get_event_loop()
    loop = get_loop_obj()
    return loop.run_until_complete(run_command_async(command, timeout=timeout, encoding=encoding, cwd=cwd, env=env))


def exec_shell(cmd, timeout=0, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None,
               preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False,
               startupinfo=None, creationflags=0):
    """exec_shell("grep 'processor' /proc/cpuinfo | sort -u | wc -l")


return-code::

    ret = {
        "exit_code": return_code,  # 0 or -1
        "stdout": stdout_msg,  # line list ['output_01', 'output_02']
        "stderr": stderr_msg   # line list ['output_01', 'output_02']
    }
code-end

    :param cmd:  exec command
    :param preexec_fn:
    :type stdin: object
    :param executable:
    :param cwd:
    :param timeout:
    :return: return a dict to caller

    """
    if cmd == "" or cmd is None:
        ret = {
            "exit_code": -1,
            "stdout": "",
            "stderr": "No cmd was found"
        }
        return ret

    fp_out = subprocess.PIPE
    fp_err = subprocess.PIPE
    temp_dir = tempfile.gettempdir()
    stdout = os.path.join(temp_dir, "stdout_%s" % str(uuid.uuid4()).replace("-", "").upper())
    stderr = os.path.join(temp_dir, "stderr_%s" % str(uuid.uuid4()).replace("-", "").upper())
    if stdout:
        fp_out = open(stdout, "w+")
    if stderr:
        fp_err = open(stderr, "w+")

    scan_process = subprocess.Popen(cmd, shell=True, stdout=fp_out, stderr=fp_err, cwd=cwd, bufsize=bufsize,
                                    executable=executable, stdin=stdin,
                                    preexec_fn=preexec_fn, close_fds=close_fds,
                                    env=env, universal_newlines=universal_newlines,
                                    startupinfo=startupinfo, creationflags=creationflags)

    return_code = None
    while True:
        return_code = scan_process.poll()
        if return_code is None:
            time.sleep(1)
        else:
            break

    fp_out.close()
    fp_err.close()
    stdout_msg = read_content(stdout)
    stderr_msg = read_content(stderr)
    Path(stderr).remove()
    Path(stdout).remove()

    ret = {
        "exit_code": return_code,
        "stdout": stdout_msg,
        "stderr": stderr_msg
    }
    return ret


def dump_data(data_to_dump, file_prefix_name="py_dump_data", dump_path=None):
    date_str = arrow.now().format('YYYYMMDD_HHmmss')
    file_name = "%s_%s_%s.dat" % (file_prefix_name, date_str, str(uuid.uuid4()).replace("-", ""))
    tmp_dir = tempfile.gettempdir()
    if dump_path:
        try:
            if not Path(tmp_dir).exists():
                Path(tmp_dir).mkdir(parents=True)
            tmp_dir = dump_path
        except Exception as ex:
            logger.error("Error: %s" % ex)
            logger.error(traceback.format_exc())

    data_dump_file = os.path.join(tmp_dir, file_name)
    fp = open(data_dump_file, "w+")

    if type(data_to_dump) is str or type(data_to_dump) is str:
        fp.write("%s\n" % data_to_dump)
    elif type(data_to_dump) is list:
        for item in data_to_dump:
            str_line = pprint.pformat(item)
            fp.write("%s\n" % str_line)
    else:
        str_line = pprint.pformat(data_to_dump)
        fp.write("%s\n" % str_line)
    fp.close()

    return data_dump_file


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("logFile", type=str, help="specify the log file's path")
        args = parser.parse_args()
        print((args.logFile))
        # exec_shell()
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())