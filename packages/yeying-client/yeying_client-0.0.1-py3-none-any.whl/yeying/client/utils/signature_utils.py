import binascii
import hashlib

from ecdsa import keys, util, curves


# 因为在生成签名的过程中每次都会选择一个新的随机数k，即使使用的是相同的私钥和相同的消息内容，由于k的不同，最终生成的（r, s）对也会不同，
# 因此签名每次都是唯一的
def sign(private_key, data, sigencode=util.sigencode_der):
    signing_key = keys.SigningKey.from_string(private_key, curve=curves.SECP256k1)
    digest = hashlib.sha256(data).digest()
    return binascii.hexlify(signing_key.sign_digest(digest=digest, sigencode=sigencode))


def verify(public_key: str, data: bytes, signature: str, sigdecode=util.sigdecode_der):
    vk = keys.VerifyingKey.from_string(public_key, curve=curves.SECP256k1)
    digest = hashlib.sha256(data).digest()
    return vk.verify_digest(signature=binascii.unhexlify(signature), digest=digest, sigdecode=sigdecode)


def encode_hex(data: bytes | bytearray | memoryview) -> str:
    """
    将字节数据编码为十六进制字符串

    参数:
        data: 字节数据，支持 bytes、bytearray 或 memoryview 类型

    返回:
        str: 小写十六进制字符串

    异常:
        TypeError: 如果输入不是字节类型
    """
    # 验证输入类型
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"输入必须是字节类型，但得到的是 {type(data).__name__}")

    # 使用内置方法转换为十六进制字符串
    return data.hex()


def decode_hex(hex_str: str) -> bytes:
    """
    将十六进制字符串解码为字节数组

    参数:
        hex_str: 十六进制格式的字符串

    返回:
        bytes: 解码后的字节数组

    异常:
        ValueError: 如果输入包含非十六进制字符或长度为奇数
    """
    # 检查输入是否有效
    if not isinstance(hex_str, str):
        raise TypeError(f"输入必须是字符串，但得到的是 {type(hex_str).__name__}")

    # 移除可能存在的空格和前缀
    cleaned = hex_str.strip().lower()
    if cleaned.startswith(('0x', '0X')):
        cleaned = cleaned[2:]

    # 验证十六进制格式
    if len(cleaned) % 2 != 0:
        raise ValueError("十六进制字符串长度必须为偶数")

    if not all(c in '0123456789abcdef' for c in cleaned):
        raise ValueError("字符串包含非十六进制字符")

    # 使用内置方法转换
    return bytes.fromhex(cleaned)


# 测试代码
if __name__ == "__main__":
    hex_data = "48656c6c6f20576f726c64"  # "Hello World"
    byte_data = decode_hex(hex_data)
    print(byte_data)  # 输出: b'Hello World'

    data = b"Hello World"
    hex_str = encode_hex(data)
    print(hex_str)  # 输出: 48656c6c6f20576f726c64
