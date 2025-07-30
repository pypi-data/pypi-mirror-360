"""
@author:cmcc
@file: http_request.py
@time: 2024/7/22 1:02
"""
import copy
import json
import logging
import os
from random import random
from icecream.core.mode.data.request_data import HttpReqData
from icecream.core.assist import parameter_handling
from icecream.core.protocol.request.base_request import BaseRequest
from icecream.utils.common import Utils, FileUtils

logger = logging.getLogger(__name__)


def calc_simple_params(raw_data, key, result, flag="remove"):
    """
    去掉key or key+uuid, 保证参数的序列，逐渐剔除
    :param key:
    :param raw_data:
    :param result:
    :param flag: remove, error
    :return:
    """

    params = raw_data.get(key)
    for item_key in params.keys():
        tmp_raw = copy.deepcopy(raw_data)
        tmp_params = copy.deepcopy(params)
        if flag == "remove":
            tmp_params.pop(item_key)
            tmp_raw[key] = tmp_params
        else:
            tmp_params[f'{item_key}_{random.randint(1, 20)}'] = tmp_params.pop(item_key)
            tmp_raw[key] = tmp_params
        result.append(tmp_raw)


class HttpRequest(BaseRequest):
    """
    example
{
	"method": "GET",
	"header": {
		"content-type": "application/json"
	},
	"url": None,
	"body": {
		"mode": "raw"
		"option": "xml"
		"raw": "6666"#
		"mode": "file"
		"file": c: /test.txt#
		"mode": "form-data"
		"data": "key": "value"
		"file": "file1": c: /test.txt
		"file2": c: /test2.text
	}
}
    """

    # todo  dict变成bean
    def __init__(self, ice, req_data: HttpReqData, setting: dict):
        self.ice = ice

        # self.method = content.get("method")
        # self.header = content.get("header") or {}
        # self.url = content.get("url")
        # self.params = content.get("query")
        # self.parameters = content.get("params")
        # self.body = content.get("body")

        self.req_data = req_data

        self.body_mode = None
        self.body_option = None
        self.setting = setting
        self.http_timeout = setting.get("http_timeout") if setting else 90
        if req_data.body:
            self.body_mode = req_data.body.get('mode')
            # req_data.body.pop('mode')
        self.stream = setting.get("stream", "true").lower() == "true" if setting else None
        self.proxies = setting.get("proxies") if setting else None
        self.concurrency = setting.get("concurrency") if setting else None

    def to_json(self):
        return {'url': self.req_data.url, 'method': self.req_data.method, 'header': self.req_data.header,
                'params': self.req_data.params, 'body': self.req_data.body, 'parameters': self.req_data.parameters}

    def is_emtpy(self):
        if self.req_data.url is None or len(self.req_data.url) == 0:
            return True
        return False

    @staticmethod
    def _xray_params(format_data) -> list:
        """
        处理参数，key 有，无，错
        临时方案需要优化
        :param format_data:
        :return:
        """
        result = []
        params = format_data.get("params")
        if params:
            calc_simple_params(format_data, "params", result, "remove")
            calc_simple_params(format_data, "params", result, "error")
        data = format_data.get("data")
        if data:
            if isinstance(data, list):
                result.append(data)
            elif isinstance(data, dict):
                calc_simple_params(format_data, "params", result, "remove")
                calc_simple_params(format_data, "params", result, "error")
        return result

    def send(self, data, http_result, proxies=None, xray_method=None):
        Utils.remove_useless_data(data, ["@ice_none"])
        if xray_method is None:
            # self._send(proxies, data)
            return self._send(proxies=proxies, deal_data=data, http_result=http_result)
        if xray_method == "simple":
            for tmp_data in self._xray_params(data):
                Utils.remove_useless_data(tmp_data, ["@ice_none"])
                # self._send(proxies, tmp_data)  # 同步
                return self._send(proxies=proxies, deal_data=tmp_data, http_result=http_result)  # 同步
        if xray_method == "high":
            # todo 高级模式
            pass

    def _send(self, deal_data, http_result, proxies=None):
        data = deal_data.get("data")
        need_encoding = deal_data.get("need_encoding")
        header = deal_data.get("header")
        ice_url = deal_data.get("url")
        params = deal_data.get("params")
        files = deal_data.get("files")
        form_data_file = deal_data.get("form_data_file")
        proxies = proxies or self.proxies
        if self.body_mode == "file":
            return self.ice.http_request.send(ice_url, self.req_data.method, params, FileUtils.chunk_read(files[0]),
                                              header, stream=True, http_result=http_result,
                                              proxies=proxies, timeout=self.http_timeout)
        if need_encoding.get("flag"):
            data = need_encoding.get("data").encode(need_encoding.get("charset"))
        if self.body_mode == "form-data":
            return self.ice.http_request.send(ice_url, self.req_data.method, params, data, header,
                                              files=form_data_file if form_data_file else None,
                                              http_result=http_result,
                                              proxies=proxies, timeout=self.http_timeout,
                                              stream=self.stream)
        return self.ice.http_request.send(ice_url, self.req_data.method, params, data, header,
                                          files=form_data_file if form_data_file else None,
                                          http_result=http_result,
                                          proxies=proxies, timeout=self.http_timeout,
                                          stream=self.stream)
