"""
@author:cmcc
@file: base_request.py
@time: 2024/7/30 10:38
"""
from abc import ABC, abstractmethod


class BaseRequest(ABC):

    @abstractmethod
    def send(self, *args, **kwargs):
        pass

