"""
@author:cmcc
@file: websocket_request.py
@time: 2024/7/22 14:53
"""
import logging

from icecream.core.test_result import CollectRequestProcess
from icecream.core.protocol.request.base_request import BaseRequest
from icecream.core.mode.data.request_data import WebSocketReqData

logger = logging.getLogger(__name__)


class WebSocketRequest(BaseRequest):
    def __init__(self, ice, req_data: WebSocketReqData, setting):
        self.ice = ice

        self.req_data = req_data

    def send(self, websocket_result: CollectRequestProcess):
        websocket_result.request = {"wupeng_req": 123}
        websocket_result.response = {"wupeng_res": 456}
