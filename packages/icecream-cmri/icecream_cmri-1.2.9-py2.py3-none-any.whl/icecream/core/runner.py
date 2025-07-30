import os
import json
import logging
import traceback
import argparse
from icecream.core.driver import IceCream
from icecream.core.mode.test_suite import TestCollect, TestItem
from icecream.core.assist import run_pre_test
from icecream.core.test_result import TestResult
from icecream.utils.common import Utils
from icecream.utils.safe_check_util import safe_output
from icecream.ext.ext_manage import ExtManage
from icecream.core.assist import Parameterization

logger = logging.getLogger(__name__)

'''

icerunner-icecream-exec_test_item-request_factory before test after-http_request send -http send



'''


class IceRunner:
    """用于remote执行测试用例"""

    def __init__(self):
        self.ic = IceCream()
        self.test_collects = []
        self.record = {}  # 原始api定义， {idxxx: {}}
        self.test_result = TestResult()  # 聚合测试结果
        self.call_backs = []  # 回调接口
        self.flag_update_env = True
        self.flag_stop = False
        self.workdir = None
        self.proxies = None
        self.ext_manage = ExtManage(self)

    def regist_callback(self, call_back):
        """注册结果回调"""
        self.call_backs.append(call_back)

    def unregist_callback(self, call_back):
        if call_back in self.call_backs:
            self.call_backs.remove(call_back)

    def call_back_result(self, result):
        """回调结果"""
        if self.call_backs:
            for call_back in self.call_backs:
                if result:
                    result["console_log"] = safe_output(self.ic.collect_info, self.ic.environment)
                call_back(result)
            self.ic.collect_info.clear()

    def _load_file_reocrd(self, file_path):
        """
        加载文件record
        :param file_path:
        :return:
        """
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                records = json.loads(f.read())
                if records:
                    self.record = {record.get("id"): record for record in records}
            except Exception as e:
                logger.warning(traceback.format_exc())

    def load_test_case(self, file_path):
        """
        载入测试用例
        :param file_path:
        :return:
        """
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                for filename in os.listdir(file_path):
                    if filename.endswith("yaml"):
                        self._parser_test_file(os.path.join(file_path, filename))
            elif os.path.isfile(file_path):
                self._parser_test_file(file_path)
        else:
            logger.error("yaml case file not exists")

    def load_test_dir(self, file_dir):
        """
        载入文件目录
        :param file_dir:
        :return:
        """
        self.ic.globals.set("ICE_WORKSPACE_DIR", file_dir)
        self.ic.globals.set("WORKSPACE_DIR", file_dir)
        self.workdir = file_dir
        for file_path in os.listdir(file_dir):
            if file_path.endswith("env.yaml"):
                self.ic.load_env_config(os.path.join(file_dir, file_path))
                continue
            if file_path.endswith("test_record.yaml"):
                self.load_test_case(os.path.join(file_dir, file_path))
                continue
            if file_path.endswith("record.json"):
                self._load_file_reocrd(os.path.join(file_dir, file_path))
                continue
            if file_path.endswith("function.py"):
                self.ic.load_file_function(os.path.join(file_dir, file_path))

    def _flatten_data(self, data_list):
        result = []
        for item in data_list:
            new_item = item.copy()
            new_item.pop('items', None)
            result.append(new_item)
            if 'items' in item:
                result.extend(self._flatten_data(item['items']))
        return result

    def _parser_test_file(self, file_path):
        content = Utils.load_yaml(file_path)
        self.test_collects.append(TestCollect(content))
        self.ic.all_items = {item['id']: TestItem(item.copy()) for item in
                             self._flatten_data(content.get("test_collect", {}).get("items"))}

    def clear_self_variables(self, data: dict):
        """
        清理自身产生的变量, 未采用，后期优化，谁生产，谁销毁
        :param data:
        :return:
        """
        for key, value in data.items():
            self.ic.variables.clear(key)

    def clear_all_variables(self):
        """
           清理自上下文变量，保护变量安全
           :param data:
           :return:
        """
        self.ic.variables.clear_all()

    def run(self):
        """运行测试集合, 总入口"""
        self.ext_manage.start_ext_plugin()
        if self.ext_manage.proxies:
            self.proxies = self.ext_manage.proxies
        for test_collect in self.test_collects:
            self.test_result.set_current_collect(test_collect.id, test_collect.name)
            for item in test_collect.items:
                if self.flag_stop:
                    return
                self.run_test_suites(item)
        self.call_backs.clear()
        self.ext_manage.stop_ext_plugin()

    def run_test_suites(self, item: TestItem):
        """运行所有item， 包含所有相关数据
        """
        self.test_result.set_test_case_start(item)
        if item.type.lower() == "folder":  # 普通文件夹
            self.run_common_folder(item)
        elif item.type.lower() == "case_folder":  # 用例文件夹
            self.run_case_folder(item)
        elif item.type.lower() == "param_folder":  # 参数化文件夹
            self.run_param_folder(item)
        elif item.type.lower() in ("case", "common"):  # 具体的case
            self.run_test_step_case(item)
        self.test_result.set_test_case_stop(item)

    def run_param_folder(self, item: TestItem):
        """
        参数化文件夹，可以用来统一参数化
        :param item:
        :return:
        """
        if self.flag_stop:
            return
        logger.debug(f"<item: param_folder> {item.name} exce_id {item.id}: start exec")
        params = item.parameters
        if Parameterization.check_params_valid(params):  # 参数化方案
            for iter_data in Parameterization.run_params(params, self.ic):
                if self.flag_stop:
                    break
                for key, value in iter_data.items():
                    self.ic.variables.set(key, value)
                self.run_prerequest(item)
                for iter_item in item.items:
                    if self.flag_stop:
                        break
                    self.run_test_suites(iter_item)
                self.clear_self_variables(iter_data)
        else:
            for iter_item in item.items:
                self.run_test_suites(iter_item)
        logger.debug(
            f"<item: param_folder> {item.name} exce_id {item.id}: exec completed! is_force_stop={self.flag_stop}")

    def run_common_folder(self, item: TestItem):
        """
        普通的测试文件夹
        :param item:
        :return:
        """
        if self.flag_stop:
            return
        logger.info(f"<item: common_folder> {item.name} exce_id {item.id}: start exec")
        self.clear_all_variables()
        for iter_item in item.items:
            self.run_test_suites(iter_item)
        self.clear_all_variables()
        logger.info(
            f"<item: common_folder> {item.name} exce_id {item.id}: exec completed! is_force_stop={self.flag_stop}")

    def run_case_folder(self, item: TestItem):
        """
        用例文件夹，可以加载测试数据及文件等
        :param item:
        :return:
        """
        if self.flag_stop:
            return
        logger.info(f"<item: case_folder> {item.name} exce_id {item.id}: start exec")
        params = item.parameters
        result = "pass"
        if Parameterization.check_params_valid(params):  # 参数化方案
            try:
                i = 1
                flag = False
                for iter_data in Parameterization.run_params(params, self.ic):
                    if self.flag_stop:
                        break
                    flag = True
                    for key, value in iter_data.items():
                        self.ic.variables.set(key, value)
                    self.run_prerequest(item)
                    for common_case in item.items:
                        common_case.inner_iter_num = i
                        temp_result = self.run_test_step_case(common_case)
                        if temp_result != "pass":
                            result = temp_result
                    item.result = result
                    item.inner_iter_num = i
                    self.call_back_result(item.to_result_item())
                    self.clear_self_variables(iter_data)
                    i = i + 1
                if flag:
                    return
            except Exception:
                self.flag_update_env = False
                error_msg = traceback.format_exc()
                logger.error(error_msg)
                item.result = "error"
                item.result_detail = [{'result': "error", "msg": "系统异常", "error": error_msg}]
                self.call_back_result(item.to_result_item())
                return
        for common_case in item.items:
            tmp_result = self.run_test_step_case(common_case)
            if tmp_result != "pass":
                result = tmp_result
        item.result = result
        self.call_back_result(item.to_result_item())
        logger.info(f"<item: case_folder> {item.name} exce_id {item.id}: exec completed")

    def run_test_step_case(self, item: TestItem):
        """
        执行case文件夹下具体step case
        :param item:
        :return:
        """
        if self.flag_stop:
            return
        logger.info(f"<item: case_step> {item.name} exce_id {item.id}: start exec")
        params = item.parameters
        result = "pass"
        if Parameterization.check_params_valid(params):  # 参数化方案
            try:
                for iter_data in Parameterization.run_params(params, self.ic):
                    if self.flag_stop:
                        break
                    for key, value in iter_data.items():
                        self.ic.variables.set(key, value)
                    self.exec_test_item(item)
                    if item.result != "pass":
                        result = "failure"
                    self.clear_self_variables(iter_data)
            except Exception:
                self.flag_update_env = False
                error_msg = traceback.format_exc()
                logger.error(error_msg)
                item.result = "error"
                result = "error"
                item.result_detail = [{'result': "error", "msg": "系统异常", "error": error_msg}]
                self.call_back_result(item.to_result_item())
        else:  # 非参数化方案
            self.exec_test_item(item)
            if item.result != "pass":
                result = "failure"
        # wupeng add start xray...
        self.ext_manage.xray_auto_attack(item)
        logger.info(f"<item: case_step> {item.name} exce_id {item.id}: exec completed")
        return result

    # 回调call_back_result都是在这里
    def exec_test_item(self, item: TestItem):
        """
        执行具体的测试项,使用参数化
        :param item:
        :return:
        """
        self.ic.put_exec_caseid(item.id)
        from icecream.core.protocol.request.factory_request import RequestFactory  # 解决循环引用
        logger.debug(f"<item: test_instance> {item.name} exce_id {item.id}: start exec")
        item.exec_id = Utils.get_uuid()
        request_factory = RequestFactory(item, self)
        request_factory.beforce_test()
        if item.result == "error":
            self.call_back_result(item.to_result_item())
            if self.ic.env_config.error_stop_flag.lower() == "on":
                self.flag_stop = True
            return
        if item.setting and item.setting.get("parameter_validation", 0) == 1:
            request_factory.parameter_validation()
            if item.result != "pass":
                self.call_back_result(item.to_result_item())
                return
        request_factory.test()
        if item.test and item.result == "error":
            self.call_back_result(item.to_result_item())
            if self.ic.env_config.error_stop_flag.lower() == "on":
                self.flag_stop = True
        request_factory.after_test()
        self.call_back_result(item.to_result_item())
        request_factory.clear_test()
        logger.debug(f"<item: test_instance> {item.name} exce_id {item.id}: exec completed")

    def run_prerequest(self, item: TestItem):
        run_pre_test(item, self.ic)
