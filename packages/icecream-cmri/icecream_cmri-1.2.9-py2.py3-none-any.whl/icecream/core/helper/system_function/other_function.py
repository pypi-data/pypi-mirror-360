# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/19 17:17

@Author  : wangchao
"""
import base64
import json
import jmespath as jp


def get_jsonpath(json_object, expr):
    """
    jsonpath解析
    """
    return jp.search(expr, json_object)


def loads(json_s):
    """
    解析json字符串

    json_s(str):
    """
    return json.loads(json_s)


def image_base64(filename):
    """
    获取图片base64码

    filename(str):
    """
    with open(filename, "rb") as f:
        image64 = base64.b64encode(f.read())
        image64_str = str(image64, encoding="utf-8")
    return image64_str


def object_to_base64(obj):
    """
    获取对象的base64值

    obj(dict):
    e.g. {'type': 'JPG', 'scenes': ['scene']}
    """
    obj_str = json.dumps(obj)
    obj_b64 = base64.b64encode(obj_str.encode('utf-8'))
    obj_b64_str = str(obj_b64, 'utf-8')
    return obj_b64_str


class OtherFunction:
    @classmethod
    def get_jsonpath(cls, json_object, expr):
        return jp.search(expr, json_object)

    @classmethod
    def loads(cls, json_s):
        return loads(json_s)

    @classmethod
    def image_base64(cls, filename):
        return image_base64(filename)

    @classmethod
    def object_to_base64(cls, obj):
        return object_to_base64(obj)


__all__ = [
    "OtherFunction", "get_jsonpath", "loads", "image_base64", "object_to_base64"
]
