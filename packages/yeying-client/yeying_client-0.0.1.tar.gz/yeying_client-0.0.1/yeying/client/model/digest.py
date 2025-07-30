# -*- coding:utf-8 -*-
"""用于更新和计算数据的哈希值，并最终返回计算结果。"""
import hashlib

from yeying.client.utils.signature_utils import encode_hex


class Digest:

    def __init__(self):
        """创建一个新的 Digest 实例，并初始化哈希状态。默认使用 SHA-256 初始哈希值。"""
        # 初始化 SHA-256 哈希状态
        self.sha256 = hashlib.sha256()

    def update(self, data: bytes):
        """
        更新哈希计算过程。

        :param data: 新的数据块，用于更新哈希值
        :return: 当前实例，便于链式调用
        """
        self.sha256.update(data)
        return self

    def digest(self):
        return self.sha256.digest()


# 测试代码
if __name__ == "__main__":
    digest = Digest()
    digest.update(b"Hello, ")
    digest.update(b"world!")
    result = digest.digest()
    print(encode_hex(result))
