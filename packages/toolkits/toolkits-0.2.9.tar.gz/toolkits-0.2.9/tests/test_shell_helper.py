from toolkits.system.shell_helper import exec_shell_async


def test_exec_shell_async():
    ret = exec_shell_async("ping -n 11 127.0.0.1", 5, encoding='GBK', cwd="C:\\")
    assert ret['exit_code'] != 0
