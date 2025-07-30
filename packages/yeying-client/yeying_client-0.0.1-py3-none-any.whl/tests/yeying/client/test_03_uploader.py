# -*- coding:utf-8 -*-
import os

from google.protobuf.json_format import MessageToJson

from tests import test_file_path
from tests.yeying import identity, option
from yeying.api.asset import asset_pb2
from yeying.client.model.file import File
from yeying.client.uploader import Uploader, UploadResult
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("Uploader start test")
    upload_client = Uploader(option, identity.securityConfig.algorithm)
    yield upload_client


def test_upload(before):
    log.info("start upload file")
    def upload_callback(result: UploadResult) -> None:
        log.info(f"[文件上传回调] 进度: {result['progress']['completed']}/{result['progress']['total']}")
        log.info(f"[文件上传回调] 区块namespaceId: {result['block'].namespaceId}")
        log.info(f"[文件上传回调] 区块大小: {result['block'].size} 字节")
        log.info(f"[文件上传回调] 区块哈希: {result['block'].hash}")
        log.info("-" * 40)

    upload_client = before
    file = File(name=os.path.basename(test_file_path), size=os.stat(test_file_path).st_size, stream=test_file_path,
                last_modified=int(os.stat(test_file_path).st_mtime * 1000))
    namespace_id1 = os.environ.get("namespace_id")
    assert namespace_id1 is not None
    assert isinstance(namespace_id1, str)
    res: asset_pb2.SignAssetResponse = upload_client.put(namespace_id=namespace_id1, file=file,
                                                         encrypted=True,
                                                         block_callback=upload_callback)
    asset = res.body.asset
    assert asset is not None
    log.info(f"upload success. asset={MessageToJson(asset)}")
    os.environ["hash"] = asset.hash
