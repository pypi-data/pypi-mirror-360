import collections
import json
import logging
import datetime

logger = logging.getLogger(__name__)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        else:
            return json.JSONEncoder.default(self, obj)


class AssertResult(object):
    def __init__(self, result, msg, error=None):
        self.result = result
        self.msg = msg
        self.error = str(error)

    def __str__(self):
        return f'result: {self.result}, msg: {self.msg}, error: {self.error}'

    def to_json(self):
        return {'result': self.result, "msg": self.msg, "error": self.error}


class TestResult(object):
    def __init__(self):
        self.current_id = None
        self.total = 0
        self.total_skip = 0
        self.total_failure = 0
        self.total_success = 0
        self.total_error = 0
        self.collect_result = collections.OrderedDict()  # {id:{ name: test_collect, item:[] }

    def set_current_collect(self, id, name):
        self.current_id = id
        self.collect_result[id] = {'name': name, "items": []}

    def set_test_case_start(self, item):
        """新增item到testcollect"""
        collect = self.collect_result.get(self.current_id)
        item.status = "running"
        if collect['items']:
            items = [collect['items'][-1]]
        else:
            items = [collect['items']]
        if item.parent_id is None:
            collect['items'].append(item.to_result_item())
        else:
            self._update_item(items, item, "new")

    def set_test_case_stop(self, item):
        collect = self.collect_result.get(self.current_id)
        item.status = "finish"
        items = [collect['items'][-1]]
        self._update_item(items, item, "update")

    def _update_item(self, items, item_exec, select_type="new"):
        """更新节点信息, new：新增， update： 更新"""
        for item in items:
            if select_type == "update":
                if item['id'] == item_exec.id:
                    item.update(item_exec.to_result_item())
                    break
            elif select_type == "new":
                if item['id'] == item_exec.parent_id:
                    item['items'].append(item_exec.to_result_item())
            if item['items']:
                self._update_item(item['items'], item_exec, select_type)

    def set_test_result(self, test_result):
        """记录测试结果"""
        result = test_result.get('result')
        self.total = self.total + 1
        if result == "pass":
            self.total_success = self.total_success + 1
        elif result == "failure":
            self.total_failure = self.total_failure + 1
        elif result == "error":
            self.total_error = self.total_error + 1

    def to_json(self):
        return json.dumps(self.collect_result, cls=MyEncoder, ensure_ascii=False, indent=" ")


class CollectRequestProcess(object):
    def __init__(self):
        self.request = {}
        self.response = {}
        self.error = None

    def __str__(self):
        return f'request: {json.dumps(self.request, ensure_ascii=False)}, ' \
               f'response: {json.dumps(self.response, ensure_ascii=False)}'

    def to_json(self):
        return {
            "request": self.request,
            "response": self.response
            }
