"""
@author:cmcc
@file: function.py
@time: 2022-08-26 17:49
"""
from icecream.core.helper.opredis import OPRedis
from icecream.core.helper.encryption import Crypt
from icecream.utils.common import FileUtils
from icecream.core.helper.system_function import *


class Function:

    @classmethod
    def read_csv(cls, path, tag="ice", split=",", is_title=True, encoding="utf-8"):
        return FileUtils.read_csv(path, tag, split, is_title, encoding)

    @classmethod
    def redis(cls, host=None, port=None, passwd=None, startup_nodes=None, max_connections=2000):
        return OPRedis(host, port, passwd, startup_nodes, max_connections)

    @classmethod
    def crypt(cls):
        """
        加解密操作类
        :return:
        """
        return Crypt

    db = DBConnectFunction()
    file = FileProcessingFunction()
    other = OtherFunction()
    random = RandomFunction()
    time = TimeFunction()
