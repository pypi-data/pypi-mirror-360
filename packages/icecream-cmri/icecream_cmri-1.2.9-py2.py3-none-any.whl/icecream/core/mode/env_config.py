"""
@author:cmcc
@file: env_config.py
@time: 2024/7/22 0:16
"""
import yaml
import os
from icecream.core.exceptions import YamlFormatException


class EnvConfig:
    """
        ice配置数据维护, env配置文件
            ENV_CONFIG:
              ENVIRONMENTS:
              - ICE_ENV_NAME: AIIP九天能力平台
                ICE_USERNAME: ningruhu
                AIIP_DOMAIN: http://aiipgateway.jiutian.hq.cmcc
                AIIP_HOST: http://172.22.16.231:30080
              EXT:
                xray:
                  call_back_url: xxxxxx
                  status: on/off
                  delay_time: 10
              ACTIVE: AIIP九天能力平台
        """

    def __init__(self, file_path):
        self.global_data = []
        self.env_data = []
        self.mode = False
        self.other = None
        self.error_stop_flag = None
        self.ext = {}
        self._load(file_path)

    def _load(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                try:
                    data = yaml.load(f.read(), yaml.FullLoader)
                    self._parser(data)
                except YamlFormatException:
                    raise YamlFormatException

    def _parser(self, data):
        config = data.get('ENV_CONFIG')
        active = ""
        if config:
            if 'ERROR_STOP_FLAG' in config:
                self.error_stop_flag = config.get('ERROR_STOP_FLAG')
            else:
                self.error_stop_flag = "off"
        if config and 'ACTIVE' in config:
            active = config.get('ACTIVE')
        if config and 'GLOBALS' in config:
            self.global_data = config.pop('GLOBALS')
        if config and 'ENVIRONMENTS' in config:
            env_datas = config.pop('ENVIRONMENTS')
            for env_data in env_datas:
                if env_data['ICE_ENV_NAME'] == active:
                    self.env_data = env_data
                    break
            else:
                self.env_data = env_datas[0]
        if config and 'MODE' in config:
            self.mode = config.pop('MODE')
        self.ext = config.get("EXT")
