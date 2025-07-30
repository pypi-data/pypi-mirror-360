# -*- coding:utf-8 -*-
from google.protobuf.json_format import MessageToJson
from yeying.client.utils.date_utils import get_current_utc_string

from yeying.api.common import ResponseCodeEnum
from yeying.client.provider.base_provider import BaseProvider
from yeying.api.config import config_pb2_grpc, config_pb2
import grpc
from yeying.client.utils import log_utils

log = log_utils.get_logger(__name__)


"""
提供对资产的管理，包括查询、版本获取、详情查看、删除等操作
"""


class ConfigProvider(BaseProvider):

    def __init__(self, **kw):
        super(ConfigProvider, self).__init__(**kw)
        # 资产元信息
        self.config_client = config_pb2_grpc.ConfigStub(grpc.insecure_channel(self.option.proxy))

    def get(
        self, key: str, config_type: config_pb2.ConfigTypeEnum = config_pb2.ConfigTypeEnum.CONFIG_TYPE_USER
    ) -> config_pb2.GetConfigResponse:
        """
        kv 配置查询
        :param key: 键
        :param config_type: 配置类型 - 枚举 config_pb2.ConfigTypeEnum
        :return: config_pb2.GetConfigResponse
        """

        body = config_pb2.GetConfigRequestBody(key=key, type=config_type)
        header = self.authenticate.create_header(body=body)
        request = config_pb2.GetConfigRequest(header=header, body=body)
        response: config_pb2.GetConfigResponse = self.config_client.Get(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"get error, response={MessageToJson(response)}")
        return response

    def set(self, key: str, value: str) -> config_pb2.SetConfigResponse:
        """
        kv 配置添加
        :param key: key 配置信息
        :param value: value 配置信息
        :return: config_pb2.GetConfigResponse
        """
        config: config_pb2.ConfigMetadata = config_pb2.ConfigMetadata(
            key=key,
            value=value,
            owner=self.authenticate.get_did(),
            createdAt=get_current_utc_string(),
            updatedAt=get_current_utc_string(),
        )
        config.signature = self.authenticate.sign_data(config.SerializeToString())
        body = config_pb2.SetConfigRequestBody(config=config)
        header = self.authenticate.create_header(body=body)
        request = config_pb2.SetConfigRequest(header=header, body=body)
        response: config_pb2.SetConfigResponse = self.config_client.Set(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"set error, response={MessageToJson(response)}")
        return response
