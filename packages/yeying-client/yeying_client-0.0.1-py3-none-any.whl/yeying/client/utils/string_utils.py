import uuid
import base64


def unicode_encode(name):
    return name.encode("unicode-escape").decode("utf-8")


def unicode_decode(name):
    return name.encode("utf-8").decode("unicode-escape")


def generate_uuid():
    return str(uuid.uuid4())


def is_empty(s):
    return False if s and not s.isspace() else True


def decode_base64(data: str) -> bytes:
    """
    解码 Base64 字符串为字节数组

    参数:
        data: Base64 编码的字符串

    返回:
        bytes: 解码后的字节数组
    """
    # 处理可能的填充问题（Python 的 base64 模块会自动处理）
    # 添加必要的 '=' 填充字符以确保字符串长度是4的倍数
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)

    return base64.b64decode(data)