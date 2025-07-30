# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/19 17:17

@Author  : wangchao
"""
import os

import pandas as pd


def read_csv(path):
    """
    读取并解析csv
    """
    data = pd.read_csv(path, encoding=u'gbk')
    return data


def get_file_params_limit(file_params, limit_num):
    """
    获取参数化文件中的指定行数
    """
    top = []
    i = 0
    for data in file_params:
        top.append(data)
        if limit_num != -1:
            i += 1
            if i >= limit_num:
                break
    for iter_data in top:
        yield {"title": iter_data.get("title"), "data": iter_data.get("data")}


def get_file_info(filename):
    """
     获取文件全路径、文件名（带后缀名）、不带后缀的文件名、文件后缀名
    """
    (filepath, temp_filename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(temp_filename)
    return filepath, temp_filename, shortname, extension


def list_all_files(path):
    """
    读取文件夹下的所有文件，返回所有文件的文件全路径
    """
    list_name = []
    for file in os.listdir(path):

        file_path = path + "/" + file  # os.path.join(path, file)
        if os.path.isdir(file_path):
            list_all_files(file_path)
        else:
            list_name.append(file_path)
    return list_name


class FileProcessingFunction:

    @classmethod
    def read_csv(cls, path):
        return read_csv(path)

    @classmethod
    def get_file_params_limit(cls, file_params, limit_num):
        return get_file_params_limit(file_params, limit_num)

    @classmethod
    def get_file_info(cls, filename):
        return get_file_info(filename)

    @classmethod
    def list_all_files(cls, path):
        return list_all_files(path)


__all__ = [
    "FileProcessingFunction", "read_csv", "get_file_params_limit", "get_file_info", "list_all_files"
]
