"""
@author:cmcc
@file: aes_cryptor.py
@time: 2022/10/8 15:13
"""

import base64
import binascii
from Crypto.Cipher import AES


class MData:

    def __init__(self, data=b"", charset='utf-8'):
        # data肯定为bytes
        self.data = data
        self.charset = charset

    def save_data(self, file_name):
        with open(file_name, 'wb') as f:
            f.write(self.data)

    def from_string(self, data):
        self.data = data.encode(self.charset)
        return self.data

    def from_base64(self, data):
        self.data = base64.b64decode(data.encode(self.charset))
        return self.data

    def from_hexstr(self, data):
        self.data = binascii.a2b_hex(data)
        return self.data

    def to_string(self):
        return self.data.decode(self.charset)

    def to_base64(self):
        return base64.b64encode(self.data).decode()

    def to_hexstr(self):
        return binascii.b2a_hex(self.data).decode()

    def to_bytes(self):
        return self.data

    def __str__(self):
        try:
            return self.to_string()
        except Exception:
            return self.to_base64()


class AEScryptor:
    """
        key = b"1234567812345678"
        iv = b"0000000000000000"
        aes = AEScryptor(key, iv, padding_mode="ZeroPadding")
        data = "天天向上"
        rData = aes.encryptFromString(data)
        print("密文：", rData.to_base64())
        rData = aes.decryptFromBase64(rData.to_base64())
        print("明文：", rData.to_string())
    """

    def __init__(self, key: bytes, iv: bytes, mode=AES.MODE_CBC, padding_mode="NoPadding", charset="utf-8"):
        """
        构建一个AES对象
        key: 秘钥，字节型数据
        mode: 使用模式，只提供两种，AES.MODE_CBC, AES.MODE_ECB
        iv： iv偏移量，字节型数据
        paddingMode: 填充模式，默认为NoPadding, 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        charset: 字符集编码
        """
        self.key = key
        self.mode = mode
        self.iv = iv
        self.charset = charset
        self.padding_mode = padding_mode
        self.data = ""

    def __zero_padding(self, data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    def __strip_zero_padding(self, data):
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    def __PKCS5_7Padding(self, data):
        needSize = 16 - len(data) % 16
        if needSize == 0:
            needSize = 16
        return data + needSize.to_bytes(1, 'little') * needSize

    def __StripPKCS5_7Padding(self, data):
        paddingSize = data[-1]
        return data.rstrip(paddingSize.to_bytes(1, 'little'))

    def __padding_data(self, data):
        if self.padding_mode == "NoPadding":
            if len(data) % 16 == 0:
                return data
            else:
                return self.__zero_padding(data)
        elif self.padding_mode == "ZeroPadding":
            return self.__zero_padding(data)
        elif self.padding_mode == "PKCS5Padding" or self.padding_mode == "PKCS7Padding":
            return self.__PKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def __stripPaddingData(self, data):
        if self.padding_mode == "NoPadding":
            return self.__strip_zero_padding(data)
        elif self.padding_mode == "ZeroPadding":
            return self.__strip_zero_padding(data)

        elif self.padding_mode == "PKCS5Padding" or self.padding_mode == "PKCS7Padding":
            return self.__StripPKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def setCharacterSet(self, charset):
        '''
        设置字符集编码
        characterSet: 字符集编码
        '''
        self.charset = charset

    def setPaddingMode(self, mode):
        '''
        设置填充模式
        mode: 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        '''
        self.padding_mode = mode

    def decryptFromBase64(self, entext):
        '''
        从base64编码字符串编码进行AES解密
        entext: 数据类型str
        '''
        data = MData(charset=self.charset)
        self.data = data.from_base64(entext)
        return self.__decrypt()

    def decryptFromHexStr(self, entext):
        '''
        从hexstr编码字符串编码进行AES解密
        entext: 数据类型str
        '''
        data = MData(charset=self.charset)
        self.data = data.from_hexstr(entext)
        return self.__decrypt()

    def decryptFromString(self, entext):
        '''
        从字符串进行AES解密
        entext: 数据类型str
        '''
        data = MData(charset=self.charset)
        self.data = data.from_string(entext)
        return self.__decrypt()

    def decryptFromBytes(self, entext):
        '''
        从二进制进行AES解密
        entext: 数据类型bytes
        '''
        self.data = entext
        return self.__decrypt()

    def encryptFromString(self, data):
        '''
        对字符串进行AES加密
        data: 待加密字符串，数据类型为str
        '''
        self.data = data.encode(self.charset)
        return self.__encrypt()

    def __encrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return

        data = self.__padding_data(self.data)
        en_data = aes.encrypt(data)
        return MData(en_data)

    def __decrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return
        data = aes.decrypt(self.data)
        return MData(self.__stripPaddingData(data), charset=self.charset)

