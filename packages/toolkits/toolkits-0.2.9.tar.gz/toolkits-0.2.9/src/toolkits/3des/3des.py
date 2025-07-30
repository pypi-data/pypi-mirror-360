# -*- coding: utf-8 -*-

import pyDes
import base64


class TripleDesUtils:
    des_mode = {"CBC": pyDes.CBC, "ECB": pyDes.ECB}
    des_pad_mode = {"PAD_PKCS5": pyDes.PAD_PKCS5, "PAD_NORMAL": pyDes.PAD_NORMAL}

    def __init__(self, mode, pad_mode, key, iv, pad=None, trans_base64=False):
        """
        :param mode: des 加密模式，目前支持 CBC，ECB
        :param pad_mode: 目前支持 PAD_PKCS5，PAD_NORMAL
        :param trans_base64: 加密结果是否以 base64 格式输出
        :param key: 密钥
        :param iv: 偏移量
        :param pad:
        """
        self.trans_base64 = trans_base64
        self.k = pyDes.triple_des(key, TripleDesUtils.des_mode.get(mode), iv, pad, TripleDesUtils.des_pad_mode.get(pad_mode))

    def encryption(self, data):
        """
        3des 加密
        说明: 3DES数据块长度为64位，所以IV长度需要为8个字符（ECB模式不用IV），密钥长度为16或24个字符（8个字符以内则结果与DES相同
        IV与密钥超过长度则截取，不足则在末尾填充'\0'补足
        :param data: 待加密数据
        :return:
        """
        _encryption_result = self.k.encrypt(data)
        if self.trans_base64:
            _encryption_result = self._base64encode(_encryption_result)
        return _encryption_result

    def decrypt(self, data):
        """
        3des 解密
        :param data: 待解密数据
        :return:
        """
        if self.trans_base64:
            data = self._base64decode(data)
        _decrypt_result = self.k.decrypt(data)
        return _decrypt_result

    @staticmethod
    def _base64encode(data):
        """
        base 64 encode
        :param data: encode data
        :return:
        """
        try:
            _b64encode_result = base64.b64encode(data)
        except Exception as e:
            raise Exception("base64 encode error:{e}")
        return _b64encode_result

    @staticmethod
    def _base64decode(data):
        """
        base 64 decode
        :param data: decode data
        :return:
        """
        try:
            _b64decode_result = base64.b64decode(data)
        except Exception as e:
            raise Exception("base64 decode error:{e}")
        return _b64decode_result


if __name__ == "__main__":
    test_data = "12345678a"
    key_a = "uusafeuusafeuusafeuusafe"
    key_b = "jiayufeuusafeuusafeuusaf"
    # [12345678a] 3des Result: 2yjtt0Y/c7xEOa9VGetBVA==
    DesObj = TripleDesUtils(mode="CBC", pad_mode="PAD_PKCS5", key=key_a, iv="01234567", trans_base64=True)
    result_a = DesObj.encryption(test_data)
    print("加密结果: %s" % result_a)
    DesObj = TripleDesUtils(mode="CBC", pad_mode="PAD_PKCS5", key=key_b, iv="01234567", trans_base64=True)
    result_b = DesObj.encryption(result_a)
    print("加密结果: %s" % result_b)

    # result2 = DesObj.decrypt(result)
    # print("解密结果: %s" % result2)
    DesObj = TripleDesUtils(mode="CBC", pad_mode="PAD_PKCS5", key=key_b, iv="01234567", trans_base64=True)
    result_a = DesObj.encryption(test_data)
    print("加密结果: %s" % result_a)
    DesObj = TripleDesUtils(mode="CBC", pad_mode="PAD_PKCS5", key=key_a, iv="01234567", trans_base64=True)
    result_b = DesObj.encryption(result_a)
    print("加密结果: %s" % result_b)
