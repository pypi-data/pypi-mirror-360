import base64
from typing import Optional

from Crypto.Cipher import AES # noqa
from Crypto.Util.Padding import pad, unpad # noqa


class AesPwdUtils:
    DEFAULT_KEY = b"jski2ksuey4xn8fu"

    def __init__(self, key: Optional[bytes] = None):
        if key is not None:
            self.key = key
        else:
            self.key = self.DEFAULT_KEY

    # 加密函数
    def encrypt(self, plain_text):
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        cipher_text, tag = cipher.encrypt_and_digest(plain_text.encode())
        return base64.b64encode(nonce + cipher_text + tag).decode()

    # 解密函数
    def decrypt(self, cipher_text):
        cipher_text = base64.b64decode(cipher_text.encode())
        nonce = cipher_text[:16]
        ciphered_data = cipher_text[16:-16]
        tag = cipher_text[-16:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        plain_text = cipher.decrypt_and_verify(ciphered_data, tag)
        return plain_text.decode()
