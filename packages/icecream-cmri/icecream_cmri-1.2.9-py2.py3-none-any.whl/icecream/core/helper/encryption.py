"""
@author:cmcc
@file: encryption.py
@time: 2022-03-07 15:54
"""
import hashlib


class Crypt:

    @classmethod
    def hash_md5_file(cls, filepath):
        m = hashlib.md5()
        with open(filepath, 'rb') as f:
            for line in f:
                m.update(line)
        return m.hexdigest()

    @classmethod
    def md5(cls, str_data: str):
        return hashlib.md5(str_data.encode(encoding='UTF-8')).hexdigest()

    @classmethod
    def sha1(cls, str_data: str):
        return hashlib.sha1(str_data.encode(encoding='UTF-8')).hexdigest()

    @classmethod
    def sha256(cls, str_data: str):
        return hashlib.sha256(str_data.encode(encoding='UTF-8')).hexdigest()
