import string
import random


class StringUtils:
    ALL_CHARACTERS = string.ascii_letters + string.digits + string.punctuation

    @classmethod
    def generate_random_string(cls, length):
        # 生成一个包含大小写字母、数字和特殊符号的所有可选字符的字符串

        # 从所有可选字符中随机选择指定长度的字符，组成字符串
        random_string = ''.join(random.choice(cls.ALL_CHARACTERS) for _ in range(length))
        return random_string
