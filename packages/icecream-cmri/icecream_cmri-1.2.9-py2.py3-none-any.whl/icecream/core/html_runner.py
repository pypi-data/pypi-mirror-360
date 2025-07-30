import argparse
import ast
import json
import os
import shutil
import uuid
from collections import Counter
from datetime import datetime
import pandas as pd
from icecream.utils.common import Utils
import yaml
from icecream.core.runner import IceRunner


def format_reponse(reponse):
    """格式化响应数据"""
    if reponse:
        return {
            "status_code": reponse.get("status_code"),
            "response_header": reponse.get("headers"),
            "response_content": reponse.get("text"),
            "size": reponse.get("size"),
            "time_line": reponse.get("resp_time")
        }


def get_json_data(json_data, key):
    if json_data:
        return json_data.get(key)


def _get_iter_test_set_id(test_sets):
    """
    # 将测试集所有数据展开
    :param test_sets:
    :return:
    """
    result = []
    for test_set in test_sets:
        if "items" in test_set:
            children = test_set.pop("items")
            result.append(test_set)
            result = result + _get_iter_test_set_id(children)
        else:
            result.append(test_set)
    return result


def get_parent_name(test_sets, test_case, result=None):
    """
    case用例全路径： xx-xx-xx-xxx
    :param test_sets:  所有测试用例
    :param test_case:  子节点用例
    :param result:
    :return:
    """
    if result is None:
        result = []
    result.append(test_case["name"])
    for test_set in test_sets:
        if test_set["category"] == "0":  # 顶级目录
            result.append(test_set['name'])
            break
        if test_case["parent_id"] == test_set['id']:
            if test_set["category"] == 2:
                result.clear()
                break
            get_parent_name(test_sets, test_set, result)


def merge_list(sources, targets, conditions: list, greedy_flag=False,
               reverse=False, source_filter=None, target_filter=None):
    """
    按条件合并列表source to target
    condition => 用作条件映射，
    如：merge_list([{task_id:1, test: 5}], [{id:1, large: 7}], ["task_id=>id"]) => [id:1, large:7 test5]
    如：merge_list([{id:1, test: 5}], [{id:1, large: 7}], ["id"]) => [id:1, large:7 test5]
    :param sources:
    :param targets:
    :param conditions:
    :param greedy_flag: 是否贪婪匹配，所用项都去适配
    :param reverse: target to source
    :param source_filter: 去掉原数组数据
    :param target_filter: 去掉目标数组数据
    :return:
    """
    source_filter = source_filter or []
    target_filter = target_filter or []

    def deal_filter(filter_data: list, target_data: dict):
        for key in filter_data:
            if key in target_data:
                target_data.pop(key, None)

    def is_condition(source_data, target_data):
        results = []
        for condition in conditions:
            if "=>" in condition:
                condition2 = condition.split("=>")
                results.append(source_data.get(condition2[0]) == target_data.get(condition2[1]))
            else:
                results.append(source_data.get(condition) == target_data.get(condition))
        flag = False if len(results) == 0 else all(results)
        if flag:
            deal_filter(source_filter, source_data)
            deal_filter(target_filter, target_data)
        return flag

    if sources and targets:
        for source in sources:
            for target in targets:
                if is_condition(source, target):
                    if reverse:
                        source.update(target)
                    else:
                        target.update(source)
                    if not greedy_flag:
                        break
    return sources if reverse else targets


def get_case_flat(test_sets):
    """
    case 路径： [{"path": xx-xx-xx-xx, "case_id":xx, "category": xx, base_num": 2}]
    :param test_sets:
    :return:
    """
    result = []
    case_folder_ids = []
    for test_set in test_sets:
        if test_set["category"] == 2:  # 用例文件夹
            case_folder_ids.append(test_set["id"])
            path_collect = []
            get_parent_name(test_sets, test_set, path_collect)
            if path_collect:
                path_collect.reverse()
                result.append({"case_id": test_set["id"],
                               "path": "->".join(path_collect),
                               "category": test_set["category"],
                               "base_num": 1
                               })
            continue
        if test_set["parent_id"] in case_folder_ids:
            case_folder_ids.append(test_set["parent_id"])
            continue
        if test_set["category"] in [3]:  # 用例
            path_collect = []
            get_parent_name(test_sets, test_set, path_collect)
            if path_collect:
                path_collect.reverse()
                result.append({"case_id": test_set["id"],
                               "path": "->".join(path_collect),
                               "category": test_set["category"],
                               "base_num": 1
                               })
    test_set_nums = []
    if case_folder_ids:
        res = Counter(case_folder_ids)
        for k, v in res.items():
            test_set_nums.append({"parent_id": k, "base_num": v - 1})
    merge_list(result, test_set_nums, ["case_id=>parent_id"], reverse=True, target_filter=["parent_id"])
    return result


class Html_Runner:

    def __init__(self, plan_path:str, report_dir:str=None, env_name:str=None):
        self.status_values = ['pass', 'failure', 'error', 'unknown']
        self.plan_path = plan_path
        self.plan_name = os.path.basename(plan_path)
        self.data_list = []
        self.runner = None
        self.df = None
        if report_dir is None:
            self.report_path = os.path.join(os.getcwd(), "report", datetime.now().strftime('%Y%m%d%H%M%S'), self.plan_name)
        else:
            self.report_path = os.path.join(report_dir, self.plan_name)
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)
        self.template_dir = os.path.dirname(os.path.dirname(__file__))
        self.modify_env_name(env_name)

    def modify_env_name(self, env_name):
        """激活环境变量"""
        if env_name is None:
            return
        env_file = os.path.join(self.plan_path, "env.yaml")
        if not os.path.exists(env_file):
            return
        data = Utils.load_yaml(env_file)
        data['ENV_CONFIG']['ACTIVE'] = env_name
        for environment in data['ENV_CONFIG']["ENVIRONMENTS"]:
            environment['ICE_WORKSPACE_DIR'] = self.report_path
        Utils.write_yaml(env_file, data)

    def run(self):
        self.runner = IceRunner()
        self.runner.regist_callback(self.call_back_verify)
        if self.plan_name:
            self.runner.load_test_dir(self.plan_path)
            self.runner.run()
            self.runner.unregist_callback(self.call_back_verify)
            self.df = pd.DataFrame(self.data_list)
            shutil.copytree(os.path.join(self.template_dir, 'resource', 'template'),
                            self.report_path, dirs_exist_ok=True)
            file_path = os.path.join(self.report_path, f"{self.plan_name}.xlsx")
            self.df.to_excel(file_path, index=False)
            self.df = pd.read_excel(file_path)

    def call_back_verify(self, result):
        """
        回调函数
        """
        test_content = result.get("test_content")
        result = {
            "id": str(uuid.uuid1()),
            "exec_id": result.get("exec_id"),
            "category": result.get("category"),
            "name": result.get("name"),
            "parent_id": result.get("parent_id"),
            "test_record_id": result.get("id"),
            "test_record": result.get("id"),
            "url": result.get("request").get("url"),
            "method": result.get("request").get("method"),
            "request_header": test_content["request"].get("headers") if test_content else {},
            "request_content": test_content["request"].get("content") if test_content else {},
            "status": result.get("result"),
            "result": result.get("result_detail"),
            "console_log": result.get("console_log", []),
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        response = format_reponse(get_json_data(test_content, "response"))
        if response:
            result.update(**response)
        self.data_list.append(result)

    def get_scenes(self):
        test_sets = [item.to_json() for item in self.runner.test_collects][0]['items']
        # 展开测试集数据
        test_sets = _get_iter_test_set_id(test_sets)
        # 获取场景信息
        test_scenes = get_case_flat(test_sets)
        filtered_df = self.df[(self.df['category'].isin([2, 3]))]

        # 场景数据获取
        task_results = filtered_df.groupby(['test_record_id']).agg({
            'exec_id': 'count',
            'status': [
                ('pass_num', lambda x: (x == 'pass').sum()),
                # 等同于Sum(Case(When(status="pass", then=Value(1)), default=Value(0)))
                ('failure_num', lambda x: (x == 'failure').sum()),
                ('error_num', lambda x: (x == 'error').sum()),
                ('unknown_num', lambda x: (x == 'unknown').sum())  # 注意：这里假设状态是'unknown'而不是'unknow'
            ]
        }).reset_index()
        task_results.columns = ['test_record_id', 'all', 'pass_num', 'failure_num', 'error_num', 'unknown_num']
        test_statistics = task_results.to_dict(orient='records')

        merge_list(test_scenes, test_statistics, ["case_id=>test_record_id"],
                   reverse=True, target_filter=["test_record_id"])
        for test_scene in test_scenes:
            if test_scene.get("pass_num") is None:
                test_scene.update({
                    "all": 0,
                    "pass_num": 0,
                    "failure_num": 0,
                    "error_num": 0,
                    "unknown_num": 0
                })
        return test_scenes

    def get_apicount(self):
        case_df = self.df[self.df['category'] != 2]
        status_column = case_df['status']
        status_count = status_column.value_counts()
        api_count = len(status_column)
        api_request_num = {'all': api_count}
        for value in self.status_values:
            if value in status_count:
                api_request_num[value] = int(status_count[value])
            else:
                api_request_num[value] = 0
        for value in self.status_values:
            api_request_num[f"{value}_rate"] = "%.2f" % (
                    round((api_request_num[value] / api_count),
                          2) * 100) + "%" if api_count != 0 else "0%"
        return api_request_num

    def get_checkpoint(self):
        result_column = self.df['result']
        result_column = result_column.apply(lambda x: ast.literal_eval(x))
        check_point_num = {}
        # 遍历result列的每一行数据
        for row_data in result_column:
            if row_data:
                for item in row_data:
                    result = item.get('result', '')
                    if result in check_point_num:
                        check_point_num[result] += 1
                    else:
                        check_point_num[result] = 1
        total_count = sum(check_point_num.values())
        check_point_num['all'] = total_count
        for value in self.status_values:
            if value not in check_point_num:
                check_point_num[value] = 0
        for value in self.status_values:
            check_point_num[f"{value}_rate"] = "%.2f" % (
                    round((check_point_num[value] / total_count),
                          2) * 100) + "%" if total_count != 0 else "0%"
        return check_point_num

    def get_scenecount(self):
        test_scenes = self.get_scenes()
        scene_num_pass = 0
        scene_num_failure = 0
        scene_num_error = 0
        scene_num_unknown = 0
        scene_num_all = len(test_scenes)
        for data_num_info in test_scenes:
            if data_num_info["pass_num"] == data_num_info["all"]:
                scene_num_pass += 1
            if data_num_info["failure_num"] != 0:
                scene_num_failure += 1
            if data_num_info["error_num"] != 0:
                scene_num_error += 1
            if data_num_info["unknown_num"] != 0:
                scene_num_unknown += 1

        scene_num_pass_rate = "%.2f" % (
                round((scene_num_pass / scene_num_all), 2) * 100) + "%" if scene_num_all != 0 else "0%"
        scene_num_failure_rate = "%.2f" % (
                round((scene_num_failure / scene_num_all), 2) * 100) + "%" if scene_num_all != 0 else "0%"
        scene_num_error_rate = "%.2f" % (
                round((scene_num_error / scene_num_all), 2) * 100) + "%" if scene_num_all != 0 else "0%"
        scene_num = {"all": scene_num_all, "pass": scene_num_pass, "failure": scene_num_failure,
                     "error": scene_num_error, "unknown": scene_num_unknown,
                     "pass_rate": scene_num_pass_rate, "failure_rate": scene_num_failure_rate,
                     "error_rate": scene_num_error_rate}
        return scene_num

    def generat_report(self):
        data = {
            "case_exec_info": {"api_request_num": self.get_apicount(),
                               "check_point_num": self.get_checkpoint(),
                               "scene_num": self.get_scenecount()},
            "data_detail": [item for item in self.data_list if item.get('category') != 2],
            "scenes_info": self.get_scenes()}
        json_path = os.path.join(self.report_path, "alldata.json")
        with open(json_path, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
