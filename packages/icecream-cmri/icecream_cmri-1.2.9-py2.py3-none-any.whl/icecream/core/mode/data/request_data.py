import json
from abc import ABC, abstractmethod


class IReqData(ABC):

    def to_dict(self):
        return self.__dict__


class HttpReqData(IReqData):

    def __init__(self, request_dict):
        self.method = request_dict.get("method")
        self.header = request_dict.get("header", {})
        self.url = request_dict.get("url")
        self.params = request_dict.get("query")
        self.parameters = request_dict.get("params")
        self.body = request_dict.get("body")


class WebSocketReqData(IReqData):

    def __init__(self, request_dict):
        self.url = request_dict.get("url")
        self.payload = request_dict.get("payload")



if __name__ == '__main__':
    request_dict = {'header': {'Access-Token': '{{AccessToken}}'}, 'method': 'GET',
                    'url': 'http://{{HOST}}/ai/pangu/api/manage/v1/userproject',
                    'query': {'pageNo': '1', 'pageSize': '100'}}
    req_data = HttpReqData(request_dict)
    r = req_data.to_dict()
    print(json.dumps(r, indent=2))


