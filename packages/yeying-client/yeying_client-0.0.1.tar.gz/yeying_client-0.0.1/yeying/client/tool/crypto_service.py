# -*- coding:utf-8 -*-
import base64
from enum import Enum
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
from ecdsa import SECP256k1, SigningKey, VerifyingKey
from yeying.api.web3 import BlockAddress, Mnemonic, SecurityAlgorithm


class CipherTypeEnum(Enum):
    CIPHER_TYPE_UNKNOWN = 0
    CIPHER_TYPE_AES_GCM_256 = 1


def trim_left(s: str, trim_str: str) -> str:
    if s is None:
        return s
    return s[len(trim_str):] if s.startswith(trim_str) else s


def derive_from_block_address(block_address: BlockAddress) -> bytes:
    """使用私钥和公钥通过ECDH派生密钥"""
    # 移除十六进制前缀
    private_key_hex = trim_left(block_address.privateKey, '0x')
    public_key_hex = trim_left(block_address.publicKey, '0x')

    # 从私钥创建签名密钥对象
    private_key_bytes = bytes.fromhex(private_key_hex)
    if len(private_key_bytes) != 32:
        raise ValueError(f"Invalid private key length: {len(private_key_bytes)} bytes, expected 32 bytes")

    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)

    # 从公钥创建验证密钥对象（使用VerifyingKey处理公钥）
    public_key_bytes = bytes.fromhex(public_key_hex)
    if len(public_key_bytes) not in (33, 65):
        raise ValueError(f"Invalid public key length: {len(public_key_bytes)} bytes, expected 33 or 65 bytes")

    vk = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)

    # 使用ECDH进行密钥派生
    shared_point = sk.privkey.secret_multiplier * vk.pubkey.point

    # 将共享点的x坐标作为派生密钥
    x_bytes = shared_point.x().to_bytes(32, 'big')
    return x_bytes


def convert_to_algorithm_name(cipher_type: CipherTypeEnum) -> str:
    """将密码类型转换为算法名称"""
    return 'AES-GCM' if cipher_type == CipherTypeEnum.CIPHER_TYPE_AES_GCM_256 else 'AES-GCM'


def decode_base64(data: str) -> bytes:
    """Base64解码"""
    return base64.b64decode(data)


class InvalidPassword(Exception):
    """无效密码异常"""
    pass


def encrypt(key: bytes, data: bytes, iv: bytes, algorithm: str = 'AES-GCM') -> bytes:
    """使用AES-GCM加密数据"""
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return ciphertext + encryptor.tag


def decrypt(key: bytes, data: bytes, iv: bytes, algorithm: str = 'AES-GCM') -> bytes:
    """使用AES-GCM解密数据"""
    if len(data) < 16:  # 确保有足够的长度包含标签
        raise InvalidPassword("Invalid ciphertext length")

    # 分离密文和认证标签
    ciphertext = data[:-16]
    tag = data[-16:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()

    try:
        return decryptor.update(ciphertext) + decryptor.finalize()
    except InvalidTag:
        raise InvalidPassword("Authentication failed - invalid tag")


class AssetCipher:
    """提供资产加密和解密功能"""

    def __init__(self, block_address: BlockAddress, security_algorithm: SecurityAlgorithm):
        # 派生原始密钥
        raw_key = derive_from_block_address(block_address)

        # 使用HKDF派生更安全的密钥
        self._derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256需要32字节密钥
            salt=None,
            info=b'asset-cipher-key',
            backend=default_backend()
        ).derive(raw_key)

        # 获取算法名称和IV
        algo_name: str = "CIPHER_TYPE_AES_GCM_256" if security_algorithm.name in ["CIPHER_TYPE_AES_GCM_256", "AES-GCM"] else "CIPHER_TYPE_AES_GCM_256"
        cipher_type: CipherTypeEnum = CipherTypeEnum[algo_name]
        self._algorithm_name = convert_to_algorithm_name(cipher_type)
        self._iv = decode_base64(security_algorithm.iv)

    def decrypt(self, data: bytes) -> bytes:
        """解密数据"""
        return decrypt(self._derived_key, data, self._iv, self._algorithm_name)

    def encrypt(self, data: bytes) -> bytes:
        """加密数据"""
        return encrypt(self._derived_key, data, self._iv, self._algorithm_name)


if __name__ == "__main__":
    # 创建BlockAddress
    block_address = BlockAddress(
        identifier="did:ethr:0x07e4:0x035b737f93ef1a74b7fd32b62b4e313876722957ca3c705588cc3c883bf2fb568c",
        address="0x45C6ff6AF1Ec4E5D15668351B12A6C630a053e16",
        privateKey="0x2721a1f0de1656df452fa83238350d56b44403f2f02a59e840e854b61010c632",  # 64字符十六进制
        publicKey="0x035b737f93ef1a74b7fd32b62b4e313876722957ca3c705588cc3c883bf2fb568c",  # 128字符十六进制
        mnemonic=Mnemonic(
            phrase="trigger happy matter office zoo chicken conduct borrow civil refuse addict lunar",
            path="m/44'/60'/0'/0/0",
            locale="en",
            password=""
        )
    )

    # 创建安全算法配置
    security_algorithm = SecurityAlgorithm(
        name="CIPHER_TYPE_AES_GCM_256",
        iv="PWPhFzsftCklcfgc"  # 12字节的Base64编码
    )

    # 初始化加密器
    cipher = AssetCipher(block_address, security_algorithm)

    # 加密数据
    plain_data = b"Secret message"
    encrypted = cipher.encrypt(plain_data)
    print(f"encrypted={encrypted}")

    # 解密数据
    decrypted = cipher.decrypt(encrypted)
    print(f"decrypted={decrypted}")
    assert decrypted == plain_data

    # 处理无效密码
    try:
        cipher.decrypt(b"invalid ciphertext")
    except InvalidPassword:
        print("Decryption failed due to invalid password")