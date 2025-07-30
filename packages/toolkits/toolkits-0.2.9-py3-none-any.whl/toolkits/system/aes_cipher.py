import base64
from Crypto.Cipher import AES
from Crypto import Random


BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s)-1:])]


class AESCipher:
    def __init__(self, key, iv_code=None):
        self.key = key
        self.iv_random_flag = False

        if iv_code:
            self.iv = iv_code
        else:
            self.iv_random_flag = True
            self.iv = Random.new().read(AES.block_size)

    def encrypt(self, raw):
        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

        if self.iv_random_flag:
            ret = base64.b64encode(self.iv + cipher.encrypt(raw))
        else:
            ret = base64.b64encode(cipher)
        return ret

    def decrypt(self, enc):
        enc = base64.b64decode(enc)

        if self.iv_random_flag:
            self.iv = enc[:16]

        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

        if self.iv_random_flag:
            ret = unpad(cipher.decrypt(enc[16:]))
        else:
            ret = unpad(cipher.decrypt(enc))
        return ret
