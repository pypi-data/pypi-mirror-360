import json
import traceback
import os
import logging
from icecream.core.protocol.http import Session
from icecream.core.assist import Variables, parameter_handling
from icecream.core.mode.assert_test import Test
from icecream.core.protocol.http import IceRequest
from icecream.core.mode.env_config import EnvConfig
from icecream.core.protocol.http import Response
from icecream.core.protocol.request.http_request import HttpRequest
from icecream.core.test_result import CollectRequestProcess
from icecream.utils.cmrischema import validate
from icecream.utils.common import Utils
from icecream.core.helper.all_function import Function
from icecream.core.helper import system_function

logger = logging.getLogger(__name__)


class IceCream(object):

    def __init__(self):
        self.debug = False
        self.env_config = None  # 相关环境变更配置
        self.test = Test()
        self._variables = Variables()
        self.http_request = IceRequest(self)
        self.request_content = {}
        self._response = None
        self.function = {"ice": self}
        self.collect_info = []
        self.helper = Function
        self.all_items = {}
        self.case_ids = []

    def put_exec_caseid(self, case_id):
        """
        添加测试用例ID到case_ids
        params: case_id
        """
        if len(self.case_ids) > 100:
            self.case_ids.pop(0)
        if case_id not in self.case_ids:
            self.case_ids.append(case_id)

    def get_case_id(self, index):
        """
        通过index获取case_id
        params: index
        return: case_id
        """
        if index < 0:
            index = len(self.case_ids) + index
        if 0 <= index < len(self.case_ids):
            return self.case_ids[index]
        else:
            return f"索引 {index} 无效，超出列表范围"

    def log(self, msg):
        """
        收集控制日志
        :param msg:
        :return:
        """
        self.collect_info.append(msg)

    @property
    def userFunc(self):
        """
        获取文本函数
        :return:
        """
        function = self.function

        class UserFunction:
            def __getattr__(self, item):
                try:
                    return function.get(item)
                except Exception:
                    pass

        return UserFunction()

    @property
    def sysFunc(self):
        """
        获取系统函数
        :return:
        """

        class SysFunction:
            def __getattr__(self, item):
                try:
                    return getattr(system_function, item)
                except Exception:
                    pass

        return SysFunction()

    def load_file_function(self, file_path):
        """
        载入文件文本函数
        :param file_path:
        :return:
        """
        with open(file_path, "r", encoding="utf-8") as f:
            self.load_function(f.read())

    def load_function(self, function):
        """
        载入文本函数
        :param function:
        :return:
        """
        try:
            exec(function, self.function)
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def get_need_env(self):
        """
        需要整理格式化的环境变量，用于上传到盘古系统上
        :return:
        """
        return self._variables.environments_collect

    def get_variables(self):
        return self._variables

    def set_debug(self, mode):
        self.debug = mode

    def load_env_config(self, file_path=None):
        if os.path.exists(file_path):
            self.env_config = EnvConfig(file_path)
            self.set_debug(self.env_config.mode)
            self._variables.load_variables(self.env_config)

    @property
    def verify_util(self):
        """
        通用验证类
        :return:
        """

        class _Verify:
            @property
            def cmri(self):
                return validate

        return _Verify()

    @property
    def file_parser(self):
        class _FileParser(object):
            @staticmethod
            def yaml(file_path):
                return Utils.load_yaml(file_path)

            @staticmethod
            def text(file_path):
                return Utils.load_text(file_path)

        return _FileParser()

    @property
    def response(self) -> Response:
        return self._response

    @property
    def request(self):
        ice_self = self

        class _Request:
            def __init__(self):
                self.params = ice_self.request_content.get("params")
                self.body = ice_self.request_content.get("body")
                self.url = ice_self.request_content.get("url")
                self.header = ice_self.request_content.get("header")

        return _Request()

    @property
    def all_scope_vars(self) -> dict:
        all_variables = {**self._variables.globals_collect, **self._variables.environments_collect,
                         **self._variables.variables_collect}
        return all_variables

    @property
    def variables(self):
        class _Variable:
            @staticmethod
            def set(key, value):
                self._variables.variables_collect[key] = value

            @staticmethod
            def get(key):
                if key in self._variables.variables_collect:
                    return self._variables.variables_collect.get(key)
                return None

            @staticmethod
            def get_all():
                return self._variables.variables_collect

            @staticmethod
            def clear(key: list | str = None):
                if key is None:
                    return
                if isinstance(key, list):
                    for k in key:
                        if k in self._variables.variables_collect:
                            del self._variables.variables_collect[k]
                else:
                    if key in self._variables.variables_collect:
                        del self._variables.variables_collect[key]

            @staticmethod
            def clear_all():
                self._variables.variables_collect = {}

        return _Variable

    @property
    def globals(self):
        class _Global:
            @staticmethod
            def set(key, value):
                self._variables.globals_collect[key] = value

            @staticmethod
            def get(key):
                return self._variables.globals_collect.get(key)

            @staticmethod
            def clear(key=None):
                if key:
                    if key in self._variables.globals_collect:
                        del self._variables.globals_collect[key]
                else:
                    self._variables.globals_collect = {}

        return _Global

    @property
    def environment(self):
        class _Environment(object):
            @staticmethod
            def set(key, value):
                self._variables.environments_collect[key] = value

            @staticmethod
            def get(key):
                return self._variables.environments_collect.get(key)

            @staticmethod
            def get_all():
                return self._variables.environments_collect

            @staticmethod
            def clear(key=None):
                if key:
                    if key in self._variables.environments_collect:
                        del self._variables.environments_collect[key]
                else:
                    self._variables.environments_collect = {}

        return _Environment

    def send_request(self, url, method, params=None, data=None, headers=None, verify=False, **kwargs) -> Response:
        """非主线程请求"""
        url = self._variables.deal_variables(url)
        if headers:
            headers = self._variables.deal_variables(headers)
        if data:
            data = self._variables.deal_variables(data)
        if params:
            params = self._variables.deal_variables(params)
        timeout = kwargs.get("timeout") or os.environ.get("HTTP_TIMEOUT") or 90
        with Session() as session:
            return session.request(url, method, params, data, headers, verify=verify, timeout=timeout, **kwargs).send()

    def download(self, url, params=None, headers=None, verify=False, filepath=None, stream=True, **kwargs) -> str:
        url = self._variables.deal_variables(url)
        if headers:
            headers = self._variables.deal_variables(headers)
        if params:
            params = self._variables.deal_variables(params)
        if filepath is None:
            work_dir = self._variables.environments_collect.get("ICE_WORKSPACE_DIR")
            filepath = os.path.join(work_dir, Utils.make_datetime_filename("temp"))
        with Session() as session:
            reps = session.request(url, "GET", params=params, headers=headers,
                                   verify=verify, stream=stream, **kwargs).send()
            if reps.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in reps.iter_content(chunk_size=1024):  # 循环写入，chunk_size是文件大小
                        f.write(chunk)
            return filepath

    def send_case_request(self, item_id):
        """
        根据测试用例ID获取测试结果
        params: item_id
        return: 测试用例请求结果
        example：
        """
        item = self.all_items.get(item_id)
        test_result = CollectRequestProcess()
        parameter = parameter_handling(test_result, self, item.req_data, item)
        base_request = HttpRequest(self, item.req_data, item.setting)
        return base_request.send(parameter, test_result)

    def send_previous_case(self):
        """
        发送上一个测试用例并获取测试结果
        """
        if len(self.case_ids) >= 2:
            previous_id = self.case_ids[-2]
            res = self.send_case_request(previous_id)
            return res

ice = IceCream()
