"""
@author:cmcc
@file: base_request.py
@time: 2024/7/22 15:51
"""
import json
import traceback
import logging
from icecream.core.mode.data.constant import RequestProtocol
from icecream.core.mode.test_suite import TestItem
from icecream.core.protocol.request.base_request import BaseRequest
from icecream.core.protocol.request.http_request import HttpRequest
from icecream.core.protocol.request.websocket_request import WebSocketRequest
from icecream.core.runner import IceRunner
from icecream.core.assist import run_pre_test, parameter_handling
from icecream.core.test_result import CollectRequestProcess
from icecream.utils.make_cmri_schema import CMRISchemaMaker
from icecream.utils.make_json_schema import JsonSchemaMaker

logger = logging.getLogger(__name__)


class RequestFactory:

    def __init__(self, item: TestItem, runner: IceRunner):
        self.item = item
        self.base_request: BaseRequest | None = None
        self.records = runner.record
        self.ic = runner.ic
        self.runner = runner
        self.parameter = None
        self._create_request()
        self.test_result = CollectRequestProcess()
        self.tmp_var = None  # 请求进来时产生的临时变量

    def _create_request(self):
        if self.item.supper_agreement == RequestProtocol.HTTP:
            #todo 这里传递的是self.item.request 是item的content?

            # self.base_request = HttpRequest(self.ic, self.item.request, self.item.setting)
            self.base_request = HttpRequest(self.ic, self.item.req_data, self.item.setting)

        elif self.item.supper_agreement == RequestProtocol.WEB_SOCKET:
            self.base_request = WebSocketRequest(self.ic, self.item.req_data, self.item.setting)

        else:
            raise ValueError("不支持的请求类型")


    def make_cmri_schema(self, record_id, specific_data):
        """
        生成cmri_schema
        :param record_id:
        :return:
        """
        record = self.records.get(record_id)
        if record:
            try:
                if record.get(specific_data):
                    return CMRISchemaMaker(record.get(specific_data)).get_cmri_schema_body()
            except Exception:
                logger.warning(traceback.format_exc())

    def make_json_schema(self, record_id):
        """
        生成json_schema
        :param record_id:
        :return:
        """
        record = self.records.get(record_id)
        if record:
            try:
                if record.get("response_data"):
                    return JsonSchemaMaker(record.get("response_data")).get_json_schema()
            except Exception:
                logger.warning(traceback.format_exc())

    def beforce_test(self):
        self.tmp_var = set(self.ic.variables.get_all())
        run_pre_test(self.item, self.ic)
        self.parameter = parameter_handling(self.test_result, self.ic, self.item.req_data, self.item)
        self.ic.request_content.update({"params": self.test_result.request.get("content", {}).get("params"),
                                        "body": self.test_result.request.get("content", {}).get("data"),
                                        "url": self.test_result.request.get("content", {}).get("url"),
                                        "header": self.test_result.request.get("headers", {})}
                                       )

    def parameter_validation(self):
        """
        请求参数cmri_schema校验
        """
        error_msg = ""
        assert_result = {}
        try:
            data = self.parameter
            if self.item.from_to and self.item.from_to != "0":
                body_cmri_schema = self.make_cmri_schema(self.item.from_to, specific_data="body_data")
                query_cmri_schema = self.make_cmri_schema(self.item.from_to, specific_data="query_params")
                if body_cmri_schema and query_cmri_schema:
                    self.ic.test.cmri_schema(data.get("data"), body_cmri_schema, "请求body参数检查")
                    self.ic.test.cmri_schema(data.get("params"), query_cmri_schema, "query参数检查")
                elif body_cmri_schema or query_cmri_schema:
                    if body_cmri_schema:
                        self.ic.test.cmri_schema(data.get("data"), body_cmri_schema, "请求body参数检查")
                    if query_cmri_schema:
                        self.ic.test.cmri_schema(data.get("params"), query_cmri_schema, "query参数检查")
                else:
                    logger.warning(f"{self.item.from_to} cmri format transfer failure")
                    error_msg = "cmri format transfer failure"
            if error_msg == "":
                assert_result = self.ic.test.commit()
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.warning(error_msg)
        finally:
            self.item.result = assert_result.get('result')
            self.item.result_detail = assert_result.get("detail")
            if error_msg != "":
                self.item.result = "error"
                self.item.result_detail = [{'result': "error", "msg": "系统异常", "error": str(error_msg)}]


    def test(self):
        if self.base_request:
            try:
                self.base_request.send(self.parameter, self.test_result, proxies=self.runner.proxies)
            except Exception as e:
                error_msg = traceback.format_exc()
                logger.warning(error_msg)
                self.item.result = "error"
                self.item.result_detail = [{'result': "error", "msg": "系统异常", "error": str(error_msg)}]
        self.item.test_content = self.test_result.to_json()

    def after_test(self):
        """运行assert相关断言"""
        if not self.item.test:
            return
        error_msg = ""
        scope = {"ice": self.ic}
        assert_result = {}
        try:
            test = [item for item in list(set(map(lambda x: x.get("script"), self.item.test))) if item is not None]
            if test:
                exec_cmd = "\n".join(test)
                if self.item.from_to and self.item.from_to != "0":
                    if "{{cmri_schema}}" in exec_cmd:
                        cmri_schema = self.make_cmri_schema(self.item.from_to, specific_data="response_data")
                        if not cmri_schema:
                            logger.warning(f"{self.item.from_to} cmri format transfer failure")
                            error_msg = "cmri format transfer failure"
                        else:
                            exec_cmd = exec_cmd.replace("{{cmri_schema}}",
                                                        json.dumps(cmri_schema, ensure_ascii=False))

                    if "{{json_schema}}" in exec_cmd:
                        # 增加对 json_schema 的判断
                        json_schema = self.make_json_schema(self.item.from_to)
                        if not json_schema:
                            logger.warning(f"{self.item.from_to} json schema transfer failure")
                            error_msg = "json schema transfer failure"
                        else:
                            exec_cmd = exec_cmd.replace("{{json_schema}}",
                                                        json.dumps(json_schema, ensure_ascii=False))

                if error_msg == "":
                    exec(exec_cmd, scope)
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.warning(error_msg)
        finally:
            try:
                assert_result = self.ic.test.commit()
            except AssertionError as e:
                pass
            self.item.result = assert_result.get('result')
            self.item.result_detail = assert_result.get("detail")
            if error_msg != "":
                self.item.result = "error"
                self.item.result_detail.append({'result': "error", "msg": "系统异常", "error": str(error_msg)})

    def clear_test(self):
        """
        单个请求执行完成后调用，用于处理测试产生的临时数据
        :return:
        """
        if self.tmp_var is None:
            return
        diff_var = set(self.ic.variables.get_all()) - self.tmp_var
        if diff_var is not None:
            self.ic.variables.clear(list(diff_var))