import traceback
import uuid
from icecream.core.mode.data.constant import RequestProtocol
from icecream.utils.common import Utils
from icecream.core.mode.data.request_data import *

class TestCollect(object):
    def __init__(self, content):
        test_collect = content.get("test_collect")
        self.name = test_collect.get("info").get("name")
        self.id = test_collect.get("info").get("id") or str(uuid.uuid4())
        self.items = []
        self._parser_item(test_collect.get("items"))

    def _parser_item(self, content):
        if content:
            for item in content:
                self.items.append(TestItem(item))

    def to_json(self):
        return {"name": self.name, "id": self.id, "items": [item.to_json() for item in self.items]}


class TestItem(object):
    def __init__(self, content, parent_id=None):
        self.name = content.get("name")
        self.id = content.get("id") or str(uuid.uuid1())
        self.type = content.get("type")  # # folder or case_folder or case or common
        self.from_to = content.get("from_to")
        self.parent_id = parent_id
        self.exec_id = str(uuid.uuid1())
        self.iter_num = 1
        self.inner_iter_num = 1
        self.supper_agreement = "http"  # todo 后续支持 websocket等
        self.category = content.get("category")
        self.parameters = content.get("params")
        self.status = None  # (running, finish)
        self.result = "unknown"  # (pass, failure, skip, error, unknown)
        self.test_content = None
        self.result_detail = []  # item为目录结构是，即不存在request时，此项可能没有统计值
        self.items = []
        self.test = []  # test: [{id: 123, script: ic.test.eq(1,2, failure)}}]
        self.prerequest = None  # {prerequest: {id: 111, script: ic.send_request(www.baidu.com)}
        self.setting = content.get("setting", {})  # 配置请求的一些高级配置, 如http_timeout, stream_mode模式等
        self.request = content.get("request") if "request" in content else None

        if content.get("supper_agreement"):
            self.supper_agreement = content.get("supper_agreement")

        # todo 转型req对象
        if self.supper_agreement == RequestProtocol.HTTP:
            self.req_data = HttpReqData(self.request)
        elif self.supper_agreement == RequestProtocol.WEB_SOCKET:
            self.req_data = WebSocketReqData(self.request)


        self.temp_vars = {}  # 临时变量，用于变量域扩展
        if "event" in content:
            if "prerequest" in content.get("event"):
                self.prerequest = content.get("event").get("prerequest")
            if "test" in content.get("event"):
                self.test.append(content.get("event").get("test"))
        if content.get("items"):
            self._parser_item(content.get("items"), self.test, self.id)

    def _parser_item(self, content, test=None, parent_id=None):
        if test is None:
            test = []
        if content:
            for item in content:
                test_item = TestItem(item, parent_id)
                if test:
                    tests = test_item.test + test
                    test_item.test = Utils.unique_aray(tests, "script")
                self.items.append(test_item)

    def to_result_item(self):
        # todo self.request to_json 需要每个request_data自己组装to_json函数
        return {
            'name': self.name, 'id': self.id, "category": self.category, 'iter_num': self.iter_num,
            'type': self.type, 'parent_id': self.parent_id, 'exec_id': self.exec_id,
            "inner_iter_num": self.inner_iter_num, 'from_to': self.from_to, 'setting': self.setting,
            # 'request': self.request
            'request': self.req_data.to_dict(), 'prerequest': self.prerequest,
            'test': self.test, 'items': [], "result": self.result, "status": self.status,
            "result_detail": self.result_detail, "test_content": self.test_content
        }

    def to_json(self):
        return {
            'name': self.name, 'id': self.id, 'type': self.type, 'category': self.category,
            'parent_id': self.parent_id, 'setting': self.setting, 'from_to': self.from_to,
            'request': self.request, 'prerequest': self.prerequest,
            'test': self.test, 'items': [item.to_json() for item in self.items]
        }
