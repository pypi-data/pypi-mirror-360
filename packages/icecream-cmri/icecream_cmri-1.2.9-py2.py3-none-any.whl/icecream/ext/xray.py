"""
@author:ningruhu
@file: xray.py
@time: 2022-08-18 14:19
"""
import logging
import socket
import os
import re
import json
import threading
import subprocess
import time
from typing import NoReturn

from icecream.core.assist import parameter_handling
from icecream.core.test_result import CollectRequestProcess
from icecream.utils.process_util import ProcessUtil
from icecream.core.mode.test_suite import TestItem
from icecream.core.protocol.request.http_request import HttpRequest


LOCAL_PORT = 9300
_init_local_port = 9300

logger = logging.getLogger(__name__)


def is_port_listening(port, host=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((str(host) if host else '127.0.0.1', port))
    s.close()
    return result == 0


def next_local_port():
    global _init_local_port
    _init_local_port = _init_local_port + 1 if _init_local_port < 1000 else LOCAL_PORT
    while is_port_listening(_init_local_port):
        _init_local_port += 1
    return _init_local_port


class Xray:

    def __init__(self, workdir=None, webhook_url=None, delay_time=None, json_output=False, flag_auto_attack=False, driver=None):
        self.xray_path = self._find_xray_path()
        self.port = LOCAL_PORT
        self.host = os.environ.get("XRAY_HOST", "127.0.0.1")
        self.process = None
        self.workdir = workdir
        self.delay_time = delay_time or 15
        self.json_output = json_output
        self.workhook_url = webhook_url
        self.last_time = 0
        self.proxies = None
        self.flag_auto_attack = flag_auto_attack
        self.auto_attack = AutoAttack(driver)

    def _find_xray_path(self):
        """
        查找xray 所在目录
        :return:
        """
        import distutils
        if "spawn" not in dir(distutils):
            import distutils.spawn
        xray_cmd = distutils.spawn.find_executable("xray")
        if xray_cmd:
            xray_path = os.path.realpath(xray_cmd)
            return xray_path

    def _load_xray(self):
        if is_port_listening(int(self.port)):
            self.port = next_local_port()
        self.proxies = {"http": f"http://127.0.0.1:{self.port}", "https": f"http://127.0.0.1:{self.port}"}
        cmd_line = [
            "xray",
            "webscan",
            "--listen", f"{self.host}:{self.port}",
            "--html-output",
            os.path.join(
                self.workdir, "html_xray_%s.html" % time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
            ]
        if self.workhook_url:
            cmd_line.extend(
                [
                    "--webhook-output",
                    self.workhook_url
                ]
            )
        if self.json_output:
            cmd_line.extend(
                [
                    "--json-output",
                    os.path.join(
                        self.workdir, "json_xray_%s.json" % time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
                ]
            )
        if os.name != "nt":
            cmd_line = [" ".join(cmd_line)]
        logger.debug(cmd_line)
        self.process = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        cwd=os.path.dirname(self.xray_path))

    def _print_process(self):
        if self.process:
            while self.process.poll() is None:
                line = self.process.stdout.readline().strip()  # 按行获取日志
                if line:
                    self.last_time = time.time()
                    logger.debug(line.decode("utf-8"))

    def sync_start(self):
        self._load_xray()
        self._print_process()

    def async_start(self):
        self._load_xray()
        time.sleep(10)
        self.last_time = time.time()
        t = threading.Thread(target=self._print_process)
        t.setDaemon(True)
        t.start()

    def stop(self):
        while time.time() - self.last_time < self.delay_time:
            time.sleep(1)
        if self.process:
            self.process.terminate()
            self.process.kill()
        ProcessUtil.clear_history_process("xray")
        logger.info("xray service stop")

    def extract_hole_by_html(self):
        """
        从html里抽取漏洞数据
        :return:
        """
        reports = os.listdir(self.workdir)
        pattern = re.compile(r'<script class=\'web-vulns\'>webVulns.push\((.*?)\)</script>')
        result = []
        for report in reports:
            if report.startswith("html_xray"):
                with open(os.path.join(self.workdir, report), 'r', encoding='utf-8') as f:
                    lines = f.read()
                    result = pattern.findall(lines)
        return list(map(lambda x: json.loads(x), result))

    def start_attack(self, record: dict, item):
        self.auto_attack.attack(record, item, self.proxies, self.flag_auto_attack)


class AutoAttack:
    def __init__(self, driver):
        self.test_record_ids = []
        self.driver = driver

    def is_exists(self, test_id) -> bool:
        return test_id in self.test_record_ids

    def attack(self, record, item: TestItem, proxies, attack_mode) -> NoReturn:
        if self.is_exists(item.from_to):  # 已攻击过，不用攻击了
            return
        logger.info(f"item: {type(item.request)}")
        self._attack(record, item, proxies, attack_mode)

    def _attack(self, record, item, proxies, attack_mode):
        record = record
        test_result = CollectRequestProcess()
        parameter = parameter_handling(test_result, self.driver, item.req_data, item)
        send_http = HttpRequest(self.driver, item.req_data, {**item.setting, "proxies": proxies})
        send_http.send(parameter, test_result, xray_method="simple" if attack_mode else None)


if __name__ == '__main__':
    xray = Xray(r"D:\TEMP_TEST\xray")
    xray.sync_start()
    # print(xray.extract_hole_by_html())
