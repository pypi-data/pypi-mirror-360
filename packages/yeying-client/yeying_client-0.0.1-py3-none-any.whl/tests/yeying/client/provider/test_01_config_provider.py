# -*- coding:utf-8 -*-
from tests.yeying import option
from yeying.api.config import ConfigTypeEnum, config_pb2
from yeying.client.provider.config_provider import ConfigProvider
from yeying.client.utils import log_utils
import pytest


log = log_utils.get_logger(__name__)


@pytest.fixture
def before():
    log.info("ConfigProvider start test")
    config_provider = ConfigProvider(option=option)
    yield config_provider


def test_get(before):
    log.info("start get config")
    config_provider = before
    log.info(config_provider)
    res: config_pb2.GetConfigResponse = config_provider.get("chunk.size", ConfigTypeEnum.CONFIG_TYPE_SYSTEM)
    log.info(f"res={res}")
    log.info("success get config")


def test_set(before):
    log.info("start set config")
    config_provider = before
    log.info(config_provider)
    res: config_pb2.SetConfigResponse = config_provider.set("test", "123")
    log.info(f"res={res}")
    log.info("success set config")

