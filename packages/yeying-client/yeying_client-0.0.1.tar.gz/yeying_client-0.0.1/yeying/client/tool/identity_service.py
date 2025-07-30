# -*- coding:utf-8 -*-
import codecs
import os.path

from google.protobuf.json_format import Parse

from yeying.api.common import CipherTypeEnum
from yeying.api.web3 import Identity, SecurityAlgorithm, BlockAddress
from yeying.client.model.identity import verify_identity
from yeying.client.utils import log_utils

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from yeying.client.utils.string_utils import decode_base64

log = log_utils.get_logger(__name__)


def load(identity_str) -> Identity:
    if not identity_str:
        log.error(f"param identity is None")
        raise Exception("param identity is None")
    content = identity_str
    if os.path.isfile(identity_str):
        content = codecs.open(identity_str, "r").read()
    identity: Identity = Parse(content, Identity())
    passed = verify_identity(identity)
    if not passed:
        log.error(f"Invalid identity={identity.metadata.did}")
        raise Exception(f"Invalid identity={identity.metadata.did}")
    return identity


def convert_cipher_type_from(type_str: str) -> CipherTypeEnum:
    algorithm_map = {
        "AES-GCM": CipherTypeEnum.CIPHER_TYPE_AES_GCM_256,
        # 可以在此添加更多枚举值到算法名称的映射
    }
    # 获取对应的算法名称，如果找不到则返回默认值
    return algorithm_map.get(type_str, CipherTypeEnum.CIPHER_TYPE_AES_GCM_256)


def convert_to_algorithm_name(cipher_type: CipherTypeEnum) -> str:
    """将加密类型枚举转换为对应的算法名称

    Args:
        cipher_type: 加密类型枚举值

    Returns:
        对应的算法名称字符串
    """
    # 使用字典映射实现类似 switch-case 的功能
    algorithm_map = {
        CipherTypeEnum.CIPHER_TYPE_AES_GCM_256: "AES-GCM",
        # 可以在此添加更多枚举值到算法名称的映射
    }

    # 获取对应的算法名称，如果找不到则返回默认值
    return algorithm_map.get(cipher_type, "AES-GCM")


def compute_hash(content: bytes) -> bytes:
    """计算 SHA-256 哈希值"""
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(content)
    return digest.finalize()


def derive_raw_key_from_string(algorithm_name: str, password: str) -> bytes:
    """
    从字符串派生原始密钥
    注意：Python 中通常直接返回密钥字节，而不是密钥对象
    """
    # 编码内容并计算哈希
    content_bytes = password.encode('utf-8')
    hash_bytes = compute_hash(content_bytes)

    # 根据算法类型处理密钥
    if "AES" in algorithm_name:
        # AES 需要固定长度的密钥 (16/24/32 字节)
        key_length = 32  # 使用 SHA256 的 32 字节作为 AES-256
        return hash_bytes[:key_length]
    elif "HMAC" in algorithm_name:
        # HMAC 可直接使用哈希值
        return hash_bytes
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm_name}")


def decrypt(
        name: str,
        key: bytes,  # 原始密钥字节
        iv: bytes,  # 初始化向量
        content: bytes  # 密文字节
) -> bytes:
    # 根据算法名称创建相应的解密器
    if "AES-CBC" in name or "AES_CBC" in name:
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        data_to_decrypt = content  # CBC模式使用完整密文
    elif "AES-GCM" in name or "AES_GCM" in name:
        # 对于 GCM 模式，分离认证标签（最后16字节）
        if len(content) < 16:
            raise ValueError("Invalid ciphertext for AES-GCM")
        data_to_decrypt = content[:-16]  # 实际密文（不含标签）
        tag = content[-16:]              # 认证标签
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),  # 将标签传入GCM模式
            backend=default_backend()
        )
    else:
        raise ValueError(f"Unsupported algorithm: {name}")

    # 创建解密器并执行解密
    decrypt_instance = cipher.decryptor()
    # 关键修复：使用data_to_decrypt而非完整content
    plaintext = decrypt_instance.update(data_to_decrypt) + decrypt_instance.finalize()
    return plaintext


def decrypt_block_address(block_address: str, security_algorithm: SecurityAlgorithm, password: str) -> BlockAddress:
    # algorithm_name = convert_to_algorithm_name(convert_cipher_type_from(security_algorithm.name))
    algorithm_name = security_algorithm.name
    crypto_key = derive_raw_key_from_string(algorithm_name, password)
    plain = decrypt(algorithm_name, crypto_key, decode_base64(security_algorithm.iv), decode_base64(block_address))
    print(plain.decode())
    block = BlockAddress()
    block.ParseFromString(plain)
    print(f"block={type(block)}")
    return block



