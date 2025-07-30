# -*- coding:utf-8 -*-
import os


from tests.yeying import option
from yeying.api.asset import namespace_pb2, asset_pb2
from yeying.client.provider.asset_provider import AssetProvider
from yeying.client.provider.namespace_provider import NamespaceProvider
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("delete asset start test")
    log.info("delete namespace start test")
    asset_provider = AssetProvider(option=option)
    namespace_provider = NamespaceProvider(option=option)
    yield asset_provider, namespace_provider


def test_clean(before):
    asset_provider, namespace_provider = before
    log.info("start delete asset")
    log.info(asset_provider)
    namespace_id = os.environ.get("namespace_id")
    assert namespace_id is not None
    assert isinstance(namespace_id, str)
    log.info(f"namespace_id={namespace_id}")

    _hash = os.environ.get("hash")
    assert _hash is not None
    assert isinstance(_hash, str)
    log.info(f"_hash={_hash}")

    # 清理文件 -> 回收站
    res: asset_pb2.DeleteAssetResponse = asset_provider.delete(namespace_id=namespace_id, _hash=_hash)
    log.info(f"res={res}")
    log.info("success delete asset")


    log.info("start delete namespace")
    log.info(namespace_provider)
    namespace_id1 = os.environ.get("namespace_id")
    assert namespace_id1 is not None
    assert isinstance(namespace_id1, str)

    # 清理 namespace
    res: namespace_pb2.DeleteNamespaceResponse = namespace_provider.delete(uid=namespace_id1)
    log.info(f"res={res}")
    log.info("success delete namespace")