"""
@author:cmcc
@file: assist.py
@time: 2022-07-26 16:50
"""
import copy
import itertools
import json
import logging
import os
import traceback
from typing import Tuple, List, Generator, Dict, Text, Any, Callable, Set
from requests_toolbelt.multipart.encoder import MultipartEncoder
from icecream.utils.common import Utils, FileUtils
from icecream.utils.pariwise import PariwiseUtil
from icecream.utils.encryption import decode_passwd
from icecream.utils.parse_params import ParseParamsOlder as ParseParams

# from icecream.utils.parse_params import ParseParams


logger = logging.getLogger(__name__)


def _replace_ice_request_data(ic, data):
    return ic.get_variables().deal_variables(data)


class Parameterization:

    @classmethod
    def check_params_valid(cls, params):
        """
        检查参数化数据，是否有效
        :param params:
        :return:
        """
        if params:
            for iter_data in params.split("\n"):
                if len(iter_data) > 0 and not iter_data.startswith("#"):
                    if iter_data.find("ice_params_") >= 0:
                        return True
        return False

    @classmethod
    def run_params(cls, params, ic):
        """
        参数化
        :param params:
        :param ic: icecream 实例对象
        :return:
        """
        scope = {"ice": ic}
        exec(params, scope)
        ice_params_product = scope.get("ice_params_product", None)  # 全量正交
        ice_params_pairwise = scope.get("ice_params_pairwise", None)  # pariwise
        ice_params_seq = scope.get("ice_params_seq", None)  # 按数组顺序序列化
        ice_params_all_seq = scope.get("ice_params_all_seq", None)  # 按数组顺序序列化,全列
        ice_params_file = scope.get("ice_params_file", None)  # 文件数据化
        if ice_params_product:
            return cls._get_product_params(ice_params_product)
        if ice_params_pairwise:
            return cls._get_pariwise_params(ice_params_pairwise)
        if ice_params_seq:
            return cls._get_seq_params(ice_params_seq)
        if ice_params_file:
            return cls._get_file_params(ice_params_file)
        if ice_params_all_seq:
            return cls._get_all_seq_params(ice_params_all_seq)
        return []

    @classmethod
    def _split_array(cls, params: dict) -> Tuple[List, List]:
        keys = []
        values = []
        for key, value in params.items():
            values.append(value)
            keys.append(key)
        return keys, values

    @classmethod
    def _get_product_params(cls, params) -> Generator[Dict, None, None]:
        """获取正交全量数据
        :param params:
        :return:

        Examples:
             >>> arg1 = {"a": [1,2], "b": [4,5]}
            Generator[
                {'a': 1, 'b': 4},
                {'a': 1, 'b': 5},
                {'a': 2, 'b': 4},
                {'a': 2, 'b': 5}
            ]
        """
        keys, values = cls._split_array(params)
        for iter_data in itertools.product(*values):
            yield dict(zip(keys, iter_data))

    @classmethod
    def _get_pariwise_params(cls, params) -> Generator[Dict, None, None]:
        """

        :param params:
        :return:
        """
        factor = params.pop("pariwise_factor", 2) or 2
        keys, values = cls._split_array(params)
        pariwise = PariwiseUtil().pairwise(values, factor)
        for iter_data in pariwise:
            yield dict(zip(keys, iter_data))

    @classmethod
    def _get_seq_params(cls, params) -> Generator[Dict, None, None]:
        """获取全序列数据

        :param params:
        :return:

         Examples:
             >>> arg1 = {"a": [1, 2], "b": [4, 5, 6]}
            Generator[
                {'a': 1, 'b': 4},
                {'a': 1, 'b': 5},
                {'a': 2, 'b': 4},
                {'a': 2, 'b': 5}
            ]
        """
        keys, values = cls._split_array(params)
        for iter_data in zip(*values):
            yield dict(zip(keys, iter_data))

    @classmethod
    def _get_all_seq_params(cls, params) -> Generator[Dict, None, None]:
        """获取全序列数据

        :param params:
        :return:

         Examples:
             >>> arg1 = {"a": [1,2], "b": [4,5]}
            Generator[
                {'a': 1, 'b': 4},
                {'a': 1, 'b': 5},
                {'a': 2, 'b': 4},
                {'a': 2, 'b': 5}
            ]
        """
        fillvalue = params.pop("@fillvalue", None)
        keys, values = cls._split_array(params)
        for iter_data in itertools.zip_longest(*values, fillvalue=fillvalue):
            yield dict(zip(keys, iter_data))

    @classmethod
    def _get_file_params(cls, ice_params_file) -> Generator[Dict, None, None]:
        """文件模式的数据参数化

        :param ice_params_file: [a,b,c,d] [1,2,3,4]
        :return:
        """
        for item_data in ice_params_file:
            yield dict(zip(item_data['title'], item_data['data']))


class Variables(object):
    """
    动态记录执行过程中的变量信息，同时初始过程加载环境变量信息
    环境变量：
    """

    def __init__(self):
        self.variables_collect = {}
        self.globals_collect = {}
        self.environments_collect = {}

    def deal_variables(self, data):
        """处理 globals, varibles, environment"""
        if not data:
            return
        collect_variables = {**self.globals_collect, **self.environments_collect, **self.variables_collect}
        return ParseParams.parse_data(data, collect_variables)

    def load_variables(self, env_config):
        if env_config.global_data:
            self.globals_collect.update(env_config.global_data)
        if env_config.env_data:
            decode_passwd(env_config.env_data)
            self.environments_collect.update(env_config.env_data)

    def replace_passwd(self, msg: str):
        """
        加密敏感信息，只能保证日志的输出加密
        :param msg:
        :return:
        """
        tmp_value = [value for key, value in self.variables_collect.items() if key.startswith("@icepwd_")]
        global_value = [value for key, value in self.globals_collect.items() if key.startswith("@icepwd_")]
        env_value = [value for key, value in self.environments_collect.items() if key.startswith("@icepwd_")]
        for iter_data in itertools.chain(tmp_value, global_value, env_value):
            if iter_data in msg:
                msg = msg.replace(iter_data, "xxxxxxxxxxxxxxxxxxxxx")
        return msg


def run_pre_test(item, ice):
    """
    执行前置测试代码
    :param item:
    :param ice:
    :return:
    """
    prerequest = item.prerequest
    if not prerequest:
        return
    scope = {"ice": ice}
    try:
        if prerequest.get("script"):
            exec(prerequest.get("script"), scope)
    except Exception:
        error_msg = traceback.format_exc()
        logger.error(error_msg)
        item.result = "error"
        item.result_detail = [{'result': "error", "msg": "系统异常", "error": str(error_msg)}]


def _deal_header_str(header: dict) -> dict:
    """header中的值只能是str, bytes"""
    if header:
        for key, value in header.items():
            if not isinstance(value, (str, bytes)):
                header[key] = str(value)
    return header


def parameter_handling(http_result, ice, req_data, item):
    req_data = copy.deepcopy(req_data)
    body_mode = req_data.body.get('mode') if req_data.body else None
    data = None
    files = []
    form_data_file = []
    try:
        req_data.header = {} if not _replace_ice_request_data(ice, req_data.header) else _replace_ice_request_data(ice,
                                                                                                                   req_data.header)
        req_data.header = _deal_header_str(req_data.header)
        need_encoding = {"flag": False, "charset": "utf-8", "data": None}
        if body_mode == "raw":
            option = Utils.ignore_case_get(req_data.body, "option")
            if option == "json":
                content_type = Utils.ignore_case_get(req_data.header, "content-type")
                if content_type is None:
                    req_data.header.update({"Content-Type": "application/json"})
                data = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "raw"))
                try:
                    data = json.loads(data)
                except Exception as e:
                    logger.warning("body params error" + str(e))
            elif option in ["xml", "text", "html"]:
                data = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "raw"))
                need_encoding = {
                    "flag": True,
                    "charset": "utf-8",
                    "data": data
                }
            else:
                data = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "raw"))
        elif body_mode == "form-data":
            excute_data = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "data"))
            data = {}
            if excute_data:
                for iter_data in excute_data:
                    for key, value in iter_data.items():
                        if isinstance(value, dict):
                            if value.get("ContentType", "Auto") in ["Auto", "text/plain"]:
                                data[key] = value["value"]
                            if value.get("ContentType") == "application/json":
                                form_data_file.append(
                                    (key, ("", json.dumps(json.loads(value["value"])), "application/json")))
                            # todo 其他类型文件未做处理
                        if isinstance(value, list):  # [{"value": 123}, {"value": 456}]
                            for k in value:
                                if k.get("ContentType", "Auto") in ["Auto", "text/plain"]:
                                    if key not in data:
                                        data[key] = k["value"]
                                    else:
                                        if isinstance(data[key], str):
                                            data[key] = [data[key]]
                                        data[key].append(k["value"])
                                if k.get("ContentType") == "application/json":
                                    form_data_file.append(
                                        (key, ("", json.dumps(json.loads(k["value"])), "application/json")))
            file_paths = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "file"))
            if file_paths:
                for iter_data in file_paths:
                    for key, value in iter_data.items():
                        if isinstance(value, dict):
                            if value.get("ContentType", "Auto") == "Auto":
                                files.append(value['value'])
                                form_data_file.append((key, FileUtils.deal_form_file(value['value'])))
                            else:
                                files.append(value['value'])
                                form_file = file_type_hand(value)
                                form_data_file.append((key, form_file))
                        if isinstance(value, list):
                            for k in value:
                                if k.get("ContentType", "Auto") == "Auto":
                                    files.append(k['value'])
                                    form_data_file.append((key, FileUtils.deal_form_file(k['value'])))
                                else:
                                    files.append(k['value'])
                                    form_file = file_type_hand(k)
                                    form_data_file.append((key, form_file))
            if form_data_file:
                Utils.remove_dict_key(req_data.header, "content-type")
            else:
                content_type = Utils.ignore_case_get(req_data.header, "content-type", "").lower()
                if data and "multipart/form-data" in content_type:
                    for key, value in data.items():
                        data[key] = str(value)
                    multipart_data = MultipartEncoder(fields=data)
                    data = multipart_data
                    req_data.header['Content-Type'] = multipart_data.content_type
        elif body_mode == "x-www-form-urllencoded":
            data = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "data"))
        elif body_mode == "file":
            file_path = _replace_ice_request_data(ice, Utils.ignore_case_get(req_data.body, "file"))
            if not os.path.exists(file_path):
                raise RuntimeError(f'{file_path} path not exists')
            else:
                files.append(file_path)
        ice_url = _replace_ice_request_data(ice, req_data.url)
        ice_params = _replace_ice_request_data(ice, req_data.params)
        if http_result:
            http_result.request = _replace_password(ice, {
                "headers": req_data.header,
                "content": {
                    "url": ice_url,
                    "params": ice_params,
                    "data": Utils.encoder_to_dict(data) if isinstance(data, MultipartEncoder) else data,
                    "file": files
                }
            })
        return {
            "url": ice_url,
            "params": ice_params,
            "data": data,
            "files": files,
            "header": req_data.header,
            "need_encoding": need_encoding,
            "form_data_file": form_data_file
        }
    except Exception:
        error_msg = traceback.format_exc()
        logger.error(error_msg)
        item.result = "error"
        item.result_detail = [{'result': "error", "msg": "请求数据处理异常", "error": str(error_msg)}]


def _replace_password(ice, data: dict) -> dict:
    """
    替换用户敏感信息
    :param data:
    :return:
    """
    return json.loads(ice.get_variables().replace_passwd(json.dumps(data, ensure_ascii=False)))


def file_type_hand(value):
    """
    将文件扩展名对应的ContentType替换成用户上传的ContentType
    """
    new_files = list(FileUtils.deal_form_file(value['value']))
    new_files[2] = value.get("ContentType")
    form_file = tuple(new_files)
    return form_file
