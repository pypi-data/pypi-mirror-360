# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/19 17:17

@Author  : wangchao
"""
import random
import string
import time


def generate_str(length=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    for i in range(length):
        random_str += base_str[random.randint(0, len(base_str) - 1)]
    return random_str


def generate_num(length):
    """
    生成随机数
    """
    ran_str = ''.join(random.sample(string.digits, length))
    return ran_str


def generate_phone_num():
    """
    生成手机号
    """
    prefix = [133, 149, 153, 173, 177, 180, 181, 189, 191, 199, 130, 131, 132, 145, 155, 156, 166, 171, 175, 176, 185,
              186, 135, 136, 137, 138, 139, 147, 150, 151, 152, 157, 158, 159, 172, 178, 182, 183, 184, 187, 188, 198]
    phone = str(random.choice(prefix)) + "".join(random.choice("0123456789") for i in range(8))
    return phone


def generate_sessionid():
    """
    生成sesssionId
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(characters, k=32))


def generate_id_s():
    """
    生成秒级id
    """
    import time
    return "{}".format(round(time.time()))


def generate_id_ms():
    """生成毫秒级id"""
    return "{}".format(round(time.time() * 1000))


class RandomFunction:

    @classmethod
    def generate_str(cls, length=16):
        return generate_str(length)

    @classmethod
    def generate_num(cls, length):
        return generate_num(length)

    @classmethod
    def generate_phone_num(cls):
        return generate_phone_num()

    @classmethod
    def generate_sessionid(cls):
        return generate_sessionid()

    @classmethod
    def generate_id_s(cls):
        return generate_id_s()

    @classmethod
    def generate_id_ms(cls):
        return generate_id_ms()


__all__ = [
    "RandomFunction",
    "generate_str", "generate_num", "generate_phone_num", "generate_id_s", "generate_id_ms", "generate_sessionid"
]
