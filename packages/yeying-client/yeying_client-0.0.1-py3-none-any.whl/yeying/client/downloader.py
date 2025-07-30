# -*- coding:utf-8 -*-
from yeying.api.web3 import SecurityAlgorithm
from yeying.client.model.option import ProviderOption
from yeying.client.provider.asset_provider import AssetProvider
from yeying.client.provider.block_provider import BlockProvider
from yeying.client.provider.config_provider import ConfigProvider
from yeying.api.asset import BlockMetadata, asset_pb2
from yeying.api.config import ConfigTypeEnum
from yeying.client.tool.crypto_service import AssetCipher
from yeying.client.utils import log_utils
from typing import Callable, TypedDict

log = log_utils.get_logger(__name__)


class Progress(TypedDict):
    """进度接口"""

    total: int
    completed: int


class DownloadResult(TypedDict):
    """上传结果接口"""

    block: BlockMetadata
    data: bytes
    progress: Progress


# 定义回调类型
DownloadCallback = Callable[[DownloadResult], None]

"""
资产仓库的客户端实现
文件下载
"""
class Downloader(object):

    def __init__(self, option: ProviderOption, algorithm: SecurityAlgorithm):
        # 数据块加密
        self.asset_cipher = AssetCipher(option.block_address, algorithm)
        # 资产元信息
        self.asset_provider = AssetProvider(option=option)
        # 文件操作
        self.block_provider = BlockProvider(option=option)
        # 字典配置
        self.config_provider = ConfigProvider(option=option)
        # 文件单个块的大小，从系统配置表中动态获取
        config_res = self.config_provider.get("chunk.size", ConfigTypeEnum.CONFIG_TYPE_SYSTEM)
        self.chunkSize = int(config_res.body.config.value)
        self.is_abort: bool = False

    def abort(self):
        self.is_abort = True

    def get(
        self,
        namespace_id: str,
        _hash: str,
        block_callback: DownloadCallback = None,
    ) -> asset_pb2.AssetMetadata:
        log.info("start download file")
        detail_res = self.asset_provider.detail(namespace_id, _hash)
        asset = detail_res.body.asset
        for i in range(asset.chunkCount):
            if self.is_abort:
                log.warn("download is abort")
                return asset_pb2.AssetMetadata()
            get_res = self.block_provider.get(namespace_id, asset.chunks[i])
            detail = BlockDetail(block=get_res.body.block, data=get_res.data)
            if asset.isEncrypted:
                # 如果资产加密，解密数据块
                detail.data = self.asset_cipher.decrypt(detail.data)
            if block_callback:
                result = DownloadResult(block=detail.block, data=detail.data, progress=Progress(total=asset.chunkCount, completed=i+1))
                block_callback(result)
        return asset

class BlockDetail(object):

    def __init__(self, block: BlockMetadata, data: bytes):
        self.block = block
        self.data = data