# -*- coding:utf-8 -*-
import os

from tests.yeying import option
from yeying.api.config import config_pb2
from yeying.api.asset import namespace_pb2, SearchNamespaceCondition
from yeying.client.provider.namespace_provider import NamespaceProvider
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("ConfigProvider start test")
    namespace_provider = NamespaceProvider(option=option)
    yield namespace_provider


def test_create(before):
    log.info("start create namespace")
    namespace_provider = before
    log.info(namespace_provider)
    res: namespace_pb2.CreateNamespaceResponse = namespace_provider.create(name="youxuehu", description="pytest namespace")
    log.info(f"res={res}")
    namespace_id = res.body.namespace.uid
    assert namespace_id is not None
    assert isinstance(namespace_id, str)
    os.environ["namespace_id"] = namespace_id
    log.info("success create namespace")


def test_set_default_namespace(before):
    log.info("start set default namespace")
    namespace_provider = before
    log.info(namespace_provider)
    namespace_id1 = os.environ.get("namespace_id")
    assert namespace_id1 is not None
    assert isinstance(namespace_id1, str)
    res: config_pb2.SetConfigResponse = namespace_provider.set_default_namespace(namespace_id=namespace_id1)
    log.info(f"res={res}")
    log.info("success set default namespace")



def test_get_default_namespace(before):
    log.info("start get default namespace")
    namespace_provider = before
    log.info(namespace_provider)
    namespace_id: str = namespace_provider.get_default_namespace()
    log.info(f"namespace_id={namespace_id}")
    assert namespace_id is not None
    log.info("success get default namespace")


def test_search(before):
    log.info("start search namespace")
    namespace_provider = before
    log.info(namespace_provider)
    res: namespace_pb2.SearchNamespaceResponse = namespace_provider.search(page=1, page_size=10, condition=SearchNamespaceCondition(name="youxuehu"))
    log.info(f"res={res}")
    assert len(res.body.namespaces) > 0
    log.info("success search namespace")


def test_detail(before):
    log.info("start detail namespace")
    namespace_provider = before
    log.info(namespace_provider)
    namespace_id1 = os.environ.get("namespace_id")
    assert namespace_id1 is not None
    assert isinstance(namespace_id1, str)
    res: namespace_pb2.NamespaceDetailResponse = namespace_provider.detail(uid=namespace_id1)
    log.info(f"res={res}")
    log.info("success detail namespace")


