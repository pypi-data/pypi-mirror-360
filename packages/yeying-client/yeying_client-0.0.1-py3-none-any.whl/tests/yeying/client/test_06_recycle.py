# -*- coding:utf-8 -*-
import os

from tests.yeying import option
from yeying.api.asset import recycle_pb2, asset_pb2
from yeying.api.common import message_pb2
from yeying.client.provider.recycle_provider import RecycleProvider
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("start test recycle")
    recycle_provider = RecycleProvider(option=option)
    yield recycle_provider


def test_search(before):
    recycle_provider = before
    log.info("start search recycle")
    log.info(recycle_provider)
    res: recycle_pb2.SearchDeletedAssetResponse = recycle_provider.search(page=1, page_size=10, condition=asset_pb2.SearchAssetCondition())
    log.info(f"res={res}")
    assert len(res.body.assets) > 0
    log.info("success search asset recycle")


def test_recover(before):
    recycle_provider = before
    log.info("start recover recycle")
    log.info(recycle_provider)

    namespace_id = os.environ.get("namespace_id")
    assert namespace_id is not None
    assert isinstance(namespace_id, str)
    log.info(f"namespace_id={namespace_id}")

    _hash = os.environ.get("hash")
    assert _hash is not None
    assert isinstance(_hash, str)
    log.info(f"_hash={_hash}")

    res: recycle_pb2.SearchDeletedAssetResponse = recycle_provider.search(page=1, page_size=10,
                                                                          condition=asset_pb2.SearchAssetCondition())
    log.info(f"res={res}")
    for asset in res.body.assets:
        curr_asset: asset_pb2.AssetMetadata = asset.asset
        namespace_id = curr_asset.namespaceId
        _hash = curr_asset.hash
        if namespace_id == curr_asset.namespaceId and _hash == curr_asset.namespaceId:
            res: recycle_pb2.RecoverDeletedAssetResponse = recycle_provider.recover(namespace_id=namespace_id, _hash=_hash)
            log.info(f"res={res}")
            assert res.body.status.code == message_pb2.ResponseStatus.code
            log.info("success recover asset recycle")


def test_remove(before):
    recycle_provider = before
    log.info("start remove recycle")
    log.info(recycle_provider)

    namespace_id = os.environ.get("namespace_id")
    assert namespace_id is not None
    assert isinstance(namespace_id, str)
    log.info(f"namespace_id={namespace_id}")

    _hash = os.environ.get("hash")
    assert _hash is not None
    assert isinstance(_hash, str)
    log.info(f"_hash={_hash}")

    res: recycle_pb2.SearchDeletedAssetResponse = recycle_provider.search(page=1, page_size=10,
                                                                          condition=asset_pb2.SearchAssetCondition())
    log.info(f"res={res}")
    for asset in res.body.assets:
        curr_asset: asset_pb2.AssetMetadata = asset.asset
        namespace_id = curr_asset.namespaceId
        _hash = curr_asset.hash
        if namespace_id == curr_asset.namespaceId and _hash == curr_asset.namespaceId:
            res: recycle_pb2.RemoveDeletedAssetResponse = recycle_provider.remove(namespace_id=namespace_id, _hash=_hash)
            log.info(f"res={res}")
            assert res.body.status.code == message_pb2.ResponseStatus.code
            log.info("success remove asset recycle")
