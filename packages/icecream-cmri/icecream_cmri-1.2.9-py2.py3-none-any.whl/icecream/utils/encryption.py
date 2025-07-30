"""
@author:cmcc
@file: cipher_util.py
@time: 2022/10/8 14:36
"""
import hashlib
from icecream.utils.aes_cryptor import AEScryptor


def decode_passwd(data: dict):
    for key, value in data.items():
        if key.startswith("@icepwd_"):
            data[key] = CryptUtil.aes_decode(value)


class CryptUtil:

    @classmethod
    def pick_fix_char(cls, str_data):
        result = []
        num = [2, 1, 12, 9, 6]
        for i in num:
            result.append(str_data[i])
        return "".join(result)

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

    @classmethod
    def aes_encrypt(cls, str_data: str):
        key = b"H@667H89*&&`~@$8"
        iv = b"0000000000000000"
        aes = AEScryptor(key, iv, padding_mode="ZeroPadding")
        en_data = aes.encryptFromString(str_data)
        return cls.pick_fix_char(en_data.to_base64()) + en_data.to_base64()

    @classmethod
    def aes_decode(cls, str_data: str):
        key = b"H@667H89*&&`~@$8"
        iv = b"0000000000000000"
        aes = AEScryptor(key, iv, padding_mode="ZeroPadding")
        offset = len(cls.pick_fix_char(str_data))
        return aes.decryptFromBase64(str_data[offset:]).to_string()

