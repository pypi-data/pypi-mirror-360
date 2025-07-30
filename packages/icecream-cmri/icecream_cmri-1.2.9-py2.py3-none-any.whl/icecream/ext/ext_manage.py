"""
@author:cmcc
@file: ext_manage.py
@time: 2024/7/21 23:41
"""
import logging
import traceback
from icecream.ext.xray import Xray

logger = logging.getLogger(__name__)


class ExtManage:

    def __init__(self, runner):
        self.runner = runner
        self.ic = runner.ic
        self.ext = []
        self.xray = None
        self.proxies = None

    def start_ext_plugin(self):
        """
        开启三方插件
        :return:
        """
        ext = self.ic.env_config.ext
        if ext:
            xray_config = ext.get("xray", {})
            if xray_config.get("status") == "on":
                auto_attack = xray_config.get("auto_distribution", "off") == "on"
                self.xray = Xray(self.runner.workdir, xray_config.get("call_back_url"), xray_config.get("delay_time"),
                                 flag_auto_attack=auto_attack, driver=self.ic)
                self.ext.append(self.xray)
                self.xray.async_start()
                self.proxies = self.xray.proxies

    def xray_auto_attack(self, item):
        if not self.xray:
            return
        record = self.runner.record.get(item.from_to)
        if record:
            self.xray.start_attack(record, item)
        else:
            self.xray.start_attack(None, item)

    def stop_ext_plugin(self):
        for ext in self.ext:
            try:
                ext.stop()
            except Exception:
                logger.warning(traceback.format_exc())
