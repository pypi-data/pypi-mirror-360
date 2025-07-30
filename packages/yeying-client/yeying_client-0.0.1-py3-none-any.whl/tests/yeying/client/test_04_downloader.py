# -*- coding:utf-8 -*-
import codecs
import os

from google.protobuf.json_format import MessageToJson
from tests.yeying import identity, option
from tests.yeying.client import output_file
from yeying.api.asset import asset_pb2
from yeying.client import downloader
from yeying.client.downloader import DownloadResult
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("Downloader start test")
    download_client = downloader.Downloader(option, identity.securityConfig.algorithm)
    yield download_client


def test_download(before):
    log.info("start download file")
    download_client = before
    namespace_id = os.environ.get("namespace_id")
    assert namespace_id is not None
    assert isinstance(namespace_id, str)
    log.info(f"namespace_id={namespace_id}")

    _hash = os.environ.get("hash")
    assert _hash is not None
    assert isinstance(_hash, str)
    log.info(f"_hash={_hash}")

    chunk_files = []

    def download_callback(result: DownloadResult) -> None:
        log.info(f"[文件下载回调] 进度: {result['progress']['completed']}/{result['progress']['total']}")
        log.info(f"[文件下载回调] 区块namespaceId: {result['block'].namespaceId}")
        log.info(f"[文件下载回调] 区块大小: {len(result['data'])} 字节")
        log.info(f"[文件下载回调] 区块哈希: {result['block'].hash}")
        chunk_files.append(result['data'])
        log.info("-" * 40)

    def merge_files(chunks, output_path):
        """合并分块文件为完整文件"""
        with open(output_path, 'wb') as f:
            for chunk in chunks:
                f.write(chunk)
        log.info(f"文件已合并至: {output_path}")

    asset: asset_pb2.AssetMetadata = download_client.get(namespace_id=namespace_id, _hash=_hash,
                                                         block_callback=download_callback)
    merge_files(chunk_files, output_file)
    assert asset is not None
    log.info(f"download success. asset={MessageToJson(asset)}")
    assert "hello, world!" == codecs.open(output_file, "r").read()
